"""
mjd's 17 puzzle.
Given 5 integers a, b, c, d, and e, find an expression that combines
a, b, c, and d with arithmetic operations (+, -, *, and /) to get e.
"""

from __future__ import division
from itertools import product

def puzzle(target, nums):
    nums = tuple(nums)
    for e in exprs_over(nums):
        try:
            v = eval(e)
        except ZeroDivisionError:
            pass
        else:
            if v == target:
                print e

commutative_ops    = ('+', '*')
noncommutative_ops = ('-', '/')
both_ops = commutative_ops + noncommutative_ops

def exprs_over(nums):
    if len(nums) == 1:
        yield nums[0]
    elif 1 < len(nums):
        for L, R in splits(nums):
            if not L or not R: continue  # Just a shortcut.
            for x, y in product(exprs_over(L), exprs_over(R)):
                for op in both_ops:
                    yield '(%s %s %s)' % (x, op, y)
                for op in noncommutative_ops:
                    yield '(%s %s %s)' % (y, op, x)

def splits(xs):
    if len(xs) == 1:
        yield (), xs
        yield xs, ()
    else:
        for L, R in splits(xs[1:]):
            yield L+(xs[0],), R
            yield L, R+(xs[0],)

## list(splits((3,7)))
#. [((3,), (7,)), ((), (7, 3)), ((7, 3), ()), ((7,), (3,))]
## list(splits((1,3,7)))
#. [((3, 1), (7,)), ((3,), (7, 1)), ((1,), (7, 3)), ((), (7, 3, 1)), ((7, 3, 1), ()), ((7, 3), (1,)), ((7, 1), (3,)), ((7,), (3, 1))]

### for e in exprs_over((1,3,7)): print e

## puzzle(17, [6,6,5,2])
#. (6 * (2 + (5 / 6)))
#. (6 * (2 + (5 / 6)))
#. (6 * ((5 / 6) + 2))
#. (6 * ((5 / 6) + 2))
#. (6 * (2 + (5 / 6)))
#. (6 * (2 + (5 / 6)))
#. (6 * ((5 / 6) + 2))
#. (6 * ((5 / 6) + 2))
#. ((2 + (5 / 6)) * 6)
#. ((2 + (5 / 6)) * 6)
#. (((5 / 6) + 2) * 6)
#. (((5 / 6) + 2) * 6)
#. ((2 + (5 / 6)) * 6)
#. ((2 + (5 / 6)) * 6)
#. (((5 / 6) + 2) * 6)
#. (((5 / 6) + 2) * 6)
