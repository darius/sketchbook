"""
Solve a SAT problem by pruned truth-table enumeration.
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
    return solving(problem, {}, variables)

def solving(problem, env, variables):
    "Try to extend a consistent assignment for problem to a satisfying one."
    if not sat.seems_consistent(problem, env):
        return None
    if not variables:
        return env
    v, variables = variables[0], variables[1:]
    for value in (False, True):
        result = solving(problem, assign(v, value, env), variables)
        if result is not None:
            return result
    return None
