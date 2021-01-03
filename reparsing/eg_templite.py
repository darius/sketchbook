import toplevel
from nonincremental import Parsing
from semantics import ast_semantics

grammar_source = r"""
start:     block.
block:     chunk* :hug :Block.

chunk:     '{#' (!'#}' /./)* '#}'
        |  '{{'_ expr '}}'                                                  :Expr
        |  '{%'_ 'if'_ expr '%}'                block '{%'_ 'endif'_  '%}'  :If
        |  '{%'_ 'for'_ ident _ 'in'_ expr '%}' block '{%'_ 'endfor'_ '%}'  :For
        |  (!/{[#{%]/ {/./})+ :join                                         :Literal.

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
        return p.interpret(ast_semantics)

## parse('')
#. (('Block', ('hug',)),)

## parse('a')
#. (('Block', ('hug', ('Literal', ('join', 'a')))),)

## parse('hello {{world}} yay')
#. (('Block', ('hug', ('Literal', ('join', 'h', 'e', 'l', 'l', 'o', ' ')), ('Expr', ('VarRef', 'world')), ('Literal', ('join', ' ', 'y', 'a', 'y')))),)

## parse('world', 'block')
#. (('Block', ('hug', ('Literal', ('join', 'w', 'o', 'r', 'l', 'd')))),)
