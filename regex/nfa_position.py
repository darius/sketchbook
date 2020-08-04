"""
Position automata (or something -- not sure of the jargon).
This should produce automata equivalent to nfa_twostage.py's.
"""

from itertools import count

def match(re, s): return run(prepare(re), s)

def run((states, f), s):
    for c in s:
        states = set().union(*[f[state] for state in states if state[0] == c])
    return (None, 1) in states  # (None, 1) is the accepting state (a hack)

# re: (n: nullable, a: first, z: last, f: follows)

def prepare(re):
    n, a, z, f = seq(re, accepting)
    return a, f

empty = (True, set(), set(), {})

p = count(1)
def lit(c):
    cp = set([(c, next(p))])
    return (False, cp, cp, {})

def alt((n1, a1, z1, f1), (n2, a2, z2, f2)):
    return (n1 or n2, a1 | a2, z1 | z2, union(f1, f2))

def seq((n1, a1, z1, f1), (n2, a2, z2, f2)):
    return (n1 and n2,
            a1 | (a2 if n1 else set()),
            (z1 if n2 else set()) | z2,
            union(union(f1, f2), cross(z1, a2)))

def many((n, a, z, f)):
    return (True, a, z, union(f, cross(z, a)))

def union(d1, d2):
    return dict((x, d1.get(x, set()) | d2.get(x, set()))
                for x in set(d1.keys()) | set(d2.keys()))

def cross(xs, ys):
    return dict((x, ys) for x in xs)

accepting = lit(None)

## re = alt(seq(lit('A'), lit('C')), seq(lit('B'), lit('C')))
## prepare(re)
#. (set([('B', 4), ('A', 2)]), {('B', 4): set([('C', 5)]), ('C', 5): set([(None, 1)]), ('C', 3): set([(None, 1)]), ('A', 2): set([('C', 3)])})

## accepting
#. (False, set([(None, 1)]), set([(None, 1)]), {})

## match(many(seq(lit('a'), many(empty))), 'aa')
#. True

## match(empty, '')
#. True
## match(empty, 'A')
#. False
## match(lit('x'), '')
#. False
## match(lit('x'), 'y')
#. False
## match(lit('x'), 'x')
#. True
## match(lit('x'), 'xx')
#. False
## match(seq(lit('a'), lit('b')), '')
#. False
## match(seq(lit('a'), lit('b')), 'ab')
#. True
## match(alt(lit('a'), lit('b')), 'b')
#. True
## match(alt(lit('a'), lit('b')), 'a')
#. True
## match(alt(lit('a'), lit('b')), 'x')
#. False
## match(many(lit('a')), '')
#. True
## match(many(lit('a')), 'a')
#. True
## match(many(lit('a')), 'x')
#. False
## match(many(lit('a')), 'aa')
#. True
## match(many(lit('a')), 'ax')
#. False

## complicated = seq(many(alt(seq(lit('a'), lit('b')), seq(lit('a'), seq(lit('x'), lit('y'))))), lit('z'))
## match(complicated, '')
#. False
## match(complicated, 'z')
#. True
## match(complicated, 'abz')
#. True
## match(complicated, 'ababaxyab')
#. False
## match(complicated, 'ababaxyabz')
#. True
## match(complicated, 'ababaxyaxz')
#. False

# originally had infinite recursion, like Thompson's original code:
## match(many(many(lit('x'))), 'xxxx')
#. True
## match(many(many(lit('x'))), 'xxxxy')
#. False

# Had a bug: empty forced a match regardless of the continuation.
## match(seq(empty, lit('x')), '')
#. False
## match(seq(empty, lit('x')), 'x')
#. True
