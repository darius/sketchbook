"""
Tie things together, with a choice of different `parsing` implementations.
"""

from metagrammar import parser_peg

class Grammar(object):
    def __init__(self, grammar_str, make_parsing):
        self.rules = dict(parser_peg(grammar_str))
        self.make_parsing = make_parsing

    def parse(self, subject_str, rule=None):
        return self.parsing(subject_str).parse_outcome(rule)
    
    def parsing(self, subject_str):
        return self.make_parsing(self.rules, subject_str)
    

# Example

## from eg_calc import Calc, calc_semantics
## from semantics import ast_semantics
## import nonincremental, incremental

## calc = Calc(nonincremental.Parsing)
## calc = Calc(incremental.Parsing)

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
