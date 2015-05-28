"""
Parsing context-free grammars using Brzozowski derivatives.
First cut -- left recursion not considered. Maybe it'll work anyway?
"""

# A grammar is a map from rule name to list of states; it must
# include a rule named 'start'. A rule derives s if any of its states 
# derives s.

# A state is a tuple of elements. It derives s if some concatenation
# of its elements' derivations (in order) equals s.

# An element is a rule name or a single literal character.

def grammar_check(grammar):
    "Check the grammar representation invariant."
    assert 'start' in grammar
    for states in grammar.values():
        for state in states:
            for element in state:
                assert isinstance(element, str)
                assert element in grammar or len(element) == 1

def parse(grammar, s):
    "Can grammar derive string s?"
    grammar_check(grammar)
    states = set(grammar['start'])
#    print
    for c in s:
        states = step(grammar, states, c)
#        print repr(c)
#        for state in states: print '   ', state
        if not states: return False
    return any_null(grammar, states, set())

def any_null(grammar, states, visited):
    return any(nullable(grammar, state, visited) for state in states)

def nullable(grammar, state, visited):
    "Can state derive the empty string?"
    if not state: return True
    if state in visited: return False
    visited.add(state)
    return all(element in grammar
               and any_null(grammar, grammar[element], visited)
               for element in state)

lefty = dict(start = [('start', 'x'), ()])

## nullable(lefty, ('start',), set())
#. True

def step(grammar, states, c):
    """Of the sentences starting with c derivable by any of states,
    consider their tails after the c. Return a set of states that
    derives just these tails."""
    visited, next_states = set(), set()
    while states:
        state = states.pop()
        if not state: continue
        visited.add(state)
        head, tail = state[0], state[1:]
        if head not in grammar: # leading literal
            if c == head: next_states.add(tail)
        else:
            for rhs in grammar[head]:
                expanded = rhs + tail
                if expanded not in visited: states.add(expanded)
    return next_states

ruling = dict(start = [('rule',)],
              rule  = [('x',)])

## parse(ruling, '')
#. False
## parse(ruling, 'x')
#. True

xstar = dict(start = [('x', 'start'),
                      () ])

## parse(xstar, '')
#. True
## parse(xstar, 'x')
#. True
## parse(xstar, 'xx')
#. True
## parse(xstar, 'xxy')
#. False

intgrammar = dict(start = [('int',)],
                  int   = [('-', 'uint'),
                           ('+', 'uint'),
                           ('uint',)],
                  uint  = [('digit', 'uint'),
                           ('digit',)],
                  digit = map(tuple, '0123456789'))

## parse(intgrammar, '-42')
#. True

sub = dict(start = [('E',)],
           E =     [('E', '-', 'T'),
                    ('T',)])

### parse(sub, 'T-T-T')

empty = dict(start = [()])

## parse(empty, '')
#. True
## parse(empty, 'x')
#. False

xgrammar = dict(start = [('x',)])

## parse(xgrammar, '')
#. False
## parse(xgrammar, 'x')
#. True

xy = dict(start = [('x', 'y')])

## parse(xy, '')
#. False
## parse(xy, 'x')
#. False
## parse(xy, 'xy')
#. True
## parse(xy, 'xyz')
#. False

xopt = dict(start = [('x',),
                     () ])

## parse(xopt, '')
#. True
## parse(xopt, 'x')
#. True
## parse(xopt, 'xx')
#. False

bal = dict(start = [('(', 'cs', ')')],
           cs = [('c', 'cs'),
                 ()],
           c = [('.',),
                ('start',)])

## parse(bal, '((())..(.))')
#. True

"""
<napping> Are you trying to construct a graph for each derivative, or just ignoring left-recursion entirely?
<napping> because you can definitely get infinite cycles of contexts
<napping> and then recognizing and sharing those through some kind of memoization or whatever is one of the things GLL does to get general parsing
<napping> but, those epsilon transitions themselves should form a finite graph/regular paths
<napping> so if you want you can probably generate some kind of regex representation of an infinite family of current states
<napping> I wonder how those sets might be related to the LR table stuff?
<darius> maybe if you took the right derivative instead of the left?
<darius> (might be a completely bogus thought)
<napping> I'm pretty sure that's completely different from LR, but might be interesting
<napping> Brozozowski got some kind of minimization from reversing DFAs, right?
<darius> yes
<napping> Ah, the other thing I was thinking of was that in a traditional deterministic LR parser you can also calculate a regular expression for what the stack can possibly look like when you are in a particular state (this time not restricting to epislon edges)
<napping> Doing the context like that is probably just a different way to represent the graph structured stack, but you might noticed something interesting that way
"""
