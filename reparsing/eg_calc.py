"""
The obligatory calculator example
"""

from semantics import base_semantics, ModuleSemantics, ComboSemantics
import operator

calc_source = r"""
start =  exp0.
exp0  :  exp1 ( '+'  exp1 :add
              | '-'  exp1 :sub )*.
exp1  :  exp2 ( '*'  exp2 :mul
              | '//' exp2 :div
              | '/'  exp2 :truediv
              | '%'  exp2 :mod )*.
exp2  :  exp3 ( '^'  exp2 :pow )?.
exp3  :  '(' exp0 ')'
      |  '-' exp1 :neg
      |  {digit+} :int.
digit =  '0'..'9'.
"""
calc_semantics = ComboSemantics(base_semantics, ModuleSemantics(operator))

def Calc(make_grammar):
    def calc(s):
        parser = calc.grammar.parsing(s)
        return parser.interpret(parser.parse(), calc_semantics)[0]
    calc.grammar = make_grammar(calc_source)
    return calc
