"""
Regular expression matching, and incremental DFA construction, using
even-more-simplified and memoized Brzozowski derivatives.
TODO:
 - Show the DFAs
 - Generalize the paths taken, a la EBG, so you don't have to
   re-derive derivatives for different characters that you can
   tell act the same. (Though this can be more costly -- the
   other characters might never appear.)
   Scheme: make deriv(c) return both the derivative and a set
   of characters that give the same derivative.
 - intersection and complement
 - more tests
 - fuller API
"""

def match(re, s):
    for c in s:
        # (This redundant test lets us exit early sometimes.)
        if re is fail: return False
        re = re.deriv(c)
    return re.nullable

class MemoTable(dict):
    def enter(self, key, make):
        if key not in self:
            self[key] = make()
        return self[key]

class RE(object):
    def __init__(self):
        self.transitions = MemoTable()
    def deriv(self, c):
        return self.transitions.enter(c, lambda: self.derivative(c))
    def derivative(self, c):
        abstract

class Fail(RE):
    nullable = False
    def derivative(self, c):
        return self
fail = Fail()

class Empty(RE):
    nullable = True
    def derivative(self, c):
        return fail
empty = Empty()

class Lit(RE):
    nullable = False
    def __init__(self, c):
        RE.__init__(self)
        assert len(c) == 1
        self.c = c
    def derivative(self, c):
        return empty if c == self.c else fail

class Alt(RE):
    def __init__(self, mk, re_set):
        RE.__init__(self)
        assert isinstance(re_set, frozenset)
        self.nullable = any(re.nullable for re in re_set)
        self.mk = mk
        self.re_set = re_set
    def derivative(self, c):
        return self.mk.alt(*[re.deriv(c) for re in self.re_set])

class Seq(RE):
    def __init__(self, mk, res):
        RE.__init__(self)
        assert isinstance(res, tuple) and 0 < len(res)
        self.nullable = all(re.nullable for re in res)
        self.mk = mk
        self.res = res
    def derivative(self, c):
        re, res = self.res[0], self.res[1:]
        blocking = self.mk.seq(re.deriv(c), *res)
        if re.nullable: return self.mk.alt(blocking, self.mk.seq(*res).deriv(c))
        else: return blocking

class Many(RE):
    nullable = True
    def __init__(self, mk, re):
        RE.__init__(self)
        self.mk = mk
        self.re = re
    def derivative(self, c):
        return self.mk.seq(self.re.deriv(c), self)

class Maker:

    def __init__(self):
        self.lits = MemoTable()
        self.alts = MemoTable()
        self.seqs = MemoTable()
        self.stars = MemoTable()

    def lit(self, c):
        return self.lits.enter(c, lambda: Lit(c))

    def alt(self, *res):
        acc = collect_alternatives(res)
        if len(acc) == 0: return fail
        if len(acc) == 1: return acc[0]
        res = frozenset(acc)
        return self.alts.enter(res, lambda: Alt(self, res))

    def seq(self, *res):
        if fail in res: return fail
        res = collect_sequence(res)
        if len(res) == 0: return empty
        if len(res) == 1: return res[0]
        return self.seqs.enter(res, lambda: Seq(self, res))

    def many(self, re):
        if re is fail or re is empty: return empty
        if isinstance(re, Many): return re
        return self.stars.enter(re, lambda: Many(self, re))

def collect_alternatives(res):
    acc = []
    for re in res:
        if re is fail:
            pass
        elif isinstance(re, Alt):
            acc.extend(re.re_set)
        else:
            acc.append(re)
    return acc

def collect_sequence(res):
    acc = []
    for re in res:
        if re is empty:
            pass
        elif isinstance(re, Seq):
            acc.extend(re.res)
        else:
            acc.append(re)
    return tuple(acc)


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
## match(mk.many(mk.lit('a')), 'xx')
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
