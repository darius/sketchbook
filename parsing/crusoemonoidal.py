"""
Newer variant on crusoeparse, with an infusion of monoidal.py.
"""

import re

def parse(x, s):
#    print 'parse', x, s
    p = x() if callable(x) else x
    if isinstance(p, (str, unicode)): return parse_regex(p, s)
    if isinstance(p, list):           return parse_rules(p, s)
    if callable(p):                   return p(s)
    raise ValueError("Not coerceable to a peg", x)

def parse_rules(rules, s):

    def parse_rule(rule, s):
        vals, peggables, act = [], rule[:-1], rule[-1]
        for p in peggables:
            p_vals, s = parse(p, s)
            if s is None: return (), None
            vals.extend(p_vals)
        r_vals = () if act is ignore else (act(*vals),)
        return r_vals, s

    for rule in rules:
        vals, s1 = parse_rule(rule, s)
        if s1 is not None: return vals, s1
    return (), None

def ignore(*vals): return ()

def parse_regex(regex, s):
    m = re.match(regex, s)
    return (m.groups(), s[m.end():]) if m else ((), None)

def complement(peggable):
    return lambda: lambda s: (((), s) if parse(peggable, s)[1] is None
                              else ((), None))


# Smoke test

def identity(x): return x

def a(): return [['(x)', c, 'y',         identity]]
def b(): return [['z',                   ignore]]
def c(): return [[complement('z'), '.',  ignore]]

## parse('x', 'y')
#. ((), None)
## parse(complement('x'), 'y')
#. ((), 'y')

## parse(a, 'xayu')
#. (('x',), 'u')
## parse(a, 'xzyu')
#. ((), None)


# Lambda calculus test

def test3(string):

    def fold_app(f, fs): return reduce(make_app, fs, f)
    def fold_lam(vp, e): return foldr(make_lam, e, vp)

    def start(): return [[_,E,                              identity]]

    def E():     return [[F,Fs,                             fold_app]]
    def Fs():    return [[F,Fs,                             cons],
                         [                                  nil]]

    def F():     return [[r'let\b',_,V,'=',_,E,';',_,E,     make_let],
                         [V,                                make_var],
                         [r'\\',_,Vp,'[.]',_,E,             fold_lam],
                         ['[(]',_,E,'[)]',_,                identity]]

    def Vp():    return [[V,Vp,                             cons],
                         [V,                                singleton]]

    def V():     return [[complement(r'let\b'), identifier, identity]]

    res = parse(start, string)[0]
    return res[0] if res else None

def make_var(v):         return v
def make_lam(v, e):      return '(lambda (%s) %s)' % (v, e)
def make_app(e1, e2):    return '(%s %s)' % (e1, e2)
def make_let(v, e1, e2): return '(let ((%s %s)) %s)' % (v, e1, e2)

_          = r'\s*'  # TODO add comments
identifier = r'([A-Za-z_]\w*)\b\s*'

def cons(x, xs):  return [x] + xs
def singleton(x): return [x]
def nil():        return []

def foldr(f, z, xs):
    for x in reversed(xs):
        z = f(x, z)
    return z

## test3('x')
#. 'x'
## test3('\\x.x')
#. '(lambda (x) x)'
## test3('(x x)')
#. '(x x)'
## test3('let x=y; x')
#. '(let ((x y)) x)'

## test3('let let=y; x')

## test3('hello')
#. 'hello'
## test3(' x')
#. 'x'
## test3('\\x . y  ')
#. '(lambda (x) y)'
## test3('((hello world))')
#. '(hello world)'

## test3('  hello ')
#. 'hello'
## test3('hello     there hi')
#. '((hello there) hi)'
## test3('a b c d e')
#. '((((a b) c) d) e)'

## test3('')
## test3('x x . y')
#. '(x x)'
## test3('\\.x')
## test3('(when (in the)')
## test3('((when (in the)))')
#. '(when (in the))'

## test3('\\a.a')
#. '(lambda (a) a)'

## test3('  \\hello . (hello)x \t')
#. '(lambda (hello) (hello x))'

## test3('\\M . (\\f . M (f f)) (\\f . M (f f))')
#. '(lambda (M) ((lambda (f) (M (f f))) (lambda (f) (M (f f)))))'

## test3('\\a b.a')
#. '(lambda (a) (lambda (b) a))'

## test3('\\a b c . a b')
#. '(lambda (a) (lambda (b) (lambda (c) (a b))))'


# Regular expressions test

regex_grammar = r"""
regex      expr $                  identity

expr       term alt_term*          cons_alt
alt_term*  \| term alt_term*       cons
alt_term*                          nil

term       factor factors          cons_seq
factors    ![)|] term              identity
factors                            epsilon

factor     prim [*]?               maybe_star

prim       \( expr \)              identity
prim       \\ (.)                  escaped_lit
prim       ![*+?|()\\] (.)         lit
"""

def regex_test(string):

    def regex():     return [[expr, '',                          identity]]

    def expr():      return [[term, r'\|', expr,                 alt],
                             [term,                              identity]]

    def term():      return [[factor, complement(r'[)|]'), term,   seq],
                             [factor,                              identity]]

    def factor():    return [[prim, '[*]',                       star],
                             [prim,                              identity]]

    def prim():      return [[r'\(', expr, r'\)',                identity],
                             [r'\\', '(.)',                      escaped_lit],
                             [complement(r'[*+?|()\\]'), '(.)',  lit]]

    res = parse(regex, string)[0]
    return res[0] if res else None

def alt(p, q): return '(%s)|(%s)' % (p, q)
def seq(p, q): return '(%s)%s' % (p, q)
def star(p):   return p + '*'
def lit(c):    return c
def escaped_lit(c): return r'\%s' % c

## regex_test('a')
#. 'a'
## regex_test('a|bc*')
#. '(a)|((b)c*)'
## regex_test('a(bc)*d')
#. '(a)((b)c*)d'
