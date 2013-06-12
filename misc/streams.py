"""
Copy an iterator so it can have multiple consumers. We should only
have to store in memory the interval in the original iterator between
the leftmost and rightmost current consumers of any of the copies;
anything before the leftmost should get GCed.
"""

## eg1 = iter('abc'); print zip(eg1, eg1),
#. [('a', 'b')]
## eg2 = LazyList(iter('abc')); print zip(eg2, eg2),
#. [('a', 'a'), ('b', 'b'), ('c', 'c')]

class LazyList:

    def __init__(self, it):
        self._state = iter(it)
        # _state can be an iterator, None, or False.
        # If iterator: not yet forced.
        # If None:     forcing is in progress or produced a head and tail.
        # if False:    forcing produced a StopIteration.

    def __iter__(self):
        lazylist = self
        while True:
            lazylist._force()
            if lazylist._state is False: break
            yield lazylist._head
            lazylist = lazylist._tail

    def _force(self):
        if self._state:
            it, self._state = self._state, None
            self._tail = LazyList(it)
            try:
                self._head = next(it)
            except StopIteration:
                self._state = False
                del self._tail

    # Plus some Lisp-style methods if you want them:

    def null(self):
        self._force()
        return self._state is False

    def head(self):
        self._force()
        return self._head

    def tail(self):
        self._force()
        return self._tail


# Example application: power series
# TODO finish

import itertools
from itertools import chain, cycle, imap, islice, izip, repeat
import operator

## dir(itertools)
#. ['__doc__', '__file__', '__name__', '__package__', 'chain', 'combinations', 'combinations_with_replacement', 'compress', 'count', 'cycle', 'dropwhile', 'groupby', 'ifilter', 'ifilterfalse', 'imap', 'islice', 'izip', 'izip_longest', 'permutations', 'product', 'repeat', 'starmap', 'takewhile', 'tee']

# http://mitpress.mit.edu/sicp/psets/ps9/ps9.ps

def add(s1, s2): return imap(operator.add, s1, s2)
def sub(s1, s2): return imap(operator.sub, s1, s2)
def scale(c, s): return (c * v for v in s)
def negate(s):   return scale(-1, s)

def coeff(s, i): return next(islice(s, i, i+1))

def series_from_coeffs(coeffs):
    return chain(coeffs, repeat(0))

def series_from_proc(proc):
    return imap(proc, count())

def alt_ones():
    return cycle([1, -1])

def show(s, n=10):
    for v in islice(s, n):
        print v
