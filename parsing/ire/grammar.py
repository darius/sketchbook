"""
Parsing expressions, with an API meant to resemble Python's re module.
TODO evolve the grammar over to my actual new plans
"""

from parson import Grammar as ParsonGrammar
import parsers

meta_grammar = r"""
top          :  '' :None pe :hug rule* :end.

rule         :  '-' name ('='             pe
                         |':'~whitespace [pe :Seclude])
                :hug.

pe           :  term ('|' pe :Choice)?
             |                             :Empty.
term         :  factor (term :Chain)?.
factor       :  '!' factor                 :Nix
             |  primary ('**' primary :Star
                        |'++' primary :Plus
                        |'*' :Star
                        |'+' :Plus
                        |'?' :Maybe
                        |'^' :Grab)*.  # N.B. this * was a ? before we added '^'
primary      :  '(' pe ')'
             |  '[' pe ']'                 :Seclude
             |  '{' extern '}'             
             |  qstring                    :Literal
             |  dqstring                   :Keyword
             |  regex                      :Regex
             |  '.'~name                   :BuiltIn
             |  ':'~( name                 :Do
                    | sqstring             :Push)
             |  name                       :Call.

extern       :  name                       :Extern.

name         :  /([A-Za-z_]\w*)/.

dqstring    ~:  '"'  dquoted_char* '"' FNORD :join.
qstring     ~:                                          #  sqstring | 
                '\\' slashed_char* '/' FNORD :join.
sqstring    ~:  /'/   quoted_char* /'/ FNORD :join.
regex       ~:  '`'    regex_char* '`' FNORD :join.

dquoted_char~:  /\\(.)/ | /([^"])/.        # TODO screen and interpret escapes
quoted_char ~:  /\\(.)/ | /([^'])/.
slashed_char~:  /\\(.)/ | /([^\/])/.       # TODO something different for backslash?
regex_char  ~:  /(\\.)/ | /([^`])/.

FNORD       ~:  whitespace?.
whitespace  ~:  /(?:\s|#.*)+/.
"""
parser_parser = ParsonGrammar(meta_grammar).bind(parsers)
