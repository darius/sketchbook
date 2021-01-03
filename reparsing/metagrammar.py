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
             |  regex
             |  "%any"                     :Any
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

# XXX probably not the same :Range though
anyof       ~:  atom ('-' atom)?.  
atom        ~:  escseq
             |  /[^*+?$()\/[\]]/.   # XXX crude, blacklist of special chars

escseq      ~:  '\\' /./.   # XXX crude
"""
parser_parser = Grammar(meta_grammar).bind(parsers)
