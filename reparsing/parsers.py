"""
Parser objects
"""

import re

# You call a parser p by p(parsing, i) and get back di, far, ops.
# parsing: a Parsing object -- holds the input and the chart (the memo table)
# i: what input offset to start parsing p from
# di: None on failure, displacement on success
# far: how far forward in parsing we looked from i
# ops: tuple of operations encoding the semantics

class Call(object):
    def __init__(self, rule):
        self.rule = rule
    def __call__(self, parsing, i):
        return parsing.call(i, self.rule)

class Ops(object):
    def __init__(self, ops):
        self.ops = ops
    def __call__(self, parsing, i):
        return 0, 0, self.ops

def Fail(): return fail
def fail(parsing, i):
    return None, 0, ()

def Empty(): return empty
empty = Ops(())

def Any(): return any_
def any_(parsing, i):
    ch = parsing.text(i, i+1)
    return (1 if ch else None), 1, ()

class Match1(object):
    # Pre: regex match length is always 1 on success
    def __init__(self, regex):
        self.re = re.compile(regex)
        self.source = regex
    def __call__(self, parsing, i):
        m = self.re.match(parsing.subject, i)
        if not m: return None, 1, ()
        assert i+1 == m.end()
        assert not m.groups()
        return 1, 1, ()

class Nix(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        di, far, ops = self.p(parsing, i)
        return (0 if di is None else None), far, ()

class Grab(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        di, far, ops = result = self.p(parsing, i)
        if di is None:
            return result
        else:
            return di, far, ops + (('lit', parsing.subject[i:i+di]),)

class Seclude(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        di, far, ops = result = self.p(parsing, i)
        if di is None:
            return result
        else:
            return di, far, (('[',),) + ops + ((']',),)

class Either(object):
    def __init__(self, p, q):
        self.p, self.q = p, q
    def __call__(self, parsing, i):
        di, far1, ops = result = self.p(parsing, i)
        if di is not None: return result
        di, far2, ops = self.q(parsing, i)
        return di, max(far1, far2), ops

class Then(object):
    def __init__(self, p, q):
        self.p, self.q = p, q
    def __call__(self, parsing, i):
        di1, far1, ops1 = result1 = self.p(parsing, i)
        if di1 is None: return result1
        di2, far2, ops2 = self.q(parsing, i+di1)
        far = max(far1, di1+far2)
        if di2 is None: return None, far, ()
        else:           return di1+di2, far, ops1+ops2

class Repeat(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        di, far, ops = 0, 0, ()
        while True:
            di2, far2, ops2 = self.p(parsing, i+di)
            far = max(far, di+far2)
            if di2 is None:
                return di, far, ops
            di += di2
            ops += ops2
    

# Helpers

def foldr(f, z, xs):
    for x in reversed(xs):
        z = f(x, z)
    return z


# Derived parsers

def Do(name):      return Ops((('do',name),))
def Push(literal): return Ops((('lit',literal),))

def Chain(*ps):  return foldr(Chain2, empty, ps)
def Choice(*ps): return foldr(Choice2, fail, ps)

def Chain2(p, q):
    if p is empty: return q
    if q is empty: return p
    return Then(p, q)

def Choice2(p, q):
    if p is fail: return q
    if q is fail: return p
    return Either(p, q)

def Literal1(ch):
    return Match1(re.escape(ch))

def Literal(s):
    return Chain(*[Literal1(ch) for ch in s])

def MatchN(*regexes):
    return Chain(*[Match1(r) for r in regexes])

def Maybe(p):
    return Choice(p, empty)

def Plus(p, separator=None):
    if separator is None:
        return Chain(p, Repeat(p))
    else:
        return Chain(p, Repeat(Chain(separator, p)))

def Star(p, separator=None):
    if separator is None:
        return Repeat(p)
    else:
        return Maybe(Plus(p, separator))
