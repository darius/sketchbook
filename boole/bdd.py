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
    def choose(self, maker, a, z):
        return z if self.value else a
    def subst(self, maker, var, value):
        return self
    def satisfy(self, target, memos):
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
    def choose(self, maker, a, z):
        mk = maker
        t = min(a, self, z, key=maker.rank).test
        return mk.cons(self.subst(mk, t, L).choose(mk,
                                                   a.subst(mk, t, L),
                                                   z.subst(mk, t, L)),
                       t,
                       self.subst(mk, t, R).choose(mk,
                                                   a.subst(mk, t, R),
                                                   z.subst(mk, t, R)))
    def subst(self, maker, var, value):
        if var is self.test:
            return value.choose(maker, self.on_L, self.on_R)
        else:
            assert maker.ranker(var) < maker.rank(self)
            return self
    def satisfy(self, target, memos):
        "Return a set of the substitutions that make self reduce to target."
        if self not in memos:
            left  = self.on_L.satisfy(target, memos)
            right = self.on_R.satisfy(target, memos)
            memos[self] = (left & right
                           | set(((self.test, L),) + s for s in left - right)
                           | set(((self.test, R),) + s for s in right - left))
        return memos[self]

def satisfy(e, target):
    assert isinstance(target, Constant)
    return sorted(e.satisfy(target, {}))

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

## satisfy(a, L)
#. [(('a', L),)]

## satisfy(m.choice(b, a, c), L)
#. [(('a', L), ('b', L)), (('a', R), ('c', L))]

## satisfy(m.choice(a, b, c), L)
#. [(('a', L), ('b', L)), (('b', R), ('c', L))]
## satisfy(m.choice(a, b, c), R)
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
## satisfy(m.imp(a, m.neg(a)), R)
#. [(('a', L),)]

## m.imp(a, b)
#. <R a b>
## m.imp(m.imp(a, b), a)
#. a
## m.imp(m.imp(m.imp(a, b), a), a)
#. R
