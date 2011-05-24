"""
Solve a SAT problem by truth-table enumeration with pruning and unit
propagation.

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

# Pre: problem_is_consistent(problem, env)
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

def assign(variable, value, env):
    env = dict(env)
    env[variable] = value
    return env

# A misnomer. Return true iff problem in env is not obviously inconsistent.
def problem_is_consistent(problem, env):
    return all(clause_is_consistent(clause, env) for clause in problem)

def clause_is_consistent(clause, env):
    return any(literal_is_consistent(literal, env) for literal in clause)

def literal_is_consistent(literal, env):
    var = abs(literal)
    sign = (var == literal)
    return env.get(var, sign) == sign

def clause_is_true(clause, env):
    return any(literal_is_true(literal, env) for literal in clause)

def literal_is_true(literal, env):
    var = abs(literal)
    sign = (var == literal)
    return env.get(var, None) == sign
