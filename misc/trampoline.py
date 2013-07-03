"""
Messing with http://web.mit.edu/kmill/www/programming/tailcall.html
turning into http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.45.5447

I give these classes lowercase names because the usual uppercase style becomes
obtrusive in this use.
"""

class trampoline(object):
    def __init__(self, f):
        self.f = f
    def __call__(self, *args, **kwargs):
        state = self.f(*args, **kwargs)
        while isinstance(state, doing):
            state = state.bounce()
        assert isinstance(state, done)
        return state.result

class doing(object):
    def __init__(self, trampolined, *args, **kwargs):
        assert isinstance(trampolined, trampoline)
        self.f = trampolined.f
        self.args = args
        self.kwargs = kwargs
    def bounce(self):
        return self.f(*self.args, **self.kwargs)

class done(object):
    def __init__(self, result):
        self.result = result

# Examples

@trampoline
def odd(n):
    return done(False) if n == 0 else doing(even, n - 1)

@trampoline
def even(n):
    return done(True) if n == 0 else doing(odd, n - 1)

## odd(4200), even(4200)
#. (False, True)

# A Scheme example using both tail and nontail calls, though it's
# unnatural for Python lists.
@trampoline
def tree_sum(x, total=0):
    if not x:
        return done(total)
    elif isinstance(x, list):
        return doing(tree_sum, x[1:], tree_sum(x[0], total))
    else:
        return done(total + x)

## tree_sum([42, [1,2,[3],4]])
#. 52
