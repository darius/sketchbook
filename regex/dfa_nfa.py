"""
DFAs from NFAs. My immediate goal is to count the DFA states produced
from vanilla NFA building vs. memoized. We find that memoization does
reduce the state count on the example from "Regular-expression
derivatives reexamined". It probably won't do as well as DFAs via
derivatives, since we don't use all the simplification rules; but it
did improve on naive Thompson NFA->DFA here.
"""

## re = alt(seq(lit('A'), lit('C')), seq(lit('B'), lit('C')))
## dfa = make_dfa(prepare(re))
## for i, (accepting, moves) in enumerate(dfa): print i, ' *'[accepting], moves
#. 0   {'A': 1, 'B': 1}
#. 1   {'C': 2}
#. 2 * {}
#. 

def make_dfa(nfa_start_states):
    """A DFA is a list of pairs (accepting: bool, moves: dict(char->index)).
    where an index is a state number -- a position in the list;
    and 'accepting' means state #i is an accepting state;
    and moves[c] is omitted if c leads to the (implicit) failure state.
    (This keeps the tables much smaller for toy examples at least.)"""
    state_nums, dfa = {}, []
    def fill_in(state):
        moves = {}
        state_nums[state] = len(dfa)
        dfa.append((accepting_state in state, moves))
        for c in range(256):
            next_state = step(state, chr(c))
            if next_state:
                if next_state not in state_nums: fill_in(next_state)
                moves[chr(c)] = state_nums[next_state]
    fill_in(frozenset(nfa_start_states))
    return dfa

def step(state, c):
    return frozenset(set.union(*[nfa_state(c) for nfa_state in state]))


def memoize(f):
    memos = {}
    def memoized(*args):
        if args not in memos: memos[args] = f(*args)
        return memos[args]
    return memoized

# To try it without memoization, reenable this:
if False:
    def memoize(f): return f

# N.B. 'state' here in an NFA means something different from the DFA
# states above. I should fix this or something.
def accepting_state(c): return set()
@memoize
def expecting_state(char, k): return lambda c: k(set()) if c == char else set()

@memoize
def state_node(state): return lambda seen: set([state])
@memoize       # TODO: use associativity/commutativity to memoize more
def alt_node(k1, k2):
    if k1 is k2: return k1
    else: return lambda seen: k1(seen) | k2(seen)

@memoize
def loop_node(k, make_k):
    def loop(seen):
        if loop in seen: return set()
        seen.add(loop)
        return k(seen) | looping(seen)
    looping = make_k(loop)
    return loop

def prepare(re): return re(state_node(accepting_state))(set())

# The following are memoized solely to help loop_node(), above, profit
# from its own memoization.
@memoize
def lit(char):     return lambda k: state_node(expecting_state(char, k))
@memoize
def alt(re1, re2): return lambda k: alt_node(re1(k), re2(k))
@memoize
def many(re):      return lambda k: loop_node(k, re)
def empty(k):      return k
@memoize
def seq(re1, re2): return lambda k: re1(re2(k))
