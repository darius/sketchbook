"""
Regular-expression matching by the Thompson construction.
Explained in C at http://swtch.com/~rsc/regexp/regexp1.html

This code follows the same interface as backtrack.py in this same
directory. backtrack.py is easier to follow but suffers exponential
blowup on some regexes. Both of these loop on nested stars like
r'a**', though (as Thompson himself pointed out in his
paper). deriv.py OTOH should work in all cases, but needs more code.
"""

def match(re, s):
    states = set([re(accepting)])
    for c in s:
        states = set.union(*[state(c) for state in states])
    return any(BING in state(EOF) for state in states)

def empty(k):  return k
def lit(char): return lambda k: lambda c: set([k]) if char == c else set()

EOF, BING = object(), object()
accepting = lit(EOF)(BING)

def seq(re1, re2): return lambda k: re1(re2(k))

def alt(re1, re2):
    def either(k):
        k1, k2 = re1(k), re2(k)
        return lambda c: k1(c) | k2(c)
    return either

def many(re):
    def re_star(k):
        def loop(c): return k(c) | re_plus(c)
        re_plus = re(loop)
        return loop
    return re_star


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

# N.B. infinite recursion, like Thompson's original code:
### match(many(many(lit('x'))), 'xxxx')

# Had a bug: empty forced a match regardless of the continuation.
## match(seq(empty, lit('x')), '')
#. False
## match(seq(empty, lit('x')), 'x')
#. True
