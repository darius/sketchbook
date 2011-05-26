"""
Solve a SAT problem by truth-table enumeration with pruning and unit
propagation. Sped up with an index from each variable to the clauses
using it.
"""

## solve([])
#. {}
## solve([[]])
## solve([[1]])
#. {1: True}
## solve([[1,-2], [2,-3], [1,3]])
#. {1: True, 2: False, 3: False}

import sat
from sat import assign

def solve(problem):
    "Return a satisfying assignment for problem, or None if impossible."
    env = {}
    if not sat.seems_consistent(problem, env):
        return None
    index = build_index(problem)
    return solving(problem, index, env,
                   sat.problem_variables(problem),
                   on_update(problem, env))

def build_index(problem):
    index = {}
    for clause in problem:
        for literal in clause:
            index.setdefault(abs(literal), []).append(clause)
    return index

def solving(problem, index, env, variables, unit_literals):
    "Try to extend a consistent assignment for problem to a satisfying one."
    if not variables:
        return env
    if unit_literals:
        literal, unit_literals = unit_literals[0], unit_literals[1:]
        v, value = abs(literal), (0 < literal)
        variables = removed(variables, v)
        env = assign(v, value, env)
        unit_literals = on_update(index.get(v, ()), env)
        if unit_literals is 'contradiction': return None
        return solving(problem, index, env, variables, unit_literals)
    v, variables = variables[0], variables[1:]
    for value in (False, True):
        env = assign(v, value, env)
        unit_literals = on_update(index.get(v, ()), env)
        if unit_literals is 'contradiction': continue
        result = solving(problem, index, env, variables, unit_literals)
        if result is not None:
            return result
    return None

def on_update(clauses, env):
    unit_literals = []
    for clause in clauses:
        unknown_literals = []
        for literal in clause:
            value = env.get(abs(literal))
            if value is None:
                unknown_literals.append(literal)
            elif value == (0 < literal):
                break                  # Clause is true
        else:
            if not unknown_literals:
                return 'contradiction' # Clause is false
            if len(unknown_literals) == 1:
                unit_literals.extend(unknown_literals)
    return unit_literals

def removed(xs, x):
    xs = list(xs)
    xs.remove(x)
    return xs
