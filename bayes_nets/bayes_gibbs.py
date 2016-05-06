"""
Based on https://github.com/aimacode/aima-python/blob/master/probability.py
"""

from __future__ import division
import operator, random

# Let's simplify by assuming there's just one Bayes net, and this will
# list its variables, with parents preceding children:
all_vars = []

class Variable:
    "A binary (True/False) random variable."

    def __init__(self, parents, cpt):
        self.parents = parents  # The variables that I depend on.
        self.cpt = cpt          # Conditional prob. that I'm true, for each combo of the parents' values.
        self.children = []      # The variables that depend on me (to be filled in).
        for parent in parents: parent.children.append(self)
        all_vars.append(self)

    def p(self, value, e):
        """Return my probability of having the value, given that my parents
        have their value from e."""
        ptrue = self.cpt[tuple(e[var] for var in self.parents)]
        return ptrue if value else 1-ptrue

    def markov_blanket_sample(self, e):
        """Return a sample from P(self | others) where others denotes that all
        other variables take their values from event e."""
        # Only my 'Markov blanket' is relevant: that is, my parents,
        # children, and children's other parents. I'm conditionally
        # independent of all other variables, given my Markov blanket.
        ex = dict(e)
        ex[self] = False
        fp = self.p(False, e) * product(child.p(ex[child], ex) for child in self.children)
        ex[self] = True
        tp = self.p(True,  e) * product(child.p(ex[child], ex) for child in self.children)
        return random.uniform(0, fp+tp) < tp

def product(numbers):
    return reduce(operator.mul, numbers, 1)

def gibbs_ask(X, e, N):
    """Estimate P(X|e): the probability that variable X is true, given
    event e. Use a Markov-chain sampling of length proportional to N."""
    assert X not in e, "Query variable must be distinct from evidence"
    Z = [var for var in all_vars if var not in e]
    state = dict(e)
    for Zi in Z: state[Zi] = random.choice([True, False])
    counts = {True: 0, False: 0}
    for _ in xrange(N):
        for Zi in Z:
            state[Zi] = Zi.markov_blanket_sample(state)
            counts[state[X]] += 1
    return counts[True] / sum(counts.values())


# Burglary example [AIMA figure 14.2]

T, F = True, False

burglary   = Variable((), {(): 0.001})
earthquake = Variable((), {(): 0.002})
alarm      = Variable((burglary, earthquake),
                      {(T, T): 0.95, (T, F): 0.94, (F, T): 0.29, (F, F): 0.001})
john_calls = Variable((alarm,), {(T,): 0.90, (F,): 0.05})
mary_calls = Variable((alarm,), {(T,): 0.70, (F,): 0.01})

# What's the probability there's a burglary, given that John and Mary both call?
## random.seed(1017)
## gibbs_ask(burglary, {john_calls:T, mary_calls:T}, 1000)
#. 0.262
