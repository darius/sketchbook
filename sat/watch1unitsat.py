"""
Solve a SAT problem by pruned truth-table enumeration. Index clauses
by a single watched literal, to cheaply detect contradiction. When we
notice a unit clause along the way, we take advantage.
"""

## solve([])
#. {}
## solve([[]])
## solve([[1]])
#. {1: True}
## solve([[1], [-1]])
## solve([[1,-2], [1,2]])
#. {1: True, 2: False}
## solve([[1,-2], [2,-3], [1,3]])
#. {1: True, 2: False, 3: False}

import sat
from sat import assign

def solve(problem):
    "Return a satisfying assignment for problem, or None if impossible."
    index, unit_literals = build_index(problem)
    if index == 'contradiction': return None
    return solving(index, {}, sat.problem_variables(problem), unit_literals)

def solving(index, env, variables, unit_literals):
    "Try to extend a consistent assignment for problem to a satisfying one."
    if unit_literals == 'contradiction':
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
                   on_update(index, v if value else -v, env, unit_literals))

def build_index(problem):
    index, unit_literals = {}, []
    for clause in problem:
        if not clause: return 'contradiction', []
        watch(index, clause, clause[0])
        if len(clause) == 1 and clause[0] not in unit_literals:
            unit_literals.extend(clause)
    return index, unit_literals

def on_update(index, literal, env, unit_literals):
    clauses = index.get(literal, ())
    unit_literals = unit_literals[:]
    for clause in clauses[:]:
        unknown_literals = []
        for literal in clause:
            value = env.get(abs(literal))
            if value is None:
                unknown_literals.append(literal)
            elif value == (0 < literal):
                clauses.remove(clause)
                watch(index, clause, literal)
                break                  # Clause is true
        else:
            if not unknown_literals:
                return 'contradiction' # Clause is false
            clauses.remove(clause)
            watch(index, clause, unknown_literals[0])
            if (len(unknown_literals) == 1
                and unknown_literals[0] not in unit_literals):
                unit_literals.extend(unknown_literals)
    return unit_literals

def watch(index, clause, literal):
    index.setdefault(-literal, []).append(clause)

def removed(xs, x):
    xs = list(xs)
    xs.remove(x)
    return xs
