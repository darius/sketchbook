from monoidal import delay, match, parse, recur, nil

def make_char_class(c_lo, c_hi):
    return '%s-%s' % (c_lo, c_hi[0]) if c_hi else c_lo

make_grammar = lambda rules: '\n'.join(rules)
rule_def     = lambda name, peg: '%s ::= %s.' % (name, peg)
fold_alt     = lambda term, terms: ' / '.join([term] + terms)
identity     = lambda x: x
epsilon      = lambda: '<epsilon>'
fold_seq     = lambda factors, action: (' '.join(factors)
                                        + ('\t:' + action[0] if action else ''))
not_         = lambda p: '!(%s)' % p
postfixed    = lambda peg, suffix: '(%s)%s' % (peg, suffix) if suffix else peg
oneof        = lambda ccs: '{%s}' % ''.join(ccs)
literal      = lambda cs: repr(''.join(cs))
rule_ref     = lambda name: '<%s>' % name
eof          = lambda: '$'
escaped_char = lambda c: '\\' + c
make_name    = lambda letter, letters: letter + ''.join(letters)
skip         = lambda: None

dot            = match('(.)')

_              = match(r'\s*')  # TODO add comments
name           = match(r'([A-Za-z_]\w*)\b\s*')

quoted_char    = (r'\\' + dot
               | match(r"([^'\\])"))

lit_char_class = (r'\\' + dot
               | match(r"([^\]\\])"))

char_class     = lit_char_class + ('-' + lit_char_class).maybe()  >> make_char_class

peg            = delay(lambda: 
                 term + ('[|]' +_+ term).star()          >> fold_alt)

primary        = ('[(]' +_+ peg + '[)]' + _
               | r'\[' + char_class.star() + r'\]' + _   >> oneof
               | "'" + quoted_char.star() + "'" + _      >> literal
               | name                                    >> rule_ref
               | r'\$' + _                               >> eof)

factor         = delay(lambda:
                 '!' +_+ factor                          >> not_
               | primary + r'([*+?]?)' + _               >> postfixed)

term           = factor.plus() + (':' +_+ name).maybe()  >> fold_seq

rule           = name + '=' +_+ peg + r'\.' + _          >> rule_def
grammar        = _ + rule.plus() + '$'                   >> make_grammar


meta_grammar = r"""
grammar         = _ rule+ $                      :make_grammar.
rule            = name '='_ peg '.'_             :rule_def.

peg             = term ('|'_ term)*              :fold_alt.
term            = factor+ (':'_ name)?           :fold_seq.
factor          = '!'_ factor                    :not_
                | primary [*+?]?_                :postfixed.
primary         = '('_ peg ')'_
                | '[' char_class* ']'_           :oneof
                | '\'' quoted_char* '\''_        :literal
                | name                           :rule_ref
                | '$'_                           :eof.

char_class      = lit_char_class ('-' lit_char_class)? :make_char_class.

lit_char_class  = '\\' char                      :escaped_char
                | !']' char.

quoted_char     = '\\' char                      :escaped_char
                | !'\'' char.

name            = alpha alphanum* !alphanum _    :make_name.
alpha           = [A-Za-z_].
alphanum        = [A-Za-z_0-9].

_               = (white_char | comment)*.
white_char      = [ \t\r\n\f].
comment         = '#' (!'\n' char)* '\n'.
"""

## print parse(grammar, meta_grammar)
#. grammar ::= <_> (<rule>)+ $	:make_grammar.
#. rule ::= <name> '=' <_> <peg> '.' <_>	:rule_def.
#. peg ::= <term> ('|' <_> <term>)*	:fold_alt.
#. term ::= (<factor>)+ (':' <_> <name>)?	:fold_seq.
#. factor ::= '!' <_> <factor>	:not_ / <primary> ({*+?})? <_>	:postfixed.
#. primary ::= '(' <_> <peg> ')' <_> / '[' (<char_class>)* ']' <_>	:oneof / "'" (<quoted_char>)* "'" <_>	:literal / <name>	:rule_ref / '$' <_>	:eof.
#. char_class ::= <lit_char_class> ('-' <lit_char_class>)?	:make_char_class.
#. lit_char_class ::= '\\' <char>	:escaped_char / !(']') <char>.
#. quoted_char ::= '\\' <char>	:escaped_char / !("'") <char>.
#. name ::= <alpha> (<alphanum>)* !(<alphanum>) <_>	:make_name.
#. alpha ::= {A-Za-z_}.
#. alphanum ::= {A-Za-z_0-9}.
#. _ ::= (<white_char> / <comment>)*.
#. white_char ::= { trnf}.
#. comment ::= '#' (!('n') <char>)* 'n'.
#. 
