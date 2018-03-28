"""
Derived from nfa_simplest_set.py
XXX the code's rather a mess.
"""

def match(re, chars):
    nfa[:] = [(None, set())]
    succs = re(set([0]))
    for i, (ch, states) in enumerate(nfa):
        nfa[i] = (ch, set_to_int(states))
    states = set_to_int(succs)
    for c in chars:
        new_states = 0
        for i, (ch, succs) in enumerate(nfa):
            if ((states>>i) & 1) and c == ch:
                new_states |= succs
        states = new_states
    return (states & 1) != 0

nfa = []

def expect(ch, succs):
    state = len(nfa)
    nfa.append((ch, succs))
    return state

def set_to_int(indices):
    return sum(1<<i for i in indices)

empty = lambda succs: succs
def lit(ch):   return lambda succs: set([expect(ch, succs)])
def seq(r, s): return lambda succs: r(s(succs))
def alt(r, s): return lambda succs: r(succs) | s(succs)
def many(r):
    def rstar(succs):
        succs = set(succs)
        succs.update(r(succs))
        return succs
    return rstar

## match(seq(many(lit('a')), lit('b')), 'aaab')
#. True
## match(seq(many(many(lit('a'))), lit('b')), 'aaab')
#. True

# (a*)*b
# (a?|b)**
## match(many(many(alt(lit('b'), alt(lit('a'), empty)))), 'aabab')
#. True

# (a*b*)*
## match(many(seq(many(lit('a')), many(lit('b')))), 'aaabba')
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

## match(many(many(lit('x'))), 'xxxx')
#. True

## match(seq(empty, lit('x')), '')
#. False
## match(seq(empty, lit('x')), 'x')
#. True
