"""
Like nfa.hs. This version has some clarity advantages over the original
nfa.py. Yes, I'm drowning in versions here.
"""

def matches(re, chars):
    states = [re(accept)]
    for c in chars:
        states = set(sum((n(c) for a, n in states), []))
    return any(a for a, n in states)

accept = (True, lambda _: [])

empty = lambda state: state
def seq(re1, re2): return lambda state: re1(re2(state))

def lit(char):
    return lambda state: (False, lambda c: [state] if char == c else [])

def alt(re1, re2):
    def either(state):
        (a1,n1), (a2,n2) = re1(state), re2(state)
        return (a1 or a2, lambda c: n1(c) + n2(c))
    return either

def many(re):
    def re_star((a, n)):
        loop = (a, lambda c: n(c) + n_re_plus(c)) 
        (_, n_re_plus) = re(loop)
        return loop
    return re_star



match = matches
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
