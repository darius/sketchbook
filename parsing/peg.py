from re import escape
from monoidal import alt, as_peg, delay, epsilon, match, parse

nonterminals = {}

suffixes = {'*': lambda p: p.star(),
            '+': lambda p: p.plus(),
            '?': lambda p: p.maybe(),
            '':  lambda p: p}

def make_char_class(c_lo, c_hi): return '-'.join([c_lo] + c_hi)

def fold_seq(factors, action):
    seq = sum(factors, epsilon(()))
    return seq >> eval(action[0]) if action else seq

def fold_alt(term, terms):
    terms = [term] + terms
    return reduce(alt, terms)    # XXX I'd rather associate the other way

def postfixed(peg, suffix, minus):
    peg = suffixes[suffix](peg)
    return peg.drop() if minus else peg

def meta_postfixed(peg, suffix, minus):
    return postfixed(peg, ''.join(suffix), ''.join(minus))


make_grammar = lambda rules: rules
rule_def     = lambda name, peg: (name, peg)
not_         = lambda p: '!(%s)' % p
oneof        = lambda ccs: match('([%s])' % ''.join(ccs))
literal      = lambda cs: match(''.join(cs))
rule_ref     = lambda name: as_peg(lambda s: nonterminals[name](s))
eof          = lambda: match('$')
escaped_char = lambda c: '\\' + c
literal_char = escape
make_name    = lambda letter, letters: letter + ''.join(letters)

dot            = match('(.)')

_              = match(r'\s*')  # TODO add comments
name           = match(r'([A-Za-z_]\w*)\b\s*')

quoted_char    = (r'\\' + dot                            >> escaped_char
               | match(r"([^'\\])")                      >> literal_char)

bracketed_char = (r'\\' + dot                            >> escaped_char
               | match(r"([^\]\\])")                     >> literal_char)

char_class     = bracketed_char + ('-' + bracketed_char).maybe()  >> make_char_class

peg            = delay(lambda: 
                 term + ('[|]' +_+ term).star()          >> fold_alt)

primary        = ('[(]' +_+ peg + '[)]' + _
               | "'" + quoted_char.star() + "'" + _      >> literal
               | r'\[' + char_class.star() + r'\]' + _   >> oneof
               | name                                    >> rule_ref
               | r'\$' + _                               >> eof)

factor         = delay(lambda:
                 '!' +_+ factor                          >> not_
               | primary + r'([*+?]?)' +_+ r'([-]?)' + _ >> postfixed)

term           = factor.plus() + (':' +_+ name).maybe()  >> fold_seq

rule           = name + '=' +_+ peg + r'\.' + _          >> rule_def
grammar        = _ + rule.plus() + '$'                   >> make_grammar


meta_grammar = r"""
grammar         = _ rule+ $                      :make_grammar.
rule            = name '='_ peg '.'_             :rule_def.

peg             = term ('|'_ term)*              :fold_alt.
term            = factor+ (':'_ name)?           :fold_seq.
factor          = '!'_ factor                    :not_
                | primary [*+?]?_ [-]?_          :meta_postfixed.
primary         = '('_ peg ')'_
                | '\'' quoted_char* '\''_        :literal
                | '[' char_class* ']'_           :oneof
                | name                           :rule_ref
                | '$'_                           :eof.

char_class      = bracketed_char ('-' bracketed_char)? :make_char_class.

bracketed_char  = '\\' char                      :escaped_char
                | !']' char                      :literal_char.

quoted_char     = '\\' char                      :escaped_char
                | !'\'' char                     :literal_char.

name            = alpha alphanum* _              :make_name.
alpha           = [A-Za-z_].
alphanum        = [A-Za-z_0-9].

_               = (white_char | comment)* -.
white_char      = [ \t\r\n\f] -.
comment         = '#' (!'\n' char)* '\n'.
"""

## nonterminals = dict(parse(grammar, meta_grammar))

## nonterminals['_']('hello')
#. [((), 'hello')]

## parse(nonterminals['alphanum'].star(), 'hello')
#. ['h', 'e', 'l', 'l', 'o']

## n_alphanum = nonterminals['alphanum']
## (n_alphanum + n_alphanum.star() + ~n_alphanum + _ >> make_name)('hello')
#. [(('hello',), '')]

## parse(nonterminals['name'], 'hello')
#. 'hello'

## parse(nonterminals['peg'], 'hello') is not None
#. True

# XXX
## parse(nonterminals['grammar'], meta_grammar)


# for x in parse(grammar, meta_grammar): print x
