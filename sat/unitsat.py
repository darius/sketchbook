"""
Solve a SAT problem by truth-table enumeration with pruning and unit
propagation.
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
    choice = choose_unit_literal(problem, env, variables)
    if choice is not None:
        v, value, variables = choice
        return solving(problem, assign(v, value, env), variables)
    v, variables = variables[0], variables[1:]
    for value in (False, True):
        result = solving(problem, assign(v, value, env), variables)
        if result is not None:
            return result
    return None

# Pre: sat.seems_consistent(problem, env)
def choose_unit_literal(problem, env, variables):
    for clause in problem:
        if clause_is_true(clause, env):
            continue
        unknown_literals = filter(lambda literal: abs(literal) not in env,
                                  clause)
        if len(unknown_literals) == 1:
            (literal,) = unknown_literals
            v, value = abs(literal), (0 < literal)
            return v, value, removed(variables, v)
    return None

def removed(xs, x):
    xs = list(xs)
    xs.remove(x)
    return xs

def clause_is_true(clause, env):
    return any(env.get(abs(literal)) == (0 < literal) for literal in clause)
