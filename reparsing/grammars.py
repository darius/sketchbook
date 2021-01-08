"""
Tie things together, with a choice of different `parsing` implementations.
Concrete syntax for grammars.
"""

from parson import Grammar as ParsonGrammar
import parsers

def Grammar(grammar_str, make_parsing):
    return GrammarParser(dict(parser_parser(grammar_str)), make_parsing)

class GrammarParser(object):
    def __init__(self, rules, make_parsing):
        self.rules = rules
        self.make_parsing = make_parsing

    def parse(self, subject_str, rule=None):
        return self.parsing(subject_str).parse(rule)
    
    def parsing(self, subject_str):
        return self.make_parsing(self.rules, subject_str)

meta_grammar = r"""rule+ :end.

rule         :  name ('='             pe
                     |':'~whitespace [pe :Seclude])
                '.'                        :hug.

pe           :  term ('|' pe :Choice)?
             |                             :Empty.
term         :  factor (term :Chain)?.
factor       :  '!' factor                 :Nix
             |  primary ('**' primary :Star
                        |'++' primary :Plus
                        |'*' :Star
                        |'+' :Plus
                        |'?' :Maybe)?.
primary      :  '(' pe ')'
             |  '[' pe ']'                 :Seclude
             |  '{' pe '}'                 :Grab
             |  qstring                    :Literal
             |  regex
             |  "%any"                     :Any
             |  ':'~( name                 :Do
                    | qstring              :Push)
             |  name                       :Call.

name         :  /([A-Za-z_]\w*)/.

FNORD       ~:  whitespace?.
whitespace  ~:  /(?:\s|#.*)+/.

qstring     ~:  /'/  quoted_char* /'/ FNORD :join.
quoted_char ~:  /\\(.)/ | /([^'])/.        # TODO screen and interpret escapes

# Just a subset of regexes: ones matching with a statically-apparent length.
regex       ~:  '/' {regchunk}* '/' FNORD  :MatchN.
regchunk    ~:  escseq
             |  '[^' anyof* ']'
             |  '['  anyof* ']'
             |  /[^()\/[\]]/.    # XXX crude

anyof       ~:  atom ('-' atom)?.  
atom        ~:  escseq
             |  /[^\/\]]/.   # XXX crude

escseq      ~:  '\\' /./.   # XXX crude
"""
parser_parser = ParsonGrammar(meta_grammar).bind(parsers)

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
## outcome = parsing.parse()
## outcome.interpret(calc_semantics)
#. (13.5,)
## outcome.interpret(ast_semantics)
#. (('sub', ('mul', ('int', '2'), ('int', '8')), ('truediv', ('int', '5'), ('int', '2'))),)
## parsing.replace(1, 2, '0')
## parsing.subject
#. '208-5/2'
## parsing.parse().interpret(calc_semantics)
#. (205.5,)

## bool(calc.grammar.parse(s0))
#. True
## bool(calc.grammar.parse('xyz'))
#. False
