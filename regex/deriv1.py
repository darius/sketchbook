"""
Regular expression matching using simplified and memoized Brzozowski
derivatives.
"""

def match(re, s):
    for c in s:
        re = re(c)
    return re.nullable

def mark(nullable, deriv):
    deriv.nullable = nullable
    return deriv

fail = mark(False, lambda c: fail)
empty = mark(True, lambda c: fail)

def _lit(literal):
    return mark(False, lambda c: empty if c == literal else fail)

class MemoTable(dict):
    def enter(self, key, make):
        if key not in self:
            self[key] = make()
        return self[key]

class Maker:

    def __init__(self):
        self.lits = MemoTable()
        self.alts = MemoTable()
        self.seqs = MemoTable()
        self.stars = MemoTable()

    def lit(self, literal):
        return self.lits.enter(literal, lambda: _lit(literal))

    def alt(self, re1, re2):
        if re1 is fail: return re2
        if re2 is fail: return re1
        return self.alts.enter((re1, re2), lambda: self._alt(re1, re2))

    def _alt(self, re1, re2):
        return mark(re1.nullable or re2.nullable,
                    lambda c: self.alt(re1(c), re2(c)))

    def seq(self, re1, re2):
        if re1 is empty: return re2
        if re2 is empty: return re1
        if re1 is fail or re2 is fail: return fail
        return self.seqs.enter((re1, re2), lambda: self._seq(re1, re2))

    def _seq(self, re1, re2):
        if re1.nullable:
            def sequence(c): return self.alt(self.seq(re1(c), re2), re2(c))
        else:
            def sequence(c): return self.seq(re1(c), re2)
        return mark(re1.nullable and re2.nullable, sequence)

    def many(self, re):
        if re is fail or re is empty: return empty
        return self.stars.enter(re, lambda: self._many(re))

    def _many(self, re):
        def loop(c): return self.seq(re(c), loop)
        return mark(True, loop)

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

## match(mk.many(mk.many(mk.lit('x'))), 'xxxx')
#. True
## match(mk.many(mk.many(mk.lit('x'))), 'xxxxy')
#. False

## match(mk.seq(empty, mk.lit('x')), '')
#. False
## match(mk.seq(empty, mk.lit('x')), 'x')
#. True

## mk.lit('x') is mk.lit('x')
#. True
## mk.alt(mk.lit('x'), mk.lit('y')) is mk.alt(mk.lit('x'), mk.lit('y'))
#. True
## mk.seq(mk.lit('x'), mk.lit('y')) is mk.seq(mk.lit('x'), mk.lit('y'))
#. True
## mk.many(mk.lit('x')) is mk.many(mk.lit('x'))
#. True
