"""
Find minimal regular expressions over a given alphabet that
satisfy a test.
"""

from re import escape, match
from memo import memoize

def find_minimal_re(alphabet, ok, max_size=9):
    for size in range(1, max_size+1):
        for re in gen_res(alphabet, size):
            if ok(re):
                yield re

@memoize
def gen_res(alphabet, size):
    acc = []
    if size == 1:
        acc.append('')
        acc.extend(map(escape, alphabet))
    if 2 <= size:
        acc.extend('(%s)*' % r
                   for r in gen_res(alphabet, size - 1)
                   if not match(r, ''))
    if 3 <= size:
        for i in range(1, size - 1):
            for re1 in gen_res(alphabet, i):
                for re2 in gen_res(alphabet, size - 1 - i):
                    acc.append('(%s)|(%s)' % (re1, re2))
                    acc.append('(%s)(%s)' % (re1, re2))
    return acc

def eg_example():
    return next(find_minimal_re('ab', lambda r: match('(%s)$' % r, 'abba') and not match('(%s)$'%r, 'baba')),
                None)

## eg_example()
#. '((a)((b)*))*'
