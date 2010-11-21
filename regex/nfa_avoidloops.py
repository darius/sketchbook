"""
Regular-expression matching by the Thompson construction.
Explained in C at http://swtch.com/~rsc/regexp/regexp1.html

Avoid epsilon-loops by construction. Needs more testing.
"""

def run(states, s):
    for c in s:
        states = set.union(*[state(c) for state in states])
    return accepting_state in states

def accepting_state(c): return set()
def expecting_state(char, k): return lambda c: k() if c == char else set()

def state_node(state): return lambda: set([state])
def alt_node(k1, k2):  return lambda: k1() | k2()
def loop_node(k, make_k):
    def loop(): return k() | looping()
    looping = make_k(loop)
    return looping

def match(re, s):
    return run(optionalize(re)(state_node(accepting_state))(), s)

def optionalize((null, re)):
    return lambda k: alt_node(k, re(k)) if null else re(k)

def lit(char):
    return False, lambda k: state_node(expecting_state(char, k))

def alt((null1, re1), (null2, re2)):
    return null1 or null2, lambda k: alt_node(re1(k), re2(k))

def many((null, re)):
    return True, many1((False, re))[1]

def many1((null, re)):    
    return null, lambda k: loop_node(k, re)

empty = (True, lambda k: k)

def seq((null1, re1), (null2, re2)):
    if null1 and null2:
        def re1_re2(k):  # (re1 | re2 | re1 re2) k = (re1 re2? | re2) k
            k2 = re2(k)
            return alt_node(re1(alt_node(k, k2)), k2)
        return True, re1_re2
    else:
        ore1 = optionalize((null1, re1))
        ore2 = optionalize((null2, re2))
        return False, lambda k: ore1(ore2(k))


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
## match(many(many(lit('x'))), 'xxxx')
#. True
## match(many(many(lit('x'))), 'xxxxy')
#. False

# Had a bug: empty forced a match regardless of the continuation.
## match(seq(empty, lit('x')), '')
#. False
## match(seq(empty, lit('x')), 'x')
#. True
