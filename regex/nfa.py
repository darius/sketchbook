"""
Regular-expression matching by the Thompson construction.
"""

def match(re, s):
    states = set([re(accepting)])
    for c in s:
        states = set.union(*[state(c) for state in states])
    return any(BING in state(EOF) for state in states)

EOF, BING = object(), object()
def accepting(c): return set([BING]) if c is EOF else set()

def fail(k):
    return lambda c: set()

def empty(k):
    return accepting

def lit(char):
    return lambda k: lambda c: set([k]) if char == c else set()

def seq(re1, re2):
    return lambda k: re1(re2(k))

def alt(re1, re2):
    return lambda k: lambda c: re1(k)(c) | re2(k)(c)

def many(re):
    def me(k):
        def state(c):
            return k(c) | re(state)(c)
        return state
    return me


## match(fail, '')
#. False
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
