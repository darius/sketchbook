"""
Solve a SAT problem by pruned truth-table enumeration.

A problem is a list of clauses. It's satisfied when all are true.

A clause is a list of literals. It's true when at least one is true.

A literal is a positive or negative integer denoting a variable
or its complement. Its truth depends on the environment.
"""

## solve([])
#. {}
## solve([[]])
## solve([[1]])
#. {1: True}
## solve([[1,-2], [2,-3], [1,3]])
#. {1: True, 2: False, 3: False}

def solve(problem):
    "Return a satisfying assignment for problem, or None if impossible."
    variables = problem_variables(problem)
    return solving(problem, {}, variables)

def problem_variables(problem):
    return sorted(set(abs(literal) for clause in problem for literal in clause))

def solving(problem, env, variables):
    "Try to extend a consistent assignment for problem to a satisfying one."
    if not problem_is_consistent(problem, env):
        return None
    if not variables:
        return env
    v, variables = variables[0], variables[1:]
    for value in (False, True):
        result = solving(problem, assign(v, value, env), variables)
        if result is not None:
            return result
    return None

def assign(variable, value, env):
    env = dict(env)
    env[variable] = value
    return env

def problem_is_consistent(problem, env):
    return all(clause_is_consistent(clause, env) for clause in problem)

def clause_is_consistent(clause, env):
    return any(literal_is_consistent(literal, env) for literal in clause)

def literal_is_consistent(literal, env):
    var = abs(literal)
    sign = (var == literal)
    return env.get(var, sign) == sign
