"""
Hand-compiled sample_rules from production.py, to explore
how it could go.
"""

from collections import deque

agenda = deque()

parents = []

def root(fact):
    if len(fact) == 3:
        if fact[0] == 'mom':
            agenda.append(['parent', fact[1], fact[2]])
        elif fact[0] == 'dad':
            agenda.append(['parent', fact[1], fact[2]])
        elif fact[0] == 'parent':
            parents.append(fact)
            for p in parents:
                if p[2] == fact[1]:
                    agenda.append(['grandparent', p[1], fact[2]])
