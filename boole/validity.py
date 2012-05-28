"""
Propositional validity checker.
Crunched down from boole.py.
Suggested by reading http://www.ps.uni-sb.de/~duchier/python/validity.py
and https://gist.github.com/2789099
"""

def is_valid(expr): return satisfy(expr, 0) == False

def satisfy(expr, value):
    return expr(value, Env(), lambda env: env)

class Env(dict):
    def extend(self, var, value):
        result = Env(self)
        result[var] = value
        return result

def Literal(x):
    return lambda value, env, succeed: x == value and succeed(env)

zero, one = Literal(0), Literal(1)

def Variable(name):
    return lambda value, env, succeed: (
        Literal(env[name])(value, env, succeed) if name in env 
        else succeed(env.extend(name, value)))

def Choice(test, if_zero, if_one):
    return lambda value, env, succeed: (
           test(0, env, lambda env: if_zero(value, env, succeed))
        or test(1, env, lambda env: if_one(value, env, succeed)))

def and_(x, y): return Choice(x, zero, y)
def or_(x, y):  return Choice(x, y, one)
def not_(x):    return Choice(x, one, zero)
def impl(x, y): return Choice(x, one, y)

## x, y = map(Variable, 'x y'.split())
## is_valid(zero), is_valid(one), is_valid(x)
#. (False, True, False)

## satisfy(zero, 0)
#. {}
## satisfy(zero, 1)
#. False

## satisfy(x, 1)
#. {'x': 1}
## satisfy(not_(x), 1)
#. {'x': 0}
## satisfy(and_(x, x), 1)
#. {'x': 1}
## satisfy(and_(x, not_(x)), 1)
#. False

## is_valid(impl(impl(impl(x, y), x), x))
#. True
## is_valid(impl(impl(impl(x, y), x), y))
#. False
