"""
Solve logic puzzles.
"""

from peglet import OneResult, Parser
import validity_smallerfirst as V

def Eqv(e1, e2):
    return V.Choice(e1, V.not_(e2), e2)

# XXX whitespace *with* a newline shouldn't be an AND -- too error-prone.
# Only with lhs and rhs on the same line should whitespace be AND.
# 
# XXX what's a good precedence/associativity for impl?
grammar = r"""
formula  = _ expr !.

expr     = sentence , _ expr  mk_and
         | sentence
sentence = sum /=/ _ sum      mk_eqv
         | sum
sum      = term \| _ sum      mk_or
         | term => _ term     mk_impl
         | term
term     = factor term        mk_and
         | factor
factor   = ~ _ primary        mk_not
         | primary
primary  = \( _ expr \) _
         | id _               mk_var

id       = ([A-Za-z_]\w*) _
_        = (?:\s|#[^\n]*)*
"""
parse = OneResult(Parser(grammar,
                         mk_eqv=Eqv, mk_impl=V.impl,
                         mk_and=V.and_, mk_or=V.or_, mk_not=V.not_,
                         mk_var=V.Variable))

def solve(puzzle_text):
    condition = parse(puzzle_text)
    if V.is_valid(condition):
        print("Valid.")
    else:
        show(V.satisfy(condition, 1))

def show(opt_env):
    if not opt_env:
        print("Unsatisfiable.")
    else:
        for k, v in sorted(opt_env.items()):
            if k is not None:
                print("%s%s" % ("" if v else "~", k))

## solve(' hey (there | ~there), ~hey | ~there')
#. hey
#. ~there
## solve(' hey (there, ~there)')
#. Unsatisfiable.
## solve('a=>b = ~b=>~a')
#. Valid.


if __name__ == '__main__':
    import sys
    solve(sys.stdin.read())
