"""
Solve a SAT problem by pruned truth-table enumeration.
Like watch1sat, but more imperative.
"""

## solve([])
#. {}
## solve([[]])
## solve([[1]])
#. {1: True}
## solve([[1,-2], [2,-3], [1,3]])
#. {1: True, 2: False, 3: False}
#X {1: True, 2: False, 3: False}
## solve([[1,-2], [1,2]])
#. {1: True, 2: False}

import sat
from sat import assign

def solve(problem):
    "Return a satisfying assignment for problem, or None if impossible."
    global index, model
    index, model = {}, {}
    if not make_index(problem): return None
    return model if solving(sat.problem_variables(problem)) else None

def solving(variables):
    "Try to extend a consistent assignment for problem to a satisfying one."
    if not variables:
        return True
    v, variables = variables[0], variables[1:]
    if update(v, False):
        if solving(variables): return True
    if update(v, True):
        if solving(variables): return True
        del model[v]
    return False

# Inv: each nonempty clause in problem is indexed under exactly one of
# its literals. That literal is either True or unknown in model.
index = None
model = None

def make_index(problem):
    for clause in problem:
        if clause: watch(clause, clause[0])
        else:      return False
    return True

def watch(clause, literal):
    index.setdefault(literal, []).append(clause)

def update(v, value):
    model[v] = value
    new_literal = (v if value else -v)
    clauses = index.get(-new_literal, ())
    for clause in clauses[:]:
        for literal in clause:
            value = model.get(abs(literal))
            if value is None or value == (0 < literal):
                clauses.remove(clause)
                watch(clause, literal)
                break
        else:
            del model[v]
            return False
    return True
