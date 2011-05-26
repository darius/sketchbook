"""
Solve a SAT problem by pruned truth-table enumeration.
Index clasuse by a single watched literal, to cheaply
detect contradiction.
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
    return solving(build_index(problem), {}, sat.problem_variables(problem))

def build_index(problem):
    index = {}
    for clause in problem:
        if not clause: return 'contradiction'
        watch(index, clause, clause[0])
    return index

def watch(index, clause, literal):
    index.setdefault(-literal, []).append(clause)

def solving(index, env, variables):
    "Try to extend a consistent assignment for problem to a satisfying one."
    if index is 'contradiction':
        return None
    if not variables:
        return env
    v, variables = variables[0], variables[1:]
    for value in (False, True):
        new_env = assign(v, value, env)
        result = solving(on_update(index, new_env, v if value else -v),
                         new_env, variables)
        if result is not None:
            return result
    return None

def on_update(index, env, new_literal):
    new_index = dict(index)
    for clause in index.get(new_literal, ()):
        for literal in clause:
            value = env.get(abs(literal))
            if value is None:
                watch(new_index, clause, literal)
                break
            elif value == (0 < literal):
                break                  # Clause is true
        else:
            return 'contradiction'
    return new_index
