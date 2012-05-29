"""
Iterative version of validity.py
Concrete representation of expressions:
   bool: constant
   str:  variable
   tuple (test_expr, if_true_expr, if_false_expr): if-then-else
"""

isa = isinstance

def is_valid(expr): return satisfy(expr, 0) == False

class Env(dict):
    def extend(self, var, value):
        result = Env(self)
        result[var] = value
        return result

def satisfy(expr, value):
    env = Env()
    fail, succeed = [], []
    while True:
        if isa(expr, tuple):
            test, if_true, if_false = expr
            # TODO: it's expensive to copy the succeed stack.
            #       Can we just save its depth instead?
            fail.append((test, env, if_true, value, list(succeed)))
            succeed.append((if_false, value))
            expr, value = test, False
        elif isa(expr, bool):
            if expr != value:
                if not fail: return False
                test, env, if_true, value, succeed = fail.pop()
                succeed.append((if_true, value))
                expr, value = test, True
            else:
                if not succeed: return env
                expr, value = succeed.pop()
        elif isa(expr, str):
            if expr in env:
                expr = env[expr]
            else:
                env = env.extend(expr, value)
                if not succeed: return env
                expr, value = succeed.pop()
        else:
            assert False

def and_(x, y): return (x, y, False)
def or_(x, y):  return (x, True, y)
def not_(x):    return (x, False, True)
def impl(x, y): return (x, y, True)

x, y = 'x y'.split()

## is_valid(False), is_valid(True), is_valid(x)
#. (False, True, False)

## satisfy(x, True)
#. {'x': True}
## satisfy(not_(x), True)
#. {'x': False}
## satisfy(and_(x, x), True)
#. {'x': True}
## satisfy(and_(x, not_(x)), True)
#. False

## is_valid(impl(impl(impl(x, y), x), x))  # Pierce's Law
#. True
## is_valid(impl(impl(impl(x, y), x), y))
#. False
