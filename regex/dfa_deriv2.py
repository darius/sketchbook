"""
Compile a full DFA from a regular expression, using Brzozowski
derivatives with simplification and memoization. Goal: compare
the state counts against methods that go through an NFA.
"""

## mk = Maker()
## re = mk.alt(mk.seq(mk.lit('A'), mk.lit('C')), mk.seq(mk.lit('B'), mk.lit('C')))
## dfa = make_dfa(re)
## for i, (accepting, moves) in enumerate(dfa): print i, ' *'[accepting], moves
#. 0   {'A': 1, 'B': 1}
#. 1   {'C': 2}
#. 2 * {}
#. 

from deriv2 import *

def make_dfa(re):
    """A DFA is a list of pairs (accepting: bool, moves: dict(char->index)).
    where an index is a state number -- a position in the list;
    and 'accepting' means state #i is an accepting state;
    and moves[c] is omitted if c leads to the (implicit) failure state.
    (This keeps the tables much smaller for toy examples at least.)"""
    state_nums, dfa = {}, []
    def fill_in(re):
        moves = {}
        state_nums[re] = len(dfa)
        dfa.append((re.nullable, moves))
        for c in range(256):
            next_state = re.deriv(chr(c))
            if next_state is not fail:
                if next_state not in state_nums: fill_in(next_state)
                moves[chr(c)] = state_nums[next_state]
    fill_in(re)
    return dfa
