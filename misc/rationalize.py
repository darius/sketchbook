"""
Find good rational approximations of real numbers. 

I don't remember where I got this algorithm; I think I adapted it from
some online discussion of Scheme's 'rationalize' primitive.
"""

def rationalize(x, limit):
    """"Return a best rational approximation (numer, denom) to x
    with denom <= limit."""
    assert 0 < limit
    best = None
    for numer, denom in rationalizations(x):
        if limit < denom: break
        best = numer, denom
    return best

def rationalizations(x):
    """Generate good rational approximations of x in order of
    increasing denominator."""
    assert 0 <= x
    ix = int(x)
    yield ix, 1
    if x != ix:
        for numer, denom in rationalizations(1.0/(x-ix)):
            yield denom + ix * numer, numer

## import itertools, math
## def show(x, n): return list(itertools.islice(rationalizations(x), n))

## show(math.e, 8)
#. [(2, 1), (3, 1), (8, 3), (11, 4), (19, 7), (87, 32), (106, 39), (193, 71)]
## show(math.pi, 6)
#. [(3, 1), (22, 7), (333, 106), (355, 113), (103993, 33102), (104348, 33215)]
## show(2.5, 6)
#. [(2, 1), (5, 2)]

## rationalize(math.pi, 1000)
#. (355, 113)
## rationalize(1.125, 1000)
#. (9, 8)
