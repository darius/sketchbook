"""
Regular expression matching using simplified and memoized Brzozowski
derivatives.
"""

def match(re, s):
    for c in s:
        re = re.deriv(c)
    return re.nullable

class Fail:
    nullable = False
    def deriv(self, c):
        return self
fail = Fail()

class Empty:
    nullable = True
    def deriv(self, c):
        return fail
empty = Empty()

class Lit:
    nullable = False
    def __init__(self, c):
        assert len(c) == 1
        self.c = c
    def deriv(self, c):
        return empty if c == self.c else fail

class Alt:
    def __init__(self, mk, re1, re2):
        self.nullable = re1.nullable or re2.nullable
        self.mk = mk
        self.re1 = re1
        self.re2 = re2
    def deriv(self, c):
        return self.mk.alt(self.re1.deriv(c), self.re2.deriv(c))

class Seq:
    def __init__(self, mk, re1, re2):
        self.nullable = re1.nullable and re2.nullable
        self.mk = mk
        self.re1 = re1
        self.re2 = re2
    def deriv(self, c):
        blocking = self.mk.seq(self.re1.deriv(c), self.re2)
        if self.re1.nullable: return self.mk.alt(blocking, self.re2.deriv(c))
        else: return blocking

class Many:
    nullable = True
    def __init__(self, mk, re):
        self.mk = mk
        self.re = re
    def deriv(self, c):
        return self.mk.seq(self.re.deriv(c), self)

class MemoTable(dict):
    def get(self, key, make):
        if key not in self:
            self[key] = make()
        return self[key]

class Maker:

    def __init__(self):
        self.lits = MemoTable()
        self.alts = MemoTable()
        self.seqs = MemoTable()
        self.stars = MemoTable()

    def lit(self, c):
        return self.lits.get(c, lambda: Lit(c))

    def alt(self, re1, re2):
        if re1 is fail: return re2
        if re2 is fail: return re1
        return self.alts.get((re1, re2), lambda: Alt(self, re1, re2))

    def seq(self, re1, re2):
        if re1 is empty: return re2
        if re2 is empty: return re1
        if re1 is fail or re2 is fail: return fail
        return self.seqs.get((re1, re2), lambda: Seq(self, re1, re2))

    def many(self, re):
        if re is fail or re is empty: return empty
        return self.stars.get(re, lambda: Many(self, re))


## mk = Maker()

## match(fail, '')
#. False
## match(empty, '')
#. True
## match(empty, 'A')
#. False
## match(mk.lit('x'), '')
#. False
## match(mk.lit('x'), 'y')
#. False
## match(mk.lit('x'), 'x')
#. True
## match(mk.lit('x'), 'xx')
#. False
### match(mk.lit('abc'), 'abc')
## match(mk.seq(mk.lit('a'), mk.lit('b')), '')
#. False
## match(mk.seq(mk.lit('a'), mk.lit('b')), 'ab')
#. True
## match(mk.alt(mk.lit('a'), mk.lit('b')), 'b')
#. True
## match(mk.alt(mk.lit('a'), mk.lit('b')), 'a')
#. True
## match(mk.alt(mk.lit('a'), mk.lit('b')), 'x')
#. False
## match(mk.many(mk.lit('a')), '')
#. True
## match(mk.many(mk.lit('a')), 'a')
#. True
## match(mk.many(mk.lit('a')), 'x')
#. False
## match(mk.many(mk.lit('a')), 'aa')
#. True

## complicated = mk.seq(mk.many(mk.alt(mk.seq(mk.lit('a'), mk.lit('b')), mk.seq(mk.lit('a'), mk.seq(mk.lit('x'), mk.lit('y'))))), mk.lit('z'))
## match(complicated, '')
#. False
## match(complicated, 'z')
#. True
## match(complicated, 'abz')
#. True
## match(complicated, 'ababaxyab')
#. False
## match(complicated, 'ababaxyabz')
#. True
## match(complicated, 'ababaxyaxz')
#. False

## mk.lit('x') is mk.lit('x')
#. True
## mk.alt(mk.lit('x'), mk.lit('y')) is mk.alt(mk.lit('x'), mk.lit('y'))
#. True
## mk.seq(mk.lit('x'), mk.lit('y')) is mk.seq(mk.lit('x'), mk.lit('y'))
#. True
## mk.many(mk.lit('x')) is mk.many(mk.lit('x'))
#. True
