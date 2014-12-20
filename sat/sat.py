"""
A SAT problem is a list of clauses. It's satisfied when all are true.

A clause is a list of literals. It's true when at least one is true.

A literal is a nonzero integer denoting a variable (if positive) or
its complement (if negative). Its truth depends on the environment.

An environment is a partial map from positive integer to boolean.
"""

def problem_variables(problem):
    return sorted(set(abs(literal) for clause in problem for literal in clause))

def assign(variable, value, env):
    env = dict(env)
    env[variable] = value
    return env

def is_satisfied(problem, env):
    return all(any(env.get(abs(literal)) == (0 < literal)
                   for literal in clause)
               for clause in problem)

def seems_consistent(problem, env):
    return all(any(env.get(abs(literal), 0 < literal) == (0 < literal)
                   for literal in clause)
               for clause in problem)


# Constraint constructors

def at_least_one(literals):
    return [literals]

def at_most_one(literals):
    return [[-literals[j], -xi]
            for i, xi in enumerate(literals)
            for j in range(i)]

## at_most_one([9, 5, 1])
#. [[-9, -5], [-9, -1], [-5, -1]]

def exactly_one(literals):
    return at_least_one(literals) + at_most_one(literals)

## exactly_one([9, 5, 1])
#. [[9, 5, 1], [-9, -5], [-9, -1], [-5, -1]]

def not_all(literals):
    return [[-v for v in literals]]

## not_all([9, 5, 1])
#. [[-9, -5, -1]]


# Problem constructor

def conjoin(*problems):
    return flatten(problems)

def flatten(xss):
    result = []
    for xs in xss:
        result.extend(xs)
    return result
