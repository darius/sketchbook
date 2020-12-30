"""
Parser objects
"""

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

class Fail(object):
    def __call__(self, parsing, i):
        return None, 0, ()

class Empty(object):
    def __call__(self, parsing, i):
        return 0, 0, ()

fail = Fail()
empty = Empty()

class Do(object):
    def __init__(self, name):
        self.ops = (('do',name),)
    def __call__(self, parsing, i):
        return 0, 0, self.ops

class Range(object):
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
    def __call__(self, parsing, i):
        ch = parsing.text(i, i+1)
        if ch == '':
            return None, 0, ()
        else:
            return (1 if self.lo <= ch <= self.hi else None), 1, ()

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
            return di, far, ops + (('grab',i,di),)

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

class Chain(object):
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
    

# Derived parsers

def Literal(s):
    result = empty
    for ch in reversed(s):
        parser = Range(ch, ch)
        result = parser if result is empty else Chain(parser, result)
    return result

def Maybe(p):
    return Either(p, empty)

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
