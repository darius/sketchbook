"""
Parsing context-free grammars using Brzozowski derivatives.
First cut -- left recursion not considered. Maybe it'll work anyway?
"""

def parse(grammar, s):
    states = set(grammar['start'])
    for c in s:
        states = step(grammar, states, c)
        if not states: return False
    return any(nullable(grammar, state) for state in states)

def nullable(grammar, state):
    if not state: return True
    head = state[0]
    # XXX can loop:
    return (head in grammar
            and any(nullable(grammar, rhs) for rhs in grammar[head]))

def step(grammar, states, c):
    visited, next_states = set(), set()
    while states:
        state = states.pop()
        if not state: continue
        visited.add(state)
        head, tail = state[0], state[1:]
        if head not in grammar: # leading literal
            assert len(head) == 1
            if c == head: next_states.add(state[1:])
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
