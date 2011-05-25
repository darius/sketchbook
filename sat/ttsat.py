"""
Solve a SAT problem by truth-table enumeration.
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
    variables = sat.problem_variables(problem)
    for env in gen_assignments(variables):
        if sat.seems_consistent(problem, env):
            return env
    return None

def gen_assignments(variables):
    if not variables:
        yield {}
    else:
        v, variables = variables[0], variables[1:]
        for env in gen_assignments(variables):
            yield assign(v, False, env)
            yield assign(v, True, env)
