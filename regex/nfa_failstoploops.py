"""
Regular-expression matching by the Thompson construction.
Explained in C at http://swtch.com/~rsc/regexp/regexp1.html
"""

def match((null, re), s):
    agenda = re(state_node(accepting_state))()
    for c in s:
        agenda = set.union(*[state(c) for state in agenda])
    return accepting_state in agenda

def accepting_state(c): return set()
def expecting_state(char, k): return lambda c: k() if c == char else set()

def state_node(state): return lambda: set([state])
def alt_node(k1, k2):  return lambda: k1() | k2()
def loop_node(k, make_k):
    def loop(): return k() | looping()
    looping = make_k(loop)
    return loop

def lit(char):
    return False, lambda k: state_node(expecting_state(char, k))
def alt((null1, re1), (null2, re2)):
    return null1 or null2, lambda k: alt_node(re1(k), re2(k))
def many((null, re)):
    assert not null, "I can't handle nested stars"
    return True, lambda k: loop_node(k, re)
empty = (True, lambda k: k)
def seq((null1, re1), (null2, re2)):
    return null1 and null2, lambda k: re1(re2(k))


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
#. Traceback (most recent call last):
#.   File "nfa_failstoploops.py", line 82, in <module>
#.     ## match(many(many(lit('x'))), 'xxxx')
#.   File "nfa_failstoploops.py", line 27, in many
#.     assert not null, "I can't handle nested stars"
#. AssertionError: I can't handle nested stars
## match(many(many(lit('x'))), 'xxxxy')
#. Traceback (most recent call last):
#.   File "nfa_failstoploops.py", line 87, in <module>
#.     ## match(many(many(lit('x'))), 'xxxxy')
#.   File "nfa_failstoploops.py", line 27, in many
#.     assert not null, "I can't handle nested stars"
#. AssertionError: I can't handle nested stars

# Had a bug: empty forced a match regardless of the continuation.
## match(seq(empty, lit('x')), '')
#. False
## match(seq(empty, lit('x')), 'x')
#. True
