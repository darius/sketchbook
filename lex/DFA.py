# From http://code.google.com/p/python-automata/
# python-automata, the Python DFA library
# License: New BSD License
# Author: Andrew Badr
# Version: July 17, 2008
# Contact: andrewbadr@gmail.com
# Code contributions are welcome.

from copy import copy
from UnionFind import UnionFind

# TODO: general code cleanup
# TODO: write tests

class DFA:
    """This class represents a deterministic finite automaton."""
    def __init__(self, states, alphabet, delta, start, accepts):
        """The inputs to the class are as follows:
         - states: An iterable containing the states of the DFA. States must be immutable.
         - alphabet: An iterable containing the symbols in the DFA's alphabet. Symbols must be immutable.
         - delta: A complete function from [states]x[alphabets]->[states].
         - start: The state at which the DFA begins operation.
         - accepts: A list containing the "accepting" or "final" states of the DFA.

        Making delta a function rather than a transition table makes it much easier to define certain DFAs. 
        If you want to use a transition table, you can just do this:
         delta = lambda q,c: transition_table[q][c]
        One caveat is that the function should not depend on the value of 'states' or 'accepts', since
        these may be modified during minimization.

        Finally, the names of states and inputs should be hashable. This generally means strings, numbers,
        or tuples of hashables.
        """
        self.states = set(states)
        self.start = start
        self.delta = delta
        self.accepts = set(accepts)
        self.alphabet = set(alphabet)
        self.current_state = start

#
# Administrative functions:
#

    def pretty_print(self):
        """Displays all information about the DFA in an easy-to-read way. Not
        actually that easy to read if it has too many states.
        """
        print ""
        print "This DFA has %s states" % len(self.states)
        print "States:", self.states
        print "Alphabet:", self.alphabet
        print "Starting state:", self.start
        print "Accepting states:", self.accepts
        print "Transition function:"
        print "\t","\t".join(map(str, sorted(self.states)))
        for c in self.alphabet:
            results = map(lambda x: self.delta(x, c), sorted(self.states))
            print c, "\t", "\t".join(map(str, results))
        print "Current state:", self.current_state
        print "Currently accepting:", self.status()
        print ""

    def validate(self):
        """Checks that: 
        (1) The accepting-state set is a subset of the state set.
        (2) The start-state is a member of the state set.
        (3) The current-state is a member of the state set.
        (4) Every transition returns a member of the state set.
        """
        assert set(self.accepts).issubset(set(self.states))
        assert self.start in self.states
        assert self.current_state in self.states
        for state in self.states:
            for char in self.alphabet:
                assert self.delta(state, char) in self.states

    def copy(self):
        """Returns a copy of the DFA. No data is shared with the original."""
        return DFA(self.states, self.alphabet, self.delta, self.start, self.accepts)

#
# Simulating execution:
#

    def input(self, char):
        """Updates the DFA's current state based on a single character of input."""
        self.current_state = self.delta(self.current_state, char)

    def input_sequence(self, char_sequence):
        """Updates the DFA's current state based on an iterable of inputs."""
        for char in char_sequence:
            self.input(char)

    def status(self):
        """Indicates whether the DFA's current state is accepting."""
        return (self.current_state in self.accepts)

    def reset(self):
        """Returns the DFA to the starting state."""
        self.current_state = self.start

    def recognizes(self, char_sequence):
        """Indicates whether the DFA accepts a given string."""
        state_save = self.current_state
        self.reset()
        self.input_sequence(char_sequence)
        valid = self.status()
        self.current_state = state_save
        return valid

#
# Minimization methods and their helper functions
#
    def state_hash(self, value):
        """Creates a hash with one key for every state in the DFA, and
        all values initialized to the 'value' passed.
        """
        d = {}
        for state in self.states:
            if callable(value):
                d[state] = value()
            else:
                d[state] = value
        return d

    def state_merge(self, q1, q2):
        """Merges q1 into q2. All transitions to q1 are moved to q2.
        If q1 was the start or current state, those are also moved to q2.
        """
        self.states.remove(q1)
        if q1 in self.accepts:
            self.accepts.remove(q1)
        if self.current_state == q1:
            self.current_state = q2
        if self.start == q1:
            self.start = q2
        transitions = {}
        for state in self.states: #without q1
            transitions[state] = {}
            for char in self.alphabet:
                next = self.delta(state, char)
                if next == q1:
                    next = q2
                transitions[state][char] = next
        self.delta = (lambda s, c: transitions[s][c])

    def reachable_from(self, q0, inclusive=True):
        """Returns the set of states reachable from given state q0. The optional
        parameter "inclusive" indicates that q0 should always be included.
        """
        reached = self.state_hash(False)
        if inclusive:
            reached[q0] = True
        to_process = [q0]
        while len(to_process):
            q = to_process.pop()
            for c in self.alphabet:
                next = self.delta(q, c)
                if reached[next] == False:
                    reached[next] = True
                    to_process.append(next)
        return filter(lambda q: reached[q], self.states)

    def reachable(self):
        """Returns the reachable subset of the DFA's states."""
        return self.reachable_from(self.start)

    def delete_unreachable(self):
        """Deletes all the unreachable states."""
        reachable = self.reachable()
        self.states = reachable
        new_accepts = []
        for q in self.accepts:
            if q in self.states:
                new_accepts.append(q)
        self.accepts = new_accepts

    def mn_classes(self):
        """Returns a partition of self.states into Myhill-Nerode equivalence classes."""
        changed = True
        classes = []
        if self.accepts != []:
            classes.append(self.accepts)
        nonaccepts = filter(lambda x: x not in self.accepts, self.states)
        if nonaccepts != []:
            classes.append(nonaccepts)
        while changed:
            changed = False
            for cl in classes:
                local_change = False
                for alpha in self.alphabet:
                    next_class = None
                    new_class = []
                    for state in cl:
                        next = self.delta(state, alpha)
                        if next_class == None:
                            for c in classes:
                                if next in c:
                                    next_class = c
                        elif next not in next_class:
                            new_class.append(state)
                            changed = True
                            local_change = True
                    if local_change == True:
                        old_class = []
                        for c in cl:
                            if c not in new_class:
                                old_class.append(c)
                        classes.remove(cl)
                        classes.append(old_class)
                        classes.append(new_class)
                        break
        return classes

    def collapse(self, partition):
        """Given a partition of the DFA's states into equivalence classes,
        collapses every equivalence class into a single "representative" state.
        Returns the hash mapping each old state to its new representative.
        """
        new_states = []
        new_start = None
        new_delta = None
        new_accepts = []
        #alphabet stays the same
        new_current_state = None
        state_map = {}
        #build new_states, new_start, new_current_state:
        for state_class in partition:
            representative = state_class[0]
            new_states.append(representative)
            for state in state_class:
                state_map[state] = representative
                if state == self.start:
                    new_start = representative
                if state == self.current_state:
                    new_current_state = representative
        #build new_accepts:
        for acc in self.accepts:
            if acc in new_states:
                new_accepts.append(acc)
        #build new_delta:
        transitions = {}
        for state in new_states:
            transitions[state] = {}
            for alpha in self.alphabet:
                transitions[state][alpha] = state_map[self.delta(state, alpha)]
        new_delta = (lambda s, a: transitions[s][a])
        self.states = new_states
        self.start = new_start
        self.delta = new_delta
        self.accepts = new_accepts
        self.current_state = new_current_state
        return state_map

    def minimize(self):
        """Classical DFA minimization, using the simple O(n^2) algorithm.
        Side effect: can mix up the internal ordering of states.
        """
        #Step 1: Delete unreachable states
        self.delete_unreachable()
        #Step 2: Partition the states into equivalence classes        
        classes = self.mn_classes()
        #Step 3: Construct the new DFA
        self.collapse(classes)

    def preamble_and_kernel(self):
        """Returns the partition of the state-set into the preamble and 
        kernel as a 2-tuple. A state is in the preamble iff there 
        are finitely many strings that reach it from the start state.

        See "The DFAs of Finitely Different Regular Languages" for context.
        """
        #O(n^2): can this be improved?
        reachable = {}
        for q in self.states:
            reachable[q] = self.reachable_from(q, inclusive=False)
        in_fin = self.state_hash(True)
        for q in reachable[self.start]:
            if q in reachable[q]:
                for next in reachable[q]:
                    in_fin[next] = False
        preamble = filter(lambda x: in_fin[x], self.states)
        kernel = filter(lambda x: not in_fin[x], self.states)
        return (preamble, kernel)

    def pluck_leaves(self):
        """Only for minimized automata. Returns a topologically ordered list of
        all the states that induce a finite language. Runs in linear time.
        """
        #Step 1: Build the states' profiles
        loops    = self.state_hash(0)
        inbound  = self.state_hash(list)
        outbound = self.state_hash(list)
        for state in self.states:
            for c in self.alphabet:
                next = self.delta(state, c)
                inbound[next].append(state)
                outbound[state].append(next)
                if state == next:
                    loops[state] += 1
        #Step 2: Add sink state to to_pluck
        to_pluck = []
        for state in self.states:
            if len(outbound[state]) == loops[state]:
                if not state in self.accepts:
                    #prints("Adding '%s' to be plucked" % state)
                    to_pluck.append(state)
        #Step 3: Pluck!
        plucked = []
        while len(to_pluck):
            state = to_pluck.pop()
            #prints("Plucking %s" % state)
            plucked.append(state)
            for incoming in inbound[state]:
                #prints("Deleting %s->%s edge" % (incoming, state))
                outbound[incoming].remove(state)
                if (len(outbound[incoming]) == 0) and (incoming != state):
                    to_pluck.append(incoming)
                    #prints("Adding '%s' to be plucked" % incoming)
        plucked.reverse()
        return plucked

    def right_finite_states(self, sink_states):
        """Given a DFA (self) and a list of states (sink_states) that are assumed to induce the
        empty language, return the topologically-ordered set of states in the DFA that induce
        finite languages.
        """
        #Step 1: Build the states' profiles
        inbound  = self.state_hash(list)
        outbound = self.state_hash(list)
        for state in self.states:
            if state in sink_states:
                continue
            for c in self.alphabet:
                next = self.delta(state, c)
                inbound[next].append(state)
                outbound[state].append(next)

        #Step 2: Pluck!
        to_pluck = sink_states
        plucked = []
        while len(to_pluck):
            state = to_pluck.pop()
            plucked.append(state)
            for incoming in inbound[state]:
                outbound[incoming].remove(state)
                if (len(outbound[incoming]) == 0) and (incoming != state):
                    to_pluck.append(incoming)
        plucked.reverse()
        return plucked
 
    def is_finite(self):
        """Indicates whether the DFA's language is a finite set."""
        D2 = self.copy()
        D2.minimize()
        plucked = D2.pluck_leaves()
        return (D2.start in plucked)

    def states_fd_equivalent(self, q1, q2):
        """Indicates whether q1 and q2 only have finitely many distinguishing strings."""
        d1 = DFA(states=self.states, start=q1, accepts=self.accepts, delta=self.delta, alphabet=self.alphabet)
        d2 = DFA(states=self.states, start=q2, accepts=self.accepts, delta=self.delta, alphabet=self.alphabet)
        sd_dfa = symmetric_difference(d1, d2)
        return sd_dfa.is_finite()

    def f_equivalence_classes(self):
        """Returns a partition of the states into finite-difference equivalence clases, using
        the experimental O(n^2) algorithm."""
        sd = symmetric_difference(self, self)
        self_pairs = [(x, x) for x in self.states]
        fd_equiv_pairs = sd.right_finite_states(self_pairs)
        sets = UnionFind()
        for state in self.states:
            sets.make_set(state)
        for (state1, state2) in fd_equiv_pairs:
            set1, set2 = sets.find(state1), sets.find(state2)
            if set1 != set2:
                sets.union(set1, set2)
        state_classes = sets.as_lists()
        return state_classes

    def hyper_minimize(self):
        """Alters the DFA into a smallest possible DFA recognizing a finitely different language.
        In other words, if D is the original DFA and D' the result of this function, then the 
        symmetric difference of L(D) and L(D') will be a finite set, and there exists no smaller
        automaton than D' with this property.

        See "The DFAs of Finitely Different Regular Languages" for context.
        """
        # Step 1: Classical minimization
        self.minimize()
        # Step 2: Partition states into equivalence classes
        state_classes = self.f_equivalence_classes()
        # Step 3: Find preamble and kernel parts
        (preamble, kernel) = self.preamble_and_kernel()
        # Step 4: Merge (f_merge_states in the paper)
        # (Could be done more efficiently)
        for sc in state_classes:
            pres = filter(lambda s: s in preamble, sc)
            kers = filter(lambda s: s in kernel, sc)
            if len(kers):
                rep = kers[0]
                for p_state in pres:
                    self.state_merge(p_state, rep)
            else:
                rep = pres[0]
                for p_state in pres[1:]:
                        self.state_merge(p_state, rep)

    def levels(self):
        """Returns a dictionary mapping each state to its distance from the starting state."""
        levels = {}
        seen = [self.start]
        levels[self.start] = 0
        level_number = 0
        level_states = [self.start]
        while len(level_states):
            next_level_states = []
            next_level_number = level_number + 1
            for q in level_states:
                for c in self.alphabet:
                    next = self.delta(q, c)
                    if next not in seen:
                        seen.append(next)
                        levels[next] = next_level_number
                        next_level_states.append(next)
            level_states = next_level_states
            level_number = next_level_number
        return levels

    def longest_word_length(self):
        """Given a DFA recognizing a finite language, returns the length of the
        longest word in that language, or None if the language is empty.
        Assumes the input is minimized.
        """
        assert(self.is_finite())
        def long_path(q,length, longest):
            if q in self.accepts:
                if length > longest:
                    longest = length
            for char in self.alphabet:
                next = self.delta(q, char)
                if next != q:
                    candidate = long_path(next, length+1, longest)
                    if candidate > longest:
                        longest = candidate
            return longest
        return long_path(self.start, 0, None)

    def DFCA_minimize(self, l=None):
        """DFCA minimization"
        Input: "self" is a DFA accepting a finite language
        Result: "self" is DFCA-minimized, and the returned value is the length of the longest
                word accepted by the original DFA

        See "Minimal cover-automata for finite languages" for context on DFCAs, and
        "An O(n^2) Algorithm for Constructing Minimal Cover Automata for Finite Languages"
        for the source of this algorithm (Campeanu, Paun, Santean, and Yu). We follow their
        algorithm exactly, except that "l" is optionally calculated for you, and the state-
        ordering is automatically created.
        
        There exists a faster, O(n*logn)-time algorithm due to Korner, from CIAA 2002.
        """

        assert(self.is_finite())

        self.minimize()

        ###Step 0: Numbering the states and computing "l"
        n = len(self.states) - 1
        state_order = self.pluck_leaves()
        if l==None:
            l = self.longest_word_length()
        #We're giving each state a numerical name so that the  algorithm can 
        # run on an "ordered" DFA -- see the paper for why. These functions
        # allow us to copiously convert between names.
        def nn(q): # "numerical name"
            return state_order.index(q)
        def rn(n): # "real name"
            return state_order[n]

        ###Step 1: Computing the gap function
        # 1.1 -- Step numbering is from the paper
        level = self.levels() #holds real names
        gap = {}  #holds numerical names
        # 1.2 
        for i in range(n):
            gap[(i, n)] = l
        if level[rn(n)] <= l:
            for q in self.accepts:
                gap[(nn(q), n)] = 0
        # 1.3
        for i in range(n-1):
            for j in range(i+1, n):
                if (rn(i) in self.accepts)^(rn(j) in self.accepts):
                    gap[(i,j)] = 0
                else:
                    gap[(i,j)] = l
        # 1.4
        def level_range(i, j):
            return l - max(level[rn(i)], level[rn(j)])
        for i in range(n-2, -1, -1):
            for j in range(n, i, -1):
                for char in self.alphabet:
                    i2 = nn(self.delta(rn(i), char))
                    j2 = nn(self.delta(rn(j), char))
                    if i2 != j2:
                        if i2 < j2:
                            g = gap[(i2, j2)]
                        else:
                            g = gap[(j2, i2)]
                        if g+1 <= level_range(i, j):
                            gap[(i,j)] = min(gap[(i,j)], g+1)

        ###Step 2: Merging states
        # 2.1
        P = {}
        for i in range(n+1):
            P[i] = False
        # 2.2
        for i in range(n):
            if P[i] == False:
                for j in range(i+1, n+1):
                    if (P[j] == False) and (gap[(i,j)] == l):
                        self.state_merge(rn(j), rn(i))
                        P[j] = True
        return l

#
# Boolean set operations on languages -- end of the DFA class
#

def cross_product(D1, D2, accept_method):
    """A generalized cross-product constructor over two DFAs. 
    The third argument is a binary boolean function f; a state (q1, q2) in the final
    DFA accepts if f(A[q1],A[q2]), where A indicates the acceptance-value of the state.
    """
    assert(D1.alphabet == D2.alphabet)
    states = []
    for s1 in D1.states:
        for s2 in D2.states:
            states.append((s1,s2))
    start = (D1.start, D2.start)
    def delta(state_pair, char):
        next_D1 = D1.delta(state_pair[0], char)
        next_D2 = D2.delta(state_pair[1], char)
        return (next_D1, next_D2)
    alphabet = copy(D1.alphabet)
    accepts = []
    for (s1, s2) in states:
        a1 = s1 in D1.accepts
        a2 = s2 in D2.accepts
        if accept_method(a1, a2):
            accepts.append((s1, s2))
    return DFA(states=states, start=start, delta=delta, accepts=accepts, alphabet=alphabet)

def intersection(D1, D2):
    """Constructs an unminimized DFA recognizing the intersection of the languages of two given DFAs."""
    f = bool.__and__
    return cross_product(D1, D2, f)

def union(D1, D2):
    """Constructs an unminimized DFA recognizing the union of the languages of two given DFAs."""
    f = bool.__or__
    return cross_product(D1, D2, f)

def symmetric_difference(D1, D2):
    """Constructs an unminimized DFA recognizing the symmetric difference of the languages of two given DFAs."""
    f = bool.__xor__
    return cross_product(D1, D2, f)

def inverse(D):
    """Constructs an unminimized DFA recognizing the inverse of the language of a given DFA."""
    new_accepts = []
    for state in D.states:
        if state not in D.accepts:
            new_accepts.append(state)
    return DFA(states=D.states, start=D.start, delta=D.delta, accepts=new_accepts, alphabet=D.alphabet)

# 
# Constructing new DFAs
# 

def from_word_list(language, alphabet):
    """Constructs an unminimized DFA accepting the given finite language."""
    accepts = language
    start = ''
    sink = 'sink'
    states = [start, sink]
    for word in language:
        for i in range(len(word)):
            prefix = word[:i+1]
            if prefix not in states:
                states.append(prefix)
    fwl = copy(states)
    def delta(q, c):
        next = q+c
        if next in fwl:
            return next
        else:
            return sink
    return DFA(states=states, alphabet=alphabet, delta=delta, start=start, accepts=accepts)

def modular_zero(n, base=2):
    """Returns a DFA that accepts all binary numbers equal to 0 mod n. Use the optional
    parameter "base" if you want something other than binary. The empty string is also 
    included in the DFA's language.
    """
    states = range(n)
    alphabet = map(str, range(base))
    delta = lambda q, c: ((q*base+int(c)) % n)
    start = 0
    accepts = [0]
    return DFA(states=states, alphabet=alphabet, delta=delta, start=start, accepts=accepts)

def random(states_size, alphabet_size, acceptance=0.5):
    """Constructs a random DFA with "states_size" states and "alphabet_size" inputs. Each 
    transition destination is chosen uniformly at random, so the resultant DFA may have 
    unreachable states. The optional "acceptance" parameter indicates what fraction of 
    the states should be accepting.
    """
    import random
    states = range(states_size)
    start = 0
    alphabet = range(alphabet_size)
    accepts = random.sample(states, int(acceptance*states_size))
    tt = {}
    for q in states:
        tt[q] = {}
        for c in alphabet:
            tt[q][c] = random.choice(states)
    delta = lambda q, c: tt[q][c]
    return DFA(states, alphabet, delta, start, accepts)

# 
# Finite-factoring
# 

def finite_factor(self):
    D1 = self.copy()
    D1.minimize()
    D2 = D1.copy()
    D2.hyper_minimize()
    D3 = symmetric_difference(D1, D2)
    l = D3.DFCA_minimize()
    return (D2, (D3, l))
