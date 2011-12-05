"""
DFAs from NFAs. My immediate goal is to count the DFA states produced
from vanilla NFA building vs. memoized. We find that memoization does
reduce the state count on the example from "Regular-expression
derivatives reexamined". It probably won't do as well as DFAs via
derivatives, since we don't use all the simplification rules; but it
did improve on naive Thompson NFA->DFA here.

TODO:
Memoization coalesces states that act like equivalent suffixes of a
regex, but it doesn't help with common prefixes. We could catch those
too with a second pass that takes the NFA and builds a reversed NFA,
memoizing in the same way. (Right?) If we take this approach, it'd
make sense for the first pass to go left to right (instead of the
current right-to-left) so that after the second pass the arrows point
forwards.

Simple example input this should help with:

    hello|hellward|awkward|jello

What's a good more-complex example including loops?

(Would it be just as good, and easier, to do this bidirectional
memoizing at the regex level and then just NFAify in one pass as
before?)

So, like this? (but memoized) --

reverse rk AcceptingNode       = rk
reverse rk (ExpectingNode n k) = reverse k (ExpectingNode n rk)
reverse rk (ForkNode k1 k2)    = reverse rk k1 `fork` reverse rk k2
reverse rk (LoopNode k makeK) = loop where
                                loop = LoopNode (reverse rk k)
                                                (reverse loop (makeK AcceptingNode))
"""


### re = seq(lit('0'), many(many(seq(lit('1'), lit('0')))))
### re = seq(alt(lit('A'), empty), many(lit('B')))

## re = alt(seq(lit('A'), lit('C')), seq(lit('B'), lit('C')))
## dfa = make_dfa(prepare((1, re)))
## dump(dfa)
#. 0     {'A': 1, 'B': 1}
#. 1     {'C': 2}
#. 2 <1> {}
#. 

def dump(dfa):
    for i, (label, moves) in enumerate(dfa):
        if label is None: label = '   '
        else: label = '<%s>' % label
        print i, label, ' '.join('%r:%d' % pair for pair in sorted(moves.items()))

def make_scanner(whitespace, res):
    res = [whitespace] + res
    return set.union(*map(prepare, enumerate(res)))

def prepare((label, re)):
    return re(state_node(make_accepting_state(label)))(set())

def make_dfa(scanner):
    """A DFA is a list of pairs (label_or_None, moves: dict(char->index)).
    where an index is a state number -- a position in the list;
    and label_or_None can mark an accepting state;
    and moves[c] is omitted if c leads to the (implicit) failure state.
    (This keeps the tables much smaller for toy examples at least.)
    0 is the implicit start state."""
    state_nums, dfa = {}, []
    def fill_in(state):
        moves = {}
        state_nums[state] = len(dfa)
        labels = [st.label for st in state if hasattr(st, 'label')]
        label = min(labels) if labels else None
        dfa.append((label, moves))
        for c in range(256):
            next_state = step(state, chr(c))
            if next_state:
                if next_state not in state_nums: fill_in(next_state)
                moves[chr(c)] = state_nums[next_state]
    fill_in(frozenset(scanner))
    return dfa

def step(state, c):
    return frozenset(set.union(*[nfa_state(c) for nfa_state in state]))


from memo import memoize
# To try it without memoization, reenable this:
if False:
    def memoize(f): return f


# N.B. 'state' here in an NFA means something different from the DFA
# states above. I should fix this or something.
@memoize
def make_accepting_state(label):
    def accepting_state(c): return set()
    accepting_state.label = label
    return accepting_state
@memoize
def expecting_state(char, k): return lambda c: k(set()) if c == char else set()

@memoize
def state_node(state): return lambda seen: set([state])
@memoize       # TODO: use associativity to memoize more
def alt_node(k1, k2):
    if k1 is k2: return k1
    # ('<' to canonicalize; but it doesn't seem to matter so far:)
    if k2 < k1: return alt_node(k2, k1)
    return lambda seen: k1(seen) | k2(seen)

@memoize
def loop_node(k, make_k):
    def loop(seen):
        if loop in seen: return set()
        seen.add(loop)
        return k(seen) | looping(seen)
    looping = make_k(loop)
    # This optimization of the NFA makes no difference in the final
    # DFA, but could help a bit if we use the NFA directly for
    # matching. Or, perhaps, it could help expose opportunities for
    # the other optimizations to work, though I haven't seen it to.
    # XXX subsumed by many(re) check below
    if looping is loop: return k
    return loop

# The following are memoized solely to help loop_node(), above, profit
# from its own memoization.
@memoize
def lit(char):     return lambda k: state_node(expecting_state(char, k))
@memoize
def alt(re1, re2): return lambda k: alt_node(re1(k), re2(k))
@memoize
def many(re):
    def me(k): return loop_node(k, re)
    if re.func_code is me.func_code: return re # XXX hack
    return me
def empty(k):      return k
@memoize
def seq(re1, re2):
    if re1 is empty: return re2
    if re2 is empty: return re1
    return lambda k: re1(re2(k))

class Struct:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def Maker():
    return Struct(**globals())
