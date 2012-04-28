"""
Newer variant on crusoeparse, with an infusion of monoidal.py.
"""

import re

def Peg(x):
    if isinstance(x, (str, unicode)): return regex_parser(x)
    if callable(x):                   return thunk_parser(x)
    raise ValueError("Not coerceable to a peg", x)

def thunk_parser(thunk):

    def parse(s):
        for rule in thunk():
            result = parse_rule(rule, s)
            if result: return result
        return []

    def parse_rule(parts, s):
        vals, factors, act = [], parts[:-1], parts[-1]
        for factor in factors:
            for f_vals, s in Peg(factor)(s):
                vals.extend(f_vals)
                break
            else:
                return []
        rvals = () if act is ignore else (act(*vals),)
        return [(rvals, s)]

    return parse

def ignore(*vals): return ()

def regex_parser(regex):
    return lambda s: [(m.groups(), s[m.end():])
                      for m in [re.match(regex, s)] if m]

def complement(factor):
    return lambda: lambda s: [] if Peg(factor)(s) else [((), s)]


# Smoke test

def identity(x): return x

def a(): return [['(x)', b, 'y',   identity]]
def b(): return [['z',             ignore]]

## Peg(a)('xzyu')
#. [(('x',), 'u')]
