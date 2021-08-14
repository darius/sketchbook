"""
Trying to cut down the code to the essence of Parson, to explain it.
"""

# Glossary:
# p, q, r: parsers
# s, nub: input string, or the remaining suffix thereof


# Basic parsers
# Take an s, and return a list of nubs. The list will have length 0 or 1.

def literal(lit):    # Match lit
    return lambda s: [s[len(lit):]] if s.startswith(lit) else []

def then(p, q):      # Match p, then match q, consecutively
    return lambda s: [nub2
                      for nub1 in p(s)
                      for nub2 in q(nub1)]

def either(p, q):
    return lambda s: p(s) or q(s)

def nix(p):
    return lambda s: [] if p(s) else [s]

# Derived parsers

empty = literal('')

def peek(p): return nix(nix(p))

def maybe(p): return either(p, empty)



# Smoke test

## literal('abc')('abc')
#. ['']
## literal('abc')('abd')
#. []
