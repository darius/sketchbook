import DFA                      # 'his' DFAs

def minimal_state_count(dfa):
    """Return the minimum number of states an equivalent dfa can
    have. Don't count the error state if one must be added to satisfy
    the DFA module's definition of a dfa."""
    dfa_with_error = maybe_add_error_state(dfa)
    error_diff = len(dfa_with_error) - len(dfa)
    his = his_from_mine(dfa_with_error)
    his.minimize()
    return len(his.states) - error_diff

def his_from_mine(dfa):
    dfa = maybe_add_error_state(dfa)
    states = range(len(dfa))
    return DFA.DFA(states,
                   get_alphabet(dfa),
                   lambda state, c: dfa[state][1][c],
                   0,
                   [state for state in states if dfa[state][0]])

def get_alphabet(dfa):
    return set(c for _, moves in dfa for c in moves)

def maybe_add_error_state(dfa):
    "Return an equivalent to dfa with no missing move-table entries."
    alphabet = get_alphabet(dfa)
    if all(len(moves) == len(alphabet) for _, moves in dfa):
        return dfa
    error_state = len(dfa)    # A new state for the missing moves to go to
    return [(accepting, dict((c, moves.get(c, error_state))
                             for c in alphabet))
            for accepting, moves in dfa + [(False, {})]]

def mine_from_his(his):
    # Not quite right -- we still need to make state 0 the start state.
    nstates = len(his.states)
    perm = dict((his_state, i) for i, his_state in enumerate(his.states))
    print perm
    states = [(state in his.accepts, dict((c, perm[his.delta(state, c)])
                                          for c in his.alphabet))
              for state in his.states]
    return perm[his.start], states

## dfa = [(False, {'0': 1}), (True, {'1': 0, '0': 2}), (False, {'0': 1})]
## maybe_add_error_state(dfa)
#. [(False, {'1': 3, '0': 1}), (True, {'1': 0, '0': 2}), (False, {'1': 3, '0': 1}), (False, {'1': 3, '0': 3})]

## his = his_from_mine(dfa)
## his.states
#. set([0, 1, 2, 3])
## his.alphabet
#. set(['1', '0'])
## his.accepts
#. set([1])


## his.minimize()
## his.states
#. [1, 0, 3]
## mine_from_his(his)
#. {0: 1, 1: 0, 3: 2}
#. 
#. (1, [(True, {'1': 1, '0': 1}), (False, {'1': 2, '0': 0}), (False, {'1': 2, '0': 2})])
