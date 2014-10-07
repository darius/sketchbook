"""
Propositional validity checker.
Crunched down from boole.py.
Suggested by reading http://www.ps.uni-sb.de/~duchier/python/validity.py
and https://gist.github.com/2789099
"""

def is_valid(expr):      return not satisfy(expr, 0)
def satisfy(expr, goal): return expr(goal, {None:None}, lambda env: env)

def Constant(value):
    return lambda goal, env, succeed: (
        value == goal and succeed(env))

def Variable(name):
    return lambda goal, env, succeed: (
        env[name] == goal and succeed(env) if name in env
        else succeed(extend(env, name, goal)))

def Choice(test, if0, if1):
    return lambda goal, env, succeed: (
           test(0, env, lambda env: if0(goal, env, succeed))
        or test(1, env, lambda env: if1(goal, env, succeed)))

def extend(env, var, value):
    result = dict(env)
    result[var] = value
    return result

zero, one = Constant(0), Constant(1)

def and_(x, y): return Choice(x, zero, y)
def or_(x, y):  return Choice(x, y, one)
def not_(x):    return Choice(x, one, zero)
def impl(x, y): return Choice(x, one, y)    # 'x implies y'

## x, y = map(Variable, 'x y'.split())
## is_valid(zero), is_valid(one), is_valid(x)
#. (False, True, False)

# This had a bug before we added the ugly {None:None}:
## satisfy(not_(zero), 1)
#. {None: None}

## satisfy(zero, 0)
#. {None: None}
## satisfy(zero, 1)
#. False

## satisfy(x, 1)
#. {'x': 1, None: None}
## satisfy(not_(x), 1)
#. {'x': 0, None: None}
## satisfy(and_(x, x), 1)
#. {'x': 1, None: None}
## satisfy(and_(x, not_(x)), 1)
#. False

## is_valid(impl(impl(impl(x, y), x), x))
#. True
## is_valid(impl(impl(impl(x, y), x), y))
#. False

"""
Here's the idea:

Consider the logical expression `if x then y else z` (represented here
as Choice(x, z, y), equivalent to (x and y) or (not x and z)). Say
you're out to find a way it can be false (represented here as
0). Well, there might be two ways: if x is true and y is false, or if
x is false and z is false. So recursively look at each of those two
possibilities, and return the first way that works, if any.

http://en.wikipedia.org/wiki/Method_of_analytic_tableaux is a
graphical pen-and-paper version of that search, but with more cases to
consider (which I unify by reducing the connectives to Choice).

The usual tableau method over AND, OR, etc. has an advantage: you
get a choice of which subexpression to expand next, which can make for
smaller search trees if you're smart. (This corresponds to choosing
an advantageous expansion into if-then-else expressions, as in
validity_smallerfirst.py, only that's more static.)
"""
