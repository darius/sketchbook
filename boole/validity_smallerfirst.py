"""
Propositional validity checker.
From validity.py but hopefully faster. (I haven't benchmarked it.)
For AND and OR we test the simpler argument first.
In the original code we always went left to right instead.
"""

def is_valid(expr):      return not satisfy(expr, 0)
def satisfy(expr, goal): return expr(goal, {None:None}, lambda env: env)

def make(size, fn):
    fn.size = size
    return fn

def Literal(value):
    return make(1, lambda goal, env, succeed: (
        value == goal and succeed(env)))

def Variable(name):
    return make(1, lambda goal, env, succeed: (
        env[name] == goal and succeed(env) if name in env
        else succeed(extend(env, name, goal))))

def Choice(test, if0, if1):
    return make(test.size + if0.size + if1.size,
                lambda goal, env, succeed: (
           test(0, env, lambda env: if0(goal, env, succeed))
        or test(1, env, lambda env: if1(goal, env, succeed))))

def extend(env, var, value):
    result = dict(env)
    result[var] = value
    return result

zero, one = Literal(0), Literal(1)

def and_(x, y): return Choice(x, zero, y) if x.size <= y.size else and_(y, x)
def or_(x, y):  return Choice(x, y, one)  if x.size <= y.size else or_ (y, x)
def not_(x):    return Choice(x, one, zero)
def impl(x, y): return Choice(x, one, y)

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
