"""
BDDs. We assume everywhere that Choices in the same expression come
from the same Maker.
"""

infinite_rank = float('Inf')

class Constant:
    def __init__(self, value):
        self.test = self
        self.value = value
    def __repr__(self):
        return 'LR'[self.value]
    def rank(self, ranker):
        return infinite_rank
    def choice(self, maker, a, m, z):
        return m.choose(maker, a, z)
    def choose(self, maker, a, z):
        return z if self.value else a
    def subst(self, maker, var, value):
        return self
    def satisfy(self, target):
        return set([()]) if self is target else set()

L = Constant(False)
R = Constant(True)

class Choice:
    def __init__(self, on_L, variable, on_R):
        self.on_L = on_L
        self.test = variable
        self.on_R = on_R
    def __repr__(self):
        if self.on_L is L and self.on_R is R:
            return self.test
        return '<%r %s %r>' % (self.on_L, self.test, self.on_R)
    def rank(self, ranker):
        return ranker(self.test)
    def choice(self, maker, a, m, z):
        assert self.rank(maker.ranker) <= maker.rank(a)
        assert self.rank(maker.ranker) <= maker.rank(m)
        assert self.rank(maker.ranker) <= maker.rank(z)
        subst, test = maker.subst, self.test
        return maker.cons(maker.choice(subst(a, test, L),
                                       subst(m, test, L),
                                       subst(z, test, L)),
                          test,
                          maker.choice(subst(a, test, R),
                                       subst(m, test, R),
                                       subst(z, test, R)))
    def choose(self, maker, a, z):
        return min(a, self, z, key=maker.rank).choice(maker, a, self, z)
    def subst(self, maker, var, value):
        if var is self.test:
            return value.choose(maker, self.on_L, self.on_R)
        else:
            assert maker.rank(var) < maker.rank(self.test)
            return self
    def satisfy(self, target):
        "Return a set of the substitutions that make self reduce to target."
        # TODO: memoize
        assert isinstance(target, Constant)
        left, right = self.on_L.satisfy(target), self.on_R.satisfy(target)
        to_L, to_R = ((self.test, L),), ((self.test, R),)
        return (left & right
                | set(to_L + s for s in left - right)
                | set(to_R + s for s in right - left))

class Maker:
    def __init__(self, ranker):
        self.ranker = ranker
        self.choices = {}
    def make_variable(self, name):
        return self.cons(L, intern(name), R)
    def rank(self, e):
        return e.rank(self.ranker)
    def choice(self, a, m, z):
        return m.choose(self, a, z)
    def cons(self, a, v, z):
        assert self.ranker(v) <= self.rank(a)
        assert self.ranker(v) <= self.rank(z)
        if a is z: return a
        key = (a, v, z)
        if key not in self.choices:
            self.choices[key] = Choice(a, v, z)
        return self.choices[key]
    def subst(self, e, v, c):
        assert self.ranker(v) <= self.rank(e)
        assert c in (L, R)
        return e if self.ranker(v) < self.rank(e) else e.subst(self, v, c)

    def neg(self, a):    return self.choice(R, a, L)
    def imp(self, a, b): return self.choice(R, a, b)
    # TODO: first sort a, b by rank in the following?
    def min(self, a, b): return self.choice(L, a, b)
    def max(self, a, b): return self.choice(b, a, R)
    def eqv(self, a, b): return self.choice(self.neg(b), a, b)
    def neq(self, a, b): return self.choice(b, a, self.neg(b))

## m = Maker(ord)
## a, b, c = map(m.make_variable, 'abc')

## m.choice(L, L, L)
#. L
## m.choice(L, L, R)
#. L
## m.choice(L, R, L)
#. L
## m.choice(L, R, R)
#. R
## m.choice(R, L, L)
#. R
## m.choice(R, L, R)
#. R
## m.choice(R, R, L)
#. L
## m.choice(R, R, R)
#. R

## m.choice(b, L, c)
#. b
## m.choice(b, a, c)
#. <b a c>
## m.choice(c, a, b)
#. <c a b>
## m.choice(a, b, c)
#. <<L b c> a <R b c>>

## a.satisfy(L)
#. set([(('a', L),)])

## m.choice(b, a, c).satisfy(L)
#. set([(('a', L), ('b', L)), (('a', R), ('c', L))])

## sorted(m.choice(a, b, c).satisfy(L))
#. [(('a', L), ('b', L)), (('b', R), ('c', L))]
## sorted(m.choice(a, b, c).satisfy(R))
#. [(('a', R), ('b', L)), (('b', R), ('c', R))]

## m.neg(a)
#. <R a L>

## m.min(a, a)
#. a
## m.imp(a, a)
#. R
## m.neq(a, a)
#. L

## m.min(a, m.neg(a))
#. L
## m.max(a, m.neg(a))
#. R
## m.eqv(a, m.neg(a))
#. L
## m.neq(a, m.neg(a))
#. R
## m.imp(a, m.neg(a)).satisfy(R)
#. set([(('a', L),)])

## m.imp(a, b)
#. <R a b>
## m.imp(m.imp(a, b), a)
#. a
## m.imp(m.imp(m.imp(a, b), a), a)
#. R
