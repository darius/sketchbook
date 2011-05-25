"""
A SAT problem is a list of clauses. It's satisfied when all are true.

A clause is a list of literals. It's true when at least one is true.

A literal is a positive or negative integer denoting a variable
or its complement. Its truth depends on the environment.

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
