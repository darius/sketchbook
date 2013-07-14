"""
Parsing context-free grammars using Brzozowski derivatives.
First cut -- left recursion not considered. Maybe it'll work anyway?
"""

# (I think:)

# A grammar is a map from rule name to list of states; it must
# include a rule named 'start'. A rule derives s if any of its states 
# derives s.

# A state is a tuple of elements. It derives s if some concatenation
# of its elements' derivations (in order) equals s.

# An element is a rule name or a single literal character.

def parse(grammar, s):
    "Can grammar derive s?"
    states = set(grammar['start'])
    for c in s:
        states = step(grammar, states, c)
        if not states: return False
    return nullable_choice(grammar, states, set())

def nullable_choice(grammar, states, visited):
    return any(nullable(grammar, state, visited) for state in states)

def nullable(grammar, state, visited):
    "Can state derive the empty string?"
    if not state: return True
    if state in visited: return False
    visited.add(state)
    head = state[0]
    return head in grammar and nullable_choice(grammar, grammar[head], visited)

lefty = dict(start = [('start', 'x'), ()])

## nullable(lefty, ('start',), set())
#. True

def step(grammar, states, c):
    """Let's say states produces the language L. Of the sentences in L that 
    start with c, consider their tails. Return a set of states that produces
    just these tails."""
    visited, next_states = set(), set()
    while states:
        state = states.pop()
        if not state: continue
        visited.add(state)
        head, tail = state[0], state[1:]
        if head not in grammar: # leading literal
            assert len(head) == 1
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
