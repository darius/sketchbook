"""
Tweak nonincremental.py to incremental reparsing.
"""

from metagrammar import parser_peg

# Top level

class Grammar(object):
    def __init__(self, grammar_str):
        self.rules = dict(parser_peg(grammar_str))
    def parsing(self, subject_str):
        return Parsing(self.rules, subject_str)
    
class Parsing(object):
    def __init__(self, rules, subject_str):
        self.rules = rules
        self.subject = subject_str
        # Memo tables for each position in subject:
        self.chart = [{} for _ in xrange(len(subject_str)+1)]
        # Max of 'far' value from each memo table:
        self.far_bounds = [0] * (len(subject_str)+1)

    def text(self, lo, hi):
        return self.subject[lo:hi]

    def replace(self, lo, hi, replacement):
        assert lo <= hi <= len(self.subject)
        # TODO notice if the replacement leaves some of it unchanged
        self.subject = self.subject[:lo] + replacement + self.subject[hi:]
        self.chart[lo:hi] = [{} for _ in xrange(len(replacement))]
        self.far_bounds[lo:hi] = [0] * len(replacement)
        # Invalidate all the chart entries that looked at subject[lo:hi]:
        for i in xrange(lo):
            if lo < i + self.far_bounds[i]:
                new_bounds = 0
                memos = self.chart[i]
                for rule, (di, far, ops) in memos.items():
                    if lo < i + far: del memos[rule]
                    else:            new_bounds = max(new_bounds, far)
                self.far_bounds[i] = new_bounds

    def parse(self, rule='start'):
        di, far, ops = self.call(0, rule)
        if di is None:
            raise Exception("Unparsable", far, self.subject)
        if di != len(self.subject):
            raise Exception("Incomplete parse", far, self.subject)
        return ops

    def interpret(self, ops, semantics):
        stack = []
        frame = []
        for insn in ops:
            op = insn[0]
            if op == '[':
                stack.append(frame)
                frame = []
            elif op == ']':
                parent = stack.pop()
                parent.extend(frame)
                frame = parent
            elif op == 'do':
                fn = semantics[insn[1]]
                frame[:] = [fn(*frame)]
            elif op == 'grab':
                i, di = insn[1:]
                frame.append(self.subject[i:i+di])
            else:
                assert 0
        assert not stack
        return tuple(frame)

    # Used by parsers, not by clients:
    def call(self, i, rule):
        column = self.chart[i]
        memo = column.get(rule)
        if memo is None:
            column[rule] = cyclic
            column[rule] = memo = self.rules[rule](self, i)
            self.far_bounds[i] = max(self.far_bounds[i], memo[1])
        elif memo is cyclic:
            raise Exception("Left-recursive rule", rule)
        return memo

cyclic = object()


# Example

## from semantics import ast_semantics
## from eg_calc import Calc, calc_semantics
## calc = Calc(Grammar)

## calc('(2-3)*4')
#. -4

## s0 = '2*8-5/2'
## calc(s0)
#. 13.5

## parsing = calc.grammar.parsing(s0)
## parse = parsing.parse()
## parsing.interpret(parse, calc_semantics)
#. (13.5,)
## parsing = calc.grammar.parsing(s0)
## parsing.interpret(parse, ast_semantics)
#. (('sub', ('mul', ('int', '2'), ('int', '8')), ('truediv', ('int', '5'), ('int', '2'))),)
## parsing.replace(1, 2, '/2*')
## parsing.text(0, len(parsing.subject))
#. '2/2*8-5/2'
## parsing.interpret(parsing.parse(), calc_semantics)
#. (5.5,)
