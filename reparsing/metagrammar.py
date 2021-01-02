"""
Concrete syntax for grammars in this new system.
"""

from parson import Grammar
import parsers

meta_grammar = r""" rule+ :end.

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
             |  qstring ('..' qstring :Range    # TODO replace this with /[x-y]/ or something
                        |             :Literal)
             |  ':'~name                   :Do
             |  name                       :Call.

name         :  /([A-Za-z_]\w*)/.

FNORD       ~:  whitespace?.
whitespace  ~:  /(?:\s|#.*)+/.

qstring     ~:  /'/  quoted_char* /'/ FNORD :join.
quoted_char ~:  /\\(.)/ | /([^'])/.        # TODO screen and interpret escapes
"""
parser_parser = Grammar(meta_grammar).bind(parsers)
