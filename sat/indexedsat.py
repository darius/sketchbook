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
    index = build_index(problem)
    return solving(index, env,
                   sat.problem_variables(problem),
                   on_update(problem, env, []))

def build_index(problem):
    index = {}
    for clause in problem:
        for literal in clause:
            index.setdefault(-literal, []).append(clause)
    return index

def solving(index, env, variables, unit_literals):
    "Try to extend a consistent assignment for problem to a satisfying one."
    if unit_literals is 'contradiction':
        return None
    if not variables:
        return env
    if unit_literals:
        literal, unit_literals = unit_literals[0], unit_literals[1:]
        v, value = abs(literal), (0 < literal)
        variables = removed(variables, v)
        return assume(index, env, variables, unit_literals, v, value)
    v, variables = variables[0], variables[1:]
    for value in (False, True):
        result = assume(index, env, variables, unit_literals, v, value)
        if result is not None:
            return result
    return None

def assume(index, env, variables, unit_literals, v, value):
    env = assign(v, value, env)
    return solving(index, env, variables,
                   on_update(index.get(v if value else -v, ()),
                             env, unit_literals))

def on_update(clauses, env, unit_literals):
    new_unit_literals = []
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
            if (len(unknown_literals) == 1
                and unknown_literals[0] not in unit_literals):
                new_unit_literals.extend(unknown_literals)
    return unit_literals + new_unit_literals

def removed(xs, x):
    xs = list(xs)
    xs.remove(x)
    return xs
