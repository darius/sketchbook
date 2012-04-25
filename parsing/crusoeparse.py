"""
Robinson Crusoe's parsing library.
Implements a subset of PEGs -- the most painful lack is of 'not'.
"""

import re

def parse(rule_func, s):

    def parse_rule_func(rule_func, s):
        for production in rule_func():
            s1 = parse_production(production, s)
            if s1: return s1
        return False

    def parse_production(production, s):
        values = []
        for symbol in production[:-1]:
            if isinstance(symbol, str):
                m = re.match(symbol, s)
                r = m and advance(s[m.end():], m.lastindex and m.group(1))
            else:
                r = parse_rule_func(symbol, s)
            if not r:
                return False
            s, value = r
            if value is not None:
                values.append(value)
        return s, production[-1](*values)

    def advance(s, value=None):
        rightmost[0] = min(rightmost[0], len(s))
        return s, value

    rightmost = [len(s)]

    r = parse_rule_func(rule_func, s)
    if r and r[0] == '':
        return r[1]
    p = len(s) - rightmost[0]
    return 'Bad syntax: %s>><<%s' % (s[:p], s[p:])


# Example

def identity(x): return x
def ignore(*args): pass

def cons(x, xs): return [x] + xs
def singleton(x): return [x]


def make_var(v):      return v
def make_lam(v, e):   return '(lambda (%s) %s)' % (v, e)
def make_app(e1, e2): return '(%s %s)' % (e1, e2)

_ = r'\s*'
identifier = r'([A-Za-z_]\w*)\b\s*'

def test(string):

    def start(): return [[_,E,                     identity]]

    def E():     return [[V,                       make_var],
                         [r'\\',_,V,'[.]',_,E,     make_lam],
                         ['[(]',_,E,_,E,_,'[)]',_, make_app]]

    def V():     return [[identifier,              identity]]

    return parse(start, string)

## test('x')
#. 'x'
## test('\\x.x')
#. '(lambda (x) x)'
## test('(x   x)')
#. '(x x)'

## test('hello')
#. 'hello'
## test(' x')
#. 'x'
## test('\\x . y  ')
#. '(lambda (x) y)'
## test('(f \\ x . (hello world))')
#. '(f (lambda (x) (hello world)))'

def foldr(f, z, xs):
    for x in reversed(xs):
        z = f(x, z)
    return z

def test2(string):

    def fold_app(f, fs): return reduce(make_app, fs, f)
    def fold_lam(vp, e): return foldr(make_lam, e, vp)

    def start(): return [[_,E,                     identity]]

    def E():     return [[F,Fs,                    fold_app]]
    def Fs():    return [[F,Fs,                    cons],
                         [                         lambda: []]]

    def F():     return [[V,                       make_var],
                         [r'\\',_,Vp,'[.]',_,E,    fold_lam],
                         ['[(]',_,E,'[)]',_,       identity]]

    def Vp():    return [[V,Vp,                    cons],
                         [V,                       singleton]]

    def V():     return [[identifier,              identity]]

    return parse(start, string)

## test2('x')
#. 'x'
## test2('\\x.x')
#. '(lambda (x) x)'
## test2('(x x)')
#. '(x x)'

## test2('hello')
#. 'hello'
## test2(' x')
#. 'x'
## test2('\\x . y  ')
#. '(lambda (x) y)'
## test2('((hello world))')
#. '(hello world)'


## test2('  hello ')
#. 'hello'
## test2('hello     there hi')
#. '((hello there) hi)'
## test2('a b c d e')
#. '((((a b) c) d) e)'

## test2('')
#. 'Bad syntax: >><<'
## test2('x x . y')
#. 'Bad syntax: x x >><<. y'
## test2('\\.x')
#. 'Bad syntax: \\>><<.x'
## test2('(when (in the)')
#. 'Bad syntax: (when (in the)>><<'
## test2('((when (in the)))')
#. '(when (in the))'

## test2('\\a.a')
#. '(lambda (a) a)'

## test2('  \\hello . (hello)x \t')
#. '(lambda (hello) (hello x))'

## test2('\\M . (\\f . M (f f)) (\\f . M (f f))')
#. '(lambda (M) ((lambda (f) (M (f f))) (lambda (f) (M (f f)))))'

## test2('\\a b.a')
#. '(lambda (a) (lambda (b) a))'

## test2('\\a b c . a b')
#. '(lambda (a) (lambda (b) (lambda (c) (a b))))'


def test3(string):

    def fold_app(f, fs): return reduce(make_app, fs, f)
    def fold_lam(vp, e): return foldr(make_lam, e, vp)

    def start(): return [[_,E,                     identity]]

    def E():     return [[F,Fs,                    fold_app]]
    def Fs():    return [[F,Fs,                    cons],
                         [                         lambda: []]]

    def F():     return [[r'let\b',_,identifier,'=',_,E,';',_,
                          lambda _ident, _E: make_lam(_ident, _E)],
                         [V,                       make_var],
                         [r'\\',_,Vp,'[.]',_,E,    fold_lam],
                         ['[(]',_,E,'[)]',_,       identity]]

    def Vp():    return [[V,Vp,                    cons],
                         [V,                       singleton]]

    def V():     return [[identifier,              identity]]

    return parse(start, string)

## test3('let x=y; x')
#. '((lambda (x) y) x)'
## test3('x')
#. 'x'
## test3('\\x.x')
#. '(lambda (x) x)'
## test3('(x x)')
#. '(x x)'

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
#. 'Bad syntax: >><<'
## test3('x x . y')
#. 'Bad syntax: x x >><<. y'
## test3('\\.x')
#. 'Bad syntax: \\>><<.x'
## test3('(when (in the)')
#. 'Bad syntax: (when (in the)>><<'
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
