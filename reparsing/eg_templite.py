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
block:     chunk* :hug :Block.

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
        return p.interpret(ast_semantics)

## parse('')
#. (('Block', ('hug',)),)

## parse('\n', rule='chunk')
#. (('Literal', '\n'),)

## parse('a')
#. (('Block', ('hug', ('Literal', 'a'))),)

## parse('hello {{world}} yay')
#. (('Block', ('hug', ('Literal', 'hello '), ('Expr', ('VarRef', 'world')), ('Literal', ' yay'))),)

## parse('world', 'block')
#. (('Block', ('hug', ('Literal', 'world'))),)

## with open('/home/darius/g/aima-python/README.md') as f: big = f.read()
## len(big)
#. 19377
## grammar.parse(big).prefix()
#. 19377
