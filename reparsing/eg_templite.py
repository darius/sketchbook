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
start:     block.      # XXX why is _ needed?
block:     chunk* :hug :Block.

chunk:     '{#' (!'#}' /./)* '#}'
        |  '{{'_ expr '}}'                                                  :Expr
        |  '{%'_ 'if'_ expr '%}'                block '{%'_ 'endif'_  '%}'  :If
        |  '{%'_ 'for'_ ident _ 'in'_ expr '%}' block '{%'_ 'endfor'_ '%}'  :For
        |  literal.

literal:   {(!/{[#{%]/ /./)+}                                               :Literal.

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

# XXX can't use /./ for a newline
## parse('\n', rule='chunk')

## parse('a')
#. (('Block', ('hug', ('Literal', 'a'))),)

## parse('hello {{world}} yay')
#. (('Block', ('hug', ('Literal', 'hello '), ('Expr', ('VarRef', 'world')), ('Literal', ' yay'))),)

## parse('world', 'block')
#. (('Block', ('hug', ('Literal', 'world'))),)

with open('/home/darius/g/aima-python/README.md') as f:
    big = f.read()
## len(big)
#. 19377
## wtf = big[:1]
## wtf
#. '\n'
## grammar.parse(big).prefix()
#. 0
## big[:231]
#. '\n\n# `aima-python` [![Build Status](https://travis-ci.org/aimacode/aima-python.svg?branch=master)](https://travis-ci.org/aimacode/aima-python) [![Binder](http://mybinder.org/badge.svg)](http://mybinder.org/repo/aimacode/aima-python)'
