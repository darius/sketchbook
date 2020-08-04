"""
Enumerate all regular expressions of a given size over a given
alphabet. Parameterized by the regular-expression constructor.
"""

from memo import memoize

@memoize
def gen_res(maker, alphabet, size):
    acc = []
    if size == 1:
        acc.append(maker.empty)
        acc.extend(map(maker.lit, alphabet))
    if 2 <= size:
        acc.extend(map(maker.many, gen_res(maker, alphabet, size - 1)))
    if 3 <= size:
        for i in range(1, size - 1):
            for re1 in gen_res(maker, alphabet, i):
                for re2 in gen_res(maker, alphabet, size - 1 - i):
                    acc.append(maker.alt(re1, re2))
                    acc.append(maker.seq(re1, re2))
    return acc


## from parse import TreeMaker

## for re in gen_res(TreeMaker(), '01', 3): print re
#. many(many(empty))
#. many(many('0'))
#. many(many('1'))
#. alt(empty, empty)
#. seq(empty, empty)
#. alt(empty, '0')
#. seq(empty, '0')
#. alt(empty, '1')
#. seq(empty, '1')
#. alt('0', empty)
#. seq('0', empty)
#. alt('0', '0')
#. seq('0', '0')
#. alt('0', '1')
#. seq('0', '1')
#. alt('1', empty)
#. seq('1', empty)
#. alt('1', '0')
#. seq('1', '0')
#. alt('1', '1')
#. seq('1', '1')

## for size in range(9): print 2, size, len(gen_res(TreeMaker(), '01', size))
#. 2 0 0
#. 2 1 3
#. 2 2 3
#. 2 3 21
#. 2 4 57
#. 2 5 327
#. 2 6 1263
#. 2 7 6753
#. 2 8 30621

## for size in range(9): print 3, size, len(gen_res(TreeMaker(), '012', size))
#. 3 0 0
#. 3 1 4
#. 3 2 4
#. 3 3 36
#. 3 4 100
#. 3 5 708
#. 3 6 2884
#. 3 7 18404
#. 3 8 90276
