"""
Find good rational approximations of real numbers. 

I don't remember where I got this algorithm; 
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

## show(2**(1./12), 5)
#. [(1, 1), (17, 16), (18, 17), (89, 84), (196, 185)]
## show(math.e, 8)
#. [(2, 1), (3, 1), (8, 3), (11, 4), (19, 7), (87, 32), (106, 39), (193, 71)]
## show(math.pi, 6)
#. [(3, 1), (22, 7), (333, 106), (355, 113), (103993, 33102), (104348, 33215)]
## show(2.5, 6)
#. [(2, 1), (5, 2)]
## show(math.log(10, 2), 6)
#. [(3, 1), (10, 3), (93, 28), (196, 59), (485, 146), (2136, 643)]
## show(math.log(10), 8)
#. [(2, 1), (7, 3), (23, 10), (76, 33), (99, 43), (175, 76), (624, 271), (3919, 1702)]
## show(.5 * (1+math.sqrt(5)), 8)
#. [(1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (13, 8), (21, 13), (34, 21)]

## rationalize(math.pi, 1000)
#. (355, 113)
## rationalize(1.125, 1000)
#. (9, 8)

"""
Ah, here's my source: I derived the logic from this Scheme code, whose
author I'm afraid I didn't record -- I think it was from some online
discussion of Scheme's 'rationalize' primitive.:

(define (find-ratio-between x y)
  (define (sr x y)
    (let ((fx (exact (floor x))) 
          (fy (exact (floor y))))
      (cond 
       ((>= fx x) (list fx 1))
       ((= fx fy) (let ((rat (sr (/ (- y fy))
                                 (/ (- x fx)))))
                    (list (+ (cadr rat) (* fx (car rat))) (car rat))))
       (else (list (+ 1 fx) 1)))))
  (cond 
    ((< y x) (find-ratio-between y x))
    ((>= x y) (list x 1))
    ((positive? x) (sr x y))
    ((negative? y) (let ((rat (sr (- y) (- x))))
                     (list (- (car rat)) (cadr rat))))
    (else '(0 1))))

N.B. you can't define find-ratio-between in terms of my
rationalizations().
"""
