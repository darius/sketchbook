"""
Parser objects
"""

import re

# You call a parser p by p(parsing, i) and get back hop, peek, ops.
# parsing: a Parsing object -- holds the input and the chart (the memo table)
# i: what input offset to start parsing p from
# hop: None on failure, displacement on success
# peek: how far forward in parsing we looked from i
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

# XXX not generally correct when edits are allowed, because
# if doesn't peek only forward, but backward too. I'm using
# this anyway because I only realized this while typing it in,
# and I'll probably get away with it for a while. Tempting fate.
def word_boundary(parsing, i):
    m = word_boundary_pat.match(parsing.subject, i)
    return (0 if m else None), 1, ()
word_boundary_pat = re.compile(r'\b')

class Nix(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        hop, peek, ops = self.p(parsing, i)
        return (0 if hop is None else None), peek, ()

class Grab(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        hop, peek, ops = result = self.p(parsing, i)
        if hop is None:
            return result
        else:
            return hop, peek, ops + (('lit', parsing.subject[i:i+hop]),)

class Seclude(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        hop, peek, ops = result = self.p(parsing, i)
        if hop is None:
            return result
        else:
            return hop, peek, (('[',),) + ops + ((']',),)

class Either(object):
    def __init__(self, p, q):
        self.p, self.q = p, q
    def __call__(self, parsing, i):
        hop, peek1, ops = result = self.p(parsing, i)
        if hop is not None: return result
        hop, peek2, ops = self.q(parsing, i)
        return hop, max(peek1, peek2), ops

class Then(object):
    def __init__(self, p, q):
        self.p, self.q = p, q
    def __call__(self, parsing, i):
        hop1, peek1, ops1 = result1 = self.p(parsing, i)
        if hop1 is None: return result1
        hop2, peek2, ops2 = self.q(parsing, i+hop1)
        peek = max(peek1, hop1+peek2)
        if hop2 is None: return None, peek, ()
        else:            return hop1+hop2, peek, ops1+ops2

class Repeat(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        hop, peek, ops = 0, 0, ()
        while True:
            hop2, peek2, ops2 = self.p(parsing, i+hop)
            peek = max(peek, hop+peek2)
            if hop2 is None:
                return hop, peek, ops
            if hop2 == 0: raise Exception("Stuck on repeat", parsing, i+hop)
            hop += hop2
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
    return Chain(*map(Literal1, s))

def MatchN(*regexes):
    return Chain(*map(Match1, regexes))

def Keyword(s):
    return Chain(Literal(s), word_boundary)

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

# (commented out to not conflict with Parson's `end`)
# end = Nix(Any)

eol = Choice(Literal1('\n'), Nix(any_))
def Eol(): return eol
