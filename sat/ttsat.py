"""
Solve a SAT problem by truth-table enumeration.

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
    for env in gen_assignments(variables):
        if problem_is_consistent(problem, env):
            return env
    return None

def problem_variables(problem):
    return sorted(set(abs(literal) for clause in problem for literal in clause))

def gen_assignments(variables):
    if not variables:
        yield {}
    else:
        v, variables = variables[0], variables[1:]
        for env in gen_assignments(variables):
            yield assign(v, False, env)
            yield assign(v, True, env)

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
