"""
Baseline, not yet incremental.
"""

from parse_outcome import ParseOutcome

class Parsing(object):
    def __init__(self, rules, subject_str):
        self.rules = rules
        self.subject = subject_str
        self.chart = [{} for _ in xrange(len(subject_str)+1)]

    def text(self, lo, hi):
        return self.subject[lo:hi]

    def replace(self, lo, hi, replacement):
        assert lo <= hi <= len(self.subject)
        self.subject = self.subject[:lo] + replacement + self.subject[hi:]
        self.chart = [{} for _ in xrange(len(self.subject)+1)]

    def parse_outcome(self, rule=None): # TODO naming
        if rule is None: rule = 'start'
        return ParseOutcome(self, rule, self.call(0, rule))

    # Used by parsers, not by clients:
    def call(self, i, rule):
        column = self.chart[i]
        memo = column.get(rule)
        if memo is None:
            column[rule] = cyclic
            column[rule] = memo = self.rules[rule](self, i)
        elif memo is cyclic:
            raise Exception("Left-recursive rule", rule)
        return memo

cyclic = object()


# Example

## from eg_calc import Calc, calc_semantics
## from semantics import ast_semantics

## calc = Calc(Parsing)

## calc('(2-3)*4')
#. -4

## s0 = '2*8-5/2'
## calc(s0)
#. 13.5

## parsing = calc.grammar.parsing(s0)
## outcome = parsing.parse_outcome()
## outcome.interpret(calc_semantics)
#. (13.5,)
## outcome.interpret(ast_semantics)
#. (('sub', ('mul', ('int', '2'), ('int', '8')), ('truediv', ('int', '5'), ('int', '2'))),)
## parsing.replace(1, 2, '0')
## parsing.text(0, len(parsing.subject))
#. '208-5/2'
## parsing.parse_outcome().interpret(calc_semantics)
#. (205.5,)
