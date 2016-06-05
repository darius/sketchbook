"""
Let's try to improve on full_joint.py by memoizing. We need to make
up a hashable dictlike type to support this.
"""

from __future__ import division

def memoize(f):
    """Return a function like f but caching its results. Its arguments
    must be hashable."""
    memos = {}
    def memoized(*args):
        try: return memos[args]
        except KeyError:
            result = memos[args] = f(*args)
            return result
    return memoized

# Let's simplify by assuming there's just one Bayes net. This will
# list its variables, parents preceding children:
all_variables = []

class Variable:
    "A binary (True/False) random variable."
    def __init__(self, parents, cpt):
        self.parents = parents  # The variables that I depend on.
        self.cpt = cpt          # The conditional probability that I'm true, for each combo of the parents' values.
        all_variables.append(self)

    def p(self, value, e):
        """Return my conditional probability of being the value, given that
        my parents have the values specified by e."""
        ptrue = self.cpt[tuple(e[var] for var in self.parents)]
        return ptrue if value else 1-ptrue

def enumeration_ask(X, e):
    """Return the conditional probability that variable X is true,
    given the {var:val} observations e."""
    assert X not in e, "Query variable must be distinct from evidence"
    e = FrozenDict(e.items())
    odds = [enumerate_all(tuple(all_variables), e.extend(X, xi))
            for xi in (False, True)]
    return odds[1] / sum(odds)

@memoize
def enumerate_all(variables, e):
    """Return the sum of those entries in the joint distribution
    consistent with e, provided variables is the remaining variables
    (the ones not in e). Parents must precede children in variables."""
    if not variables:
        return 1
    Y, rest = variables[0], variables[1:]
    if Y in e:
        return Y.p(e[Y], e) * enumerate_all(rest, e)
    else:
        return sum(Y.p(y, e) * enumerate_all(rest, e.extend(Y, y))
                   for y in (False, True))

class FrozenDict(object):
    def __init__(self, items):
        self._k = tuple(items)

    def extend(self, key, val):
        return FrozenDict(self._k + ((key, val),))

    def __contains__(self, key):
        return any(k == key for k, v in self._k)

    def __getitem__(self, key):
        for k, v in self._k:
            if k == key:
                return v
        raise KeyError("missing", key)

    def __hash__(self):
        return hash(self._k)

    def __eq__(self, other):
        return instanceof(other, FrozenDict) and self._k == other.__k

# Burglary example [AIMA figure 14.2]

T, F = True, False

burglary   = Variable((), {(): 0.001})
earthquake = Variable((), {(): 0.002})
alarm      = Variable((burglary, earthquake),
                      {(T, T): 0.95, (T, F): 0.94, (F, T): 0.29, (F, F): 0.001})
john_calls = Variable((alarm,), {(T,): 0.90, (F,): 0.05})
mary_calls = Variable((alarm,), {(T,): 0.70, (F,): 0.01})

## enumeration_ask(burglary, {john_calls:T, mary_calls:T})
#. 0.2841718353643929
