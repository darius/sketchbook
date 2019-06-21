"""
(This is old code I'm checking in without re-understanding it. It
might be misguided and worthless.)

Let's explain the Model T Enfilade in modern language as a generic
monoidal tree. For simplicity we won't bother about balancing it.

We'll represent elements of a monoid as Python objects with an __add__
method. I'm not sure yet how the zero elements will be tracked.
"""

class Enfilade(object):
    def __init__(self, u0, d0, tree):
        self.u0 = u0
        self.d0 = d0
        self.tree = tree
    def get_u(self):
        return self.tree.get_u(self.u0)

class Tree(object):
    def __add__(self, other):
        return Compose(self, other)
    def get_u(self, u0):
        abstract
        
class Empty(Tree):
    def __add__(self, tree):
        return tree
    def get_u(self, u0):
        return u0

class Leaf(Tree):
    def __init__(self, datum, u):
        self.datum = datum
        self.u = u
    def get_u(self, u0):
        return self.u

class Compose(Tree):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.u = left.u + right.u
    def get_u(self, u0):
        return self.u

def Act(action, tree):
    if isinstance(tree, Acted):
        return Acted(action + tree.action, tree.tree)
    else:
        return Acted(action, tree)

class Acted(Tree):
    def __init__(self, action, tree):
        self.action = action
        self.tree = tree
    def get_u(self, u0):
        return self.action(self.tree.get_u(u0)) # XXX right?
