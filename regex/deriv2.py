"""
Regular expression matching, and incremental DFA construction, using
even-more-simplified and memoized Brzozowski derivatives.

Rather less clunky, but also less Pythonic, than deriv.py.
"""

from memo import memoize

def match(re, s):
    for c in s:
        re = re.deriv(c)
        # (This redundant test lets us exit early sometimes.)
        if re is fail: return False
    return re.nullable

def mark(nullable, deriv, tag, args):
    deriv.nullable = nullable
    deriv.tag = tag
    deriv.args = args
    deriv.deriv = memoize(deriv)
    return deriv

fail = mark(False, lambda c: fail, 'fail', ())
empty = mark(True, lambda c: fail, 'empty', ())

def _lit(literal): return mark(False,
                               lambda c: empty if c == literal else fail,
                               'lit', literal)

class Maker:

    def __init__(self):
        self.empty  = empty
        self.lit    = memoize(_lit)
        self.mkalt  = memoize(self._alt)
        self.mkseq  = memoize(self._seq)
        self.mkmany = memoize(self._many)

    def alt(self, *res):
        res = collect_alternatives(res)
        if len(res) == 0: return fail
        if len(res) == 1:
            for re in res:
                return re
        return self.mkalt(res)

    def _alt(self, re_set):
        return mark(any(re.nullable for re in re_set),
                    lambda c: self.alt(*[re.deriv(c) for re in re_set]),
                    'alt', re_set)

    def seq(self, *res):
        if fail in res: return fail
        res = collect_sequence(res)
        if len(res) == 0: return empty
        if len(res) == 1: return res[0]
        return self.mkseq(res)

    def _seq(self, res):
        hd, tl = res[0], res[1:]
        if hd.nullable:
            def sequence(c): return self.alt(self.seq(hd.deriv(c), *tl),
                                             self.seq(*tl).deriv(c))
        else:
            def sequence(c): return self.seq(hd.deriv(c), *tl)
        return mark(all(re.nullable for re in res),
                    sequence,
                    'seq', res)

    def many(self, re):
        if re is fail or re is empty: return empty
        if re.tag is 'many': return re
        return self.mkmany(re)

    def _many(self, re):
        def loop(c): return self.seq(re.deriv(c), loop)
        return mark(True, loop, 'many', (re,))

def collect_alternatives(res):
    acc = []
    for re in res:
        if re.tag is 'alt':
            acc.extend(re.args)
        elif re is not fail:
            acc.append(re)
    return frozenset(acc)

def collect_sequence(res):
    acc = []
    for re in res:
        if re.tag is 'seq':
            acc.extend(re.args)
        elif re is not empty:
            acc.append(re)
    return tuple(acc)

def show(re):
    if re.tag is 'lit':
        return repr(re.args)
    return '%s(%s)' % (re.tag, ', '.join(map(show, re.args)))

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
