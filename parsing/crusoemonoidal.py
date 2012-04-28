"""
Newer variant on crusoeparse, with an infusion of monoidal.py.
"""

import re

def parse(x, s):
#    print 'parse', x, s
    p = x() if callable(x) else x
    if isinstance(p, (str, unicode)): return parse_regex(p, s)
    if isinstance(p, list):           return parse_rules(p, s)
    if callable(p):                   return p(s)
    raise ValueError("Not coerceable to a peg", x)

def parse_rules(rules, s):

    def parse_rule(rule, s):
        vals, peggables, act = [], rule[:-1], rule[-1]
        for p in peggables:
            p_vals, s = parse(p, s)
            if s is None: return (), None
            vals.extend(p_vals)
        r_vals = () if act is ignore else (act(*vals),)
        return r_vals, s

    for rule in rules:
        vals, s1 = parse_rule(rule, s)
        if s1 is not None: return vals, s1
    return (), None

def ignore(*vals): return ()

def parse_regex(regex, s):
    m = re.match(regex, s)
    return (m.groups(), s[m.end():]) if m else ((), None)

def complement(peggable):
    return lambda: lambda s: (((), s) if parse(peggable, s)[1] is None
                              else ((), None)


# Smoke test

def identity(x): return x

def a(): return [['(x)', c, 'y',         identity]]
def b(): return [['z',                   ignore]]
def c(): return [[complement('z'), '.',  ignore]]

## parse('x', 'y')
#. ((), None)
## parse(complement('x'), 'y')
#. ((), 'y')

## parse(a, 'xayu')
#. (('x',), 'u')
## parse(a, 'xzyu')
#. ((), None)
