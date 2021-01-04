"""
A template language, similar to templite by Ned Batchelder.
https://github.com/aosabook/500lines/tree/master/template-engine
(Still missing a few features.)
Ported from Parson.
"""

import toplevel
from nonincremental import Parsing
from semantics import ast_semantics

grammar_source = r"""
start:     block.
block:     chunk* :Block.
chunk:     '{#' (!'#}' %any)* '#}'
        |  '{{'_ expr '}}'                                                  :Expr
        |  '{%'_ 'if'_ expr '%}'                block '{%'_ 'endif'_  '%}'  :If
        |  '{%'_ 'for'_ ident _ 'in'_ expr '%}' block '{%'_ 'endfor'_ '%}'  :For
        |  {(!/{[#{%]/ %any)+}                                              :Literal.

expr:      access ('|' function :Call)* _ .
access:    ident :VarRef ('.' ident :Access)*.
function:  ident.

ident:     {/[A-Za-z_]/ /[A-Za-z_0-9]/*}.

_:         /\s/*.
"""

grammar = toplevel.Grammar(grammar_source, Parsing)

def parse(text, rule=None):
    p = grammar.parse(text, rule)
    if p:
        for x in p.interpret(ast_semantics)[0]:
            print x

## parse('')
#. Block

## parse('a')
#. Block
#. ('Literal', 'a')

## parse('hello {{world}} yay')
#. Block
#. ('Literal', 'hello ')
#. ('Expr', ('VarRef', 'world'))
#. ('Literal', ' yay')

## with open('/home/darius/g/aima-python/README.md') as f: big = f.read()
## len(big)
#. 19377
## bool(grammar.parse(big))
#. True

## parse('{% if foo.bar %} {% for x in xs|ok %} {{x}} {% endfor %} yay {% endif %}')
#. Block
#. ('If', ('Access', ('VarRef', 'foo'), 'bar'), ('Block', ('Literal', ' '), ('For', 'x', ('Call', ('VarRef', 'xs'), 'ok'), ('Block', ('Literal', ' '), ('Expr', ('VarRef', 'x')), ('Literal', ' '))), ('Literal', ' yay ')))

## parse('hello {%for x in xs%} whee{{x}} {% endfor %} yay')
#. Block
#. ('Literal', 'hello ')
#. ('For', 'x', ('VarRef', 'xs'), ('Block', ('Literal', ' whee'), ('Expr', ('VarRef', 'x')), ('Literal', ' ')))
#. ('Literal', ' yay')

## parse(' {%if x%} whee{{x}} {% endif %} yay {%if y%} ok{{y}} {% endif %}')
#. Block
#. ('Literal', ' ')
#. ('If', ('VarRef', 'x'), ('Block', ('Literal', ' whee'), ('Expr', ('VarRef', 'x')), ('Literal', ' ')))
#. ('Literal', ' yay ')
#. ('If', ('VarRef', 'y'), ('Block', ('Literal', ' ok'), ('Expr', ('VarRef', 'y')), ('Literal', ' ')))
