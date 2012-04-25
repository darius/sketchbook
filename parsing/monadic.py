"""
Monadic parser combinators plus a textual DSL expanding into them, plus
an example 'real' PEG grammar.
Glossary:
  p, q: parser (function from s to list [(val, s)] of length 0 or 1)
  s: string (the unparsed remainder of the input)
  val: a value produced by parsing
  res: a result: a pair (val, s)
  f: function from val to p
"""

import re

def parse(p, s):
    "Return the value from p parsing (a prefix of) s, or None on failure."
    for value, rest in p(s): return value


# Constructors for PEG parsers.
# TODO: error localization, stream input, memoizing

# 'give' and 'take' are the monad operators usually named 'return' and 'bind'.
# E.g.: take(give('hello'), lambda val: ...) binds val to 'hello'
def give(val):  return lambda s: [(val, s)]
def take(p, f): return lambda s: [res for val, s1 in p(s) for res in f(val)(s1)]

def drop(p, q): return take(p, lambda _: q)
def cons(p, q): return take(p, lambda vp: take(q, lambda vq: give([vp]+vq)))

def match(regex):  return lambda s: [(m.group(0), s[m.end():])
                                     for m in [re.match(regex, s)] if m]

def alt(p, *qs):   return lambda s: p(s) or (alt(*qs)(s) if qs else [])
def complement(p): return lambda s: [] if p(s) else [(None, s)]

def star(p):       return alt(cons(p, lambda s: star(p)(s)),
                              give([]))

def opt(p):        return alt(p, give(None))
def plus(p):       return cons(p, star(p))

## drop(match(r'he'), match(r'.'))('hello')
#. [('l', 'lo')]


# Using these parser combinators directly is flexible, but wordy and
# 'noisy' in Python. So here's a somewhat crude but concise textual
# DSL for parsers.

def parse_grammar(text, get_action=eval):
    """Given a PEG grammar as text like the example below, return a
    dict from nonterminal name to parser. get_action interprets the
    semantic actions in the right-hand column."""

    def analyze_rule(factors, act):
        return take(analyze_factors(factors),
                    lambda values: give(get_action(act)(*values)))

    def analyze_factors(factors):
        if not factors: return give([])
        extend = cons if factors[0].endswith(',') else drop
        return extend(analyze_factor(factors[0]), analyze_factors(factors[1:]))

    def analyze_factor(factor):
        arg, op = factor[:-1], factor[-1:]
        if op in simple_ops:     return simple_ops[op](arg)
        elif op in compound_ops: return compound_ops[op](analyze_factor(arg))
        else:                    return lambda s: parsers[factor](s)

    simple_ops   = {"'": lambda string: match(re.escape(string)),'/': match}
    compound_ops = {'*': star, '?': opt, '+': plus, '!': complement, ',': lambda p: p}

    grammar = {}
    for line in text.splitlines():
        parts = line.split()
        if parts:
            name, factors, act = parts[0], parts[1:-1], parts[-1]
            grammar.setdefault(name, []).append(analyze_rule(factors, act))
    return dict((name, alt(*alts)) for name, alts in grammar.items())


# As an example, a grammar for PEG grammars, which should be nicer than the
# above after we fill in the semantic actions properly and sweat the details.

# * 3-column syntax: nonterminal name, body, semantic action.
# * A body is space-separated 'factors'.
# * A factor can have suffixes *, +, ?, ! (not), / (regex), ' (literal).
# * The comma suffix means "pass this factor's result to the semantic action";
#   without a comma, the result is dropped.
# (I guess it should be prefixes instead of suffixes, but I'm doubting the
# value of this DSL anyway. It takes ~30 lines to implement; it'd
# probably be a better investment to overload Python operators to work
# on parsers, and then with that implement something like the grammar
# below for a better textual DSL.)
peg_rules = r"""
grammar          _ rule+, $/                    make_grammar
rule             name, =' _ peg, .' _           make_rule

peg              term, alt_term*,               fold_alt
alt_term         /' _ term,                     identity
peg                                             epsilon

term             factor+, action?,              fold_seq
action           :' _ name,                     identity

factor           !' _ primary,                  not_
factor           primary, [*+?]/?, _            postfixed

primary          (' _ peg, )' _                 identity
primary          [' char_class*, ]' _           oneof
primary          '' quoted_char*, '' _          literal
primary          name,                          rule_ref
primary          $' _                           eof

char_class       lit_char_class, range?,        char_class
range            -' lit_char_class,             identity

lit_char_class   \' ./,                         escaped_char
lit_char_class   ]'! ./,                        identity

quoted_char      \' ./,                         escaped_char
quoted_char      ''! ./,                        identity

name             alpha, alphanum*, alphanum! _  make_name
alpha            [A-Za-z_]/,                    identity
alphanum         [A-Za-z_0-9]/,                 identity

_                ws_or_comment*                 skip
ws_or_comment    \s/                            skip
ws_or_comment    #[^\n]*\n?/                    skip
"""
make_grammar = lambda rules: '\n'.join(rules)
make_rule    = lambda name, peg: '%s ::= %s.' % (name, peg)
fold_alt     = lambda term, terms: ' / '.join([term] + terms)
identity     = lambda x: x
epsilon      = lambda: '<epsilon>'
fold_seq     = lambda factors, action: (' '.join(factors)
                                        + ('\t:' + action if action else ''))
not_         = lambda p: '!(%s)' % p
postfixed    = lambda p, suffix: '(%s)%s' % (p, suffix) if suffix else p
oneof        = lambda ccs: '{%s}' % ''.join(ccs)
literal      = lambda cs: repr(''.join(cs))
rule_ref     = lambda name: '<%s>' % name
eof          = lambda: '$'
char_class   = lambda x, y: '%s-%s' % (x, y) if y else x
escaped_char = lambda c: '\\' + c
make_name    = lambda letter, letters: letter + ''.join(letters)
skip         = lambda: None

parsers = parse_grammar(peg_rules)


# Smoke test

## parsers['name']('hello there')
#. [('hello', 'there')]

## parsers['primary']("$")
#. [('$', '')]
## parsers['primary']("hey")
#. [('<hey>', '')]
## parsers['primary']("[x-\\yz]")
#. [('{x-\\yz}', '')]
## parsers['primary']("'y\\'o'")
#. [('"y\\\\\'o"', '')]
## parsers['primary']("(hey)")
#. [('<hey>', '')]

## print parse(parsers['grammar'], "start = 'yo' there* /(d u/d[e])+.  end = .")
#. start ::= 'yo' (<there>)* / (<d> <u> / <d> {e})+.
#. end ::= <epsilon>.
#. 
