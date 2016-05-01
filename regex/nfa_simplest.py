"""
Like nfa.hs after the further edits to remove the 'fork' state constructors.
"""

def match(re, chars):
    states = re([accept])
    for c in chars:
        states = set(sum((state(c) for state in states), []))
    return accept in states

accept = lambda c: []
def expect(ch, ks): return lambda c: ks if ch == c else []

empty = lambda ks: ks
def lit(ch):   return lambda ks: [expect(ch, ks)]
def seq(r, s): return lambda ks: r(s(ks))
def alt(r, s): return lambda ks: r(ks) + s(ks)
def many(r):
    def rstar(ks):
        ks = ks[:]
        ks.extend(k for k in r(ks) if k not in ks)
        return ks
    return rstar

## match(seq(many(lit('a')), lit('b')), 'aaab')
#. True
## match(seq(many(many(lit('a'))), lit('b')), 'aaab')
#. True

## match(empty, '')
#. True
## match(empty, 'A')
#. False
## match(lit('x'), '')
#. False
## match(lit('x'), 'y')
#. False
## match(lit('x'), 'x')
#. True
## match(lit('x'), 'xx')
#. False
## match(seq(lit('a'), lit('b')), '')
#. False
## match(seq(lit('a'), lit('b')), 'ab')
#. True
## match(alt(lit('a'), lit('b')), 'b')
#. True
## match(alt(lit('a'), lit('b')), 'a')
#. True
## match(alt(lit('a'), lit('b')), 'x')
#. False
## match(many(lit('a')), '')
#. True
## match(many(lit('a')), 'a')
#. True
## match(many(lit('a')), 'x')
#. False
## match(many(lit('a')), 'aa')
#. True
## match(many(lit('a')), 'ax')
#. False

## complicated = seq(many(alt(seq(lit('a'), lit('b')), seq(lit('a'), seq(lit('x'), lit('y'))))), lit('z'))
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

## match(many(many(lit('x'))), 'xxxx')
#. True

## match(seq(empty, lit('x')), '')
#. False
## match(seq(empty, lit('x')), 'x')
#. True
