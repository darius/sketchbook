"""
I 'cleaned up' some code for Peter Norvig.
Thanks to Charles Lee for pointing out that
    decorator = decorator(decorator)
leaves decorator without a doc string, and for the fix.
"""

import functools

def decorator(d):
    "Make function d a decorator: d wraps a function fn."
    return lambda fn: functools.update_wrapper(d(fn), fn)

decorator = decorator(decorator)(decorator)


# Silly example use
@decorator
def twice(f):
    return lambda x: f(f(x))

@twice
def foo(x):
    "Be quartic or be square!"
    return x*x

## foo(2)
#. 16

## help(foo)
#. Help on function foo:
#. 
#. foo(x)
#.     Be quartic or be square!
#. 
#. 
