"""
The obligatory calculator example
"""

import toplevel
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
digit =  /\d/.
"""
calc_semantics = ComboSemantics(base_semantics, ModuleSemantics(operator))

def Calc(make_parsing):
    def calc(s):
        return calc.grammar.parse(s).interpret(calc_semantics)[0]
    calc.grammar = toplevel.Grammar(calc_source, make_parsing)
    return calc
