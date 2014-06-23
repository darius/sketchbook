"""
Format Lisp lists using a version of the offside rule.
A list can be Lisp-style: ((a x) (b (y) z) (c))
Or offside-style: a x
                  b (y) z
                  c
In the latter case it's preceded by a ':'.
As defined here, ':' appears only after a non-list car of a list.
"""

def pr(x):
    assert isinstance(x, list)
    if x and not isinstance(x[0], list) and all(y and isinstance(y, list) for y in x[1:]):
        hd = lispr(x[0]) + ': '
        margin = '\n' + ' '*len(hd)
        return hd + margin.join(pr(y).replace('\n', margin) for y in x[1:])
    else:
        return lispr(x)[1:-1]

def lispr(x):
    if isinstance(x, list):
        if not x:
            return '()'
        else:
            return '(' + lispr_each(x) + ')'
    else:
        return str(x)

def lispr_each(xs):
    return ' '.join(map(lispr, xs))

## a = ['define', ['factorial', 'n'], ['if', ['=', 'n', 0], ['blah', 1], ['*', ['n', ['factorial', ['-', 'n', 1]]]]]]
## lispr(a)
#. '(define (factorial n) (if (= n 0) (blah 1) (* (n (factorial (- n 1))))))'
## print pr(a)
#. define: factorial n
#.         if: = n 0
#.             blah 1
#.             *: n: factorial: - n 1
