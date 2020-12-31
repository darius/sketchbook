"""
Tweak nonincremental.py to incremental reparsing.
"""

from parse_outcome import ParseOutcome

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
        # Delete all the preceding chart entries that looked at subject[lo:hi]:
        for i in xrange(lo):
            if lo < i + self.far_bounds[i]:
                new_bounds = 0
                memos = self.chart[i]
                for rule, (di, far, ops) in memos.items():
                    if lo < i + far: del memos[rule]
                    else:            new_bounds = max(new_bounds, far)
                self.far_bounds[i] = new_bounds
        # And replace the directly affected columns:
        self.chart[lo:hi] = [{} for _ in xrange(len(replacement))]
        self.far_bounds[lo:hi] = [0] * len(replacement)

    def parse(self, rule=None):
        if rule is None: rule = 'start'
        return ParseOutcome(self, rule, self.call(0, rule))

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
## from eg_calc import Calc, calc_semantics
## from semantics import ast_semantics

## calc = Calc(Parsing)

## parsing = calc.grammar.parsing('-2')
## parsing.parse().interpret(ast_semantics)
#. (('neg', ('int', '2')),)

## parsing.replace(0, 0, '3')
## parsing.subject
#. '3-2'
## parsing.parse().interpret(ast_semantics)
#. (('sub', ('int', '3'), ('int', '2')),)
## parsing.parse().memo[2]
#. (('[',), ('[',), ('[',), ('[',), ('lit', '3'), ('do', 'int'), (']',), (']',), (']',), ('[',), ('[',), ('[',), ('lit', '2'), ('do', 'int'), (']',), (']',), (']',), ('do', 'sub'), (']',))



## calc('-3*4')
#. -12


## parsing = calc.grammar.parsing('3-2')
## parsing.subject
#. '3-2'
## parsing.parse().interpret(ast_semantics)
#. (('sub', ('int', '3'), ('int', '2')),)

## parsing.replace(1, 1, '/3')
## parsing.subject
#. '3/3-2'
## parsing.parse().interpret(ast_semantics)
#. (('sub', ('truediv', ('int', '3'), ('int', '3')), ('int', '2')),)



## parsing = calc.grammar.parsing('')
## parsing.subject
#. ''
## parsing.parse()
#. start<None,1,()>

## parsing.replace(0, 0, '5')
## parsing.subject
#. '5'
## parsing.parse().interpret(ast_semantics)
#. (('int', '5'),)

## parsing.replace(0, 0, '3')
## parsing.subject
#. '35'
## parsing.parse().interpret(ast_semantics)
#. (('int', '35'),)

## parsing.replace(1, 2, '')
## parsing.subject
#. '3'
## parsing.parse().interpret(ast_semantics)
#. (('int', '3'),)

## parsing.replace(1, 1, '-2')
## parsing.subject
#. '3-2'
## parsing.parse().interpret(ast_semantics)
#. (('sub', ('int', '3'), ('int', '2')),)

## parsing.replace(1, 1, '/3')  # XXX trouble!
## parsing.subject
#. '3/3-2'
## parsing.parse().interpret(ast_semantics)
#. (('sub', ('truediv', ('int', '3'), ('int', '3')), ('int', '2')),)

## parsing.replace(2, 3, '5*4')
## parsing.subject
#. '3/5*4-2'
## parsing.parse().interpret(ast_semantics)
#. (('sub', ('mul', ('truediv', ('int', '3'), ('int', '5')), ('int', '4')), ('int', '2')),)

## parsing.replace(0, 3, '6/3')
## parsing.subject
#. '6/3*4-2'
## parsing.parse().interpret(ast_semantics)
#. (('sub', ('mul', ('truediv', ('int', '6'), ('int', '3')), ('int', '4')), ('int', '2')),)



## s0 = '2*8-5/2'


## parsing = calc.grammar.parsing(s0)
## parsing.subject
#. '2*8-5/2'
## outcome = parsing.parse()
## outcome.interpret(calc_semantics)
#. (13.5,)
## outcome.interpret(ast_semantics)
#. (('sub', ('mul', ('int', '2'), ('int', '8')), ('truediv', ('int', '5'), ('int', '2'))),)

## parsing.replace(1, 1, '/2')
## parsing.subject
#. '2/2*8-5/2'
## parsing.parse().interpret(ast_semantics)
#. (('sub', ('mul', ('truediv', ('int', '2'), ('int', '2')), ('int', '8')), ('truediv', ('int', '5'), ('int', '2'))),)

## parsing.subject[4:4+1]
#. '8'


## parsing = calc.grammar.parsing(s0)
## parsing.replace(1, 2, '/2*')
## parsing.subject
#. '2/2*8-5/2'
## parsing.parse().interpret(ast_semantics)
#. (('sub', ('mul', ('truediv', ('int', '2'), ('int', '2')), ('int', '8')), ('truediv', ('int', '5'), ('int', '2'))),)


## parsing = calc.grammar.parsing(s0)
## parsing.replace(1, 2, '')
## parsing.text(0, len(parsing.subject))
#. '28-5/2'
## parsing.parse().interpret(calc_semantics)
#. (25.5,)
