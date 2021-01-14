"""
Puny BASIC, ported from Parson
"""

import grammars
from semantics import ast_semantics

grammar_source = r"""
start     :  (_ line %eol)*.
line      :  numeral stmt                  :numbered
          |  command.

command   :  "run"_                        :run
          |  "new"_                        :new
          |  "load"_   {/\S/+}             :load
          |  "save"_   {/\S/+}             :save
          |  stmt                          :immediate.

stmt      :  "print"_  printing            :print
          |  '?'_      printing            :print
          |  "input"_  id                  :input
          |  "goto"_   exp                 :goto
          |  "if"_     relexp "then"_ exp  :if
          |  "gosub"_  exp                 :gosub
          |  "return"_                     :return
          |  "end"_                        :end
          |  "list"_                       :list
          |  "rem"_    /./*
          |  ("let"_)? id '='_ exp         :let.

printing  :  (display writes)?.
writes    :  ';'_        printing
          |  ','_ :space printing
          |       :newline.

display   :  exp :write
          |  '"' {qchar}* :quote '"'_.
qchar     :  '"' '"'  # Two consecutive double-quotes mean '"'.
          |  /[^"]/.  # Any other character just means itself.

relexp    :  exp  (  '<>'_ exp :ne
                   | '<='_ exp :le
                   | '<'_  exp :lt
                   | '='_  exp :eq
                   | '>='_ exp :ge
                   | '>'_  exp :gt
                  )?.
exp       :  exp1 (  '+'_ exp1 :add
                   | '-'_ exp1 :sub
                  )*.
exp1      :  exp2 (  '*'_ exp2 :mul
                   | '/'_ exp2 :idiv
                  )*.
exp2      :  primary ('^'_ exp2 :pow)?.

primary   :  '-'_ exp1 :neg
          |  id        :fetch
          |  numeral      
          |  '('_ exp ')'_.

id        :  {/[a-z]/} _.  # TODO: longer names, screening out reserved words

numeral   :  {/\d/+} _ :int.

_         :  /\s/*.
"""

def Basic(make_parsing):
    def basic(s, rule=None):
        return basic.grammar.parse(s, rule).interpret(ast_semantics)[0]
    basic.grammar = grammars.Grammar(grammar_source, make_parsing)
    return basic

## from nonincremental import Parsing
## parse = Basic(Parsing)

## parse("a=1", rule='command')
#. ('immediate', ('let', 'a', ('int', '1')))

## parse("10 a=1", rule='line')
#. ('numbered', ('int', '10'), ('let', 'a', ('int', '1')))

## parse("run")
#. ('run',)
