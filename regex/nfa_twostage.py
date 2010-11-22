"""
Regular-expression matching by the Thompson construction.
Explained in C at http://swtch.com/~rsc/regexp/regexp1.html

Like nfa_stifleloops.py, but all the loop detection goes into the
preparation stage; then the match stage can just use the already-
computed successor sets. This scheme seems likely to be the NFA
variant fastest at matching. I wish it were a bit simpler, though
it's not too bad.
"""

def match(re, s): return run(prepare_nfa(prepare(re)), s)

def prepare_nfa(k):
    states = k(set())
    for state in states:
        if state.successors is None:
            state.successors = 'computing'
            state.successors = prepare_nfa(state.k)
    return states

def run(states, s):
    for c in s:
        states = set.union(*[state(c) for state in states])
    return accepting_state in states

def expecting_state(char, k):
    def me(c): return me.successors if c == char else set()
    me.k = k
    me.successors = None
    return me

accepting_state = expecting_state(None, lambda seen: set())

def state_node(state):
    return lambda seen: set([state])

def alt_node(k1, k2):
    return lambda seen: k1(seen) | k2(seen)

def loop_node(k, make_k):
    def loop(seen):
        if loop in seen: return set()
        seen.add(loop)
        return k(seen) | looping(seen)
    looping = make_k(loop)
    return loop

def prepare(re): return re(state_node(accepting_state))

def lit(char):     return lambda k: state_node(expecting_state(char, k))
def alt(re1, re2): return lambda k: alt_node(re1(k), re2(k))
def many(re):      return lambda k: loop_node(k, re)
def empty(k):      return k
def seq(re1, re2): return lambda k: re1(re2(k))


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
