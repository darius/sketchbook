"""
Parsing context-free grammars using Brzozowski derivatives.
First cut -- left recursion not considered.
This looks suspiciously like Earley.
"""

# A grammar is a map from rule name to list of chains; it must
# include a rule named 'start'. A rule derives s if any of its chains 
# derives s.

# A chain is a tuple of elements. It derives s if some concatenation
# of its elements' derivations (in order) equals s.

# An element is one of
#  ('push', rule_name)
#  ('pop', rule_name)
#  ('shift', character)
# In the initial grammar no pops may appear.

def Push(name): return 'push', name
def Pop(name):  return 'pop', name
def Shift(ch):  return 'shift', ch

def Grammar(**kwargs):
    return dict((name, [tuple(Push(x) if x in kwargs else Shift(x)
                              for x in chain)
                        for chain in chains])
                for name, chains in kwargs.items())

def grammar_check(grammar):
    "Check the grammar representation invariant."
    assert 'start' in grammar
    for chains in grammar.values():
        for chain in chains:
            for element in chain:
                assert isinstance(element, tuple) and len(element) == 2
                tag, x = element
                if tag == 'push':
                    assert x in grammar
                elif tag == 'shift':
                    assert isinstance(x, str) and len(x) == 1
                else:
                    assert False

# A state is a pair (parsed, chain) where parsed is a tuple of tuples
# of parse subtrees.

def parse(grammar, s):
    "Can grammar derive string s?"
    grammar_check(grammar)
    states = set([(((),), (Push('start'),))])
#    print
    for c in s:
        states = step(grammar, states, c)
#        print repr(c)
#        for state in states: print '   ', state
        if not states: return []
    return filter_null(grammar, states, ())

def filter_null(grammar, states, visiting):
    return sum((nullify(grammar, state, visiting) for state in states), [])

def nullify(grammar, state, visiting):
    """Return a list of results: each is the parsed part of reduced(state)
    if state can derive the empty string."""
    parsed, chain = state = reduced(state)
    if not chain: return [parsed]
    (tag, x), tail = chain[0], chain[1:]
    if tag == 'push':
        if x in visiting:
            return [] # Stifle loops. (Why am I bothering when I don't handle left recursion elsewhere?)
        states = [(parsed + ((),), head_chain + (Pop(x),) + tail)
                  for head_chain in grammar[x]]
        return filter_null(grammar, states, visiting + (x,))
    elif tag == 'shift':
        return []
    else:
        assert False

def step(grammar, states, c):
    """Of the sentences starting with c derivable by any of states,
    consider their tails after the c. Return a set of states that
    derives just these tails."""
    visited, next_states = set(), set()
    while states:
        state = states.pop()
        visited.add(state)
        parsed, chain = reduced(state)
        if not chain: continue
        (tag, head), tail = chain[0], chain[1:]
        if tag == 'shift':
            if c == head:
                next_states.add((parsed[:-1] + (parsed[-1] + (c,),), tail))
        else:
            for rhs in grammar[head]:
                expanded = parsed + ((),), rhs + (Pop(head),) + tail
                if expanded not in visited:
                    states.add(expanded)
    return next_states

def reduced(state):
    parsed, chain = state
    while chain and chain[0][0] == 'pop':
        parsed = parsed[:-2] + ((parsed[-2] + ((chain[0][1], parsed[-1]),)),)
        chain = chain[1:]
    return parsed, chain

ruling = Grammar(start = [('rule',)],
                 rule  = [('x',)])

## parse(ruling, '')
#. []
## parse(ruling, 'x')
#. [((('start', (('rule', ('x',)),)),),)]

xstar = Grammar(start = [('x', 'start'),
                         () ])

## parse(xstar, '')
#. [((('start', ()),),)]
## parse(xstar, 'x')
#. [((('start', ('x', ('start', ()))),),)]
## parse(xstar, 'xx')
#. [((('start', ('x', ('start', ('x', ('start', ()))))),),)]
## parse(xstar, 'xxy')
#. []

intgrammar = Grammar(start = [('int',)],
                     int   = [('-', 'uint'),
                              ('+', 'uint'),
                              ('uint',)],
                     uint  = [('digit', 'uint'),
                              ('digit',)],
                     digit = map(tuple, '0123456789'))

## parse(intgrammar, '-42')
#. [((('start', (('int', ('-', ('uint', (('digit', ('4',)), ('uint', (('digit', ('2',)),)))))),)),),)]

sub = Grammar(start = [('E',)],
              E =     [('E', '-', 'T'),
                       ('T',)])

### parse(sub, 'T-T-T')

empty = Grammar(start = [()])

## parse(empty, '')
#. [((('start', ()),),)]
## parse(empty, 'x')
#. []

xgrammar = Grammar(start = [('x',)])

## parse(xgrammar, '')
#. []
## parse(xgrammar, 'x')
#. [((('start', ('x',)),),)]

xy = Grammar(start = [('x', 'y')])

## parse(xy, '')
#. []
## parse(xy, 'x')
#. []
## parse(xy, 'xy')
#. [((('start', ('x', 'y')),),)]
## parse(xy, 'xyz')
#. []

xopt = Grammar(start = [('x',),
                        () ])

## parse(xopt, '')
#. [((('start', ()),),)]
## parse(xopt, 'x')
#. [((('start', ('x',)),),)]
## parse(xopt, 'xx')
#. []

bal = Grammar(start = [('(', 'cs', ')')],
              cs = [('c', 'cs'),
                    ()],
              c = [('.',),
                   ('start',)])

## parse(bal, '((())..(.))')
#. [((('start', ('(', ('cs', (('c', (('start', ('(', ('cs', (('c', (('start', ('(', ('cs', ()), ')')),)), ('cs', ()))), ')')),)), ('cs', (('c', ('.',)), ('cs', (('c', ('.',)), ('cs', (('c', (('start', ('(', ('cs', (('c', ('.',)), ('cs', ()))), ')')),)), ('cs', ()))))))))), ')')),),)]
## parse(bal, '()')
#. [((('start', ('(', ('cs', ()), ')')),),)]
