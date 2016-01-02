"""
A basic demo of automatic differentiation. (Almost untested.)
Forward mode, and for simplicity supporting only one variable.
"""
from __future__ import division

class DualNumber(object):
    def __init__(self, v, d):
        self.v = v              # The value
        self.d = d              # The derivative
    def __neg__(self):
        return DualNumber(-self.v, -self.d)
    def __add__(self, other):
        other = promote(other)
        return DualNumber(self.v + other.v, self.d + other.d)
    def __sub__(self, other):
        other = promote(other)
        return DualNumber(self.v - other.v, self.d - other.d)
    def __mul__(self, other):
        other = promote(other)
        return DualNumber(self.v * other.v, self.d*other.v + self.v*other.d)
    def __div__(self, other):
        other = promote(other)
        return DualNumber(self.v / other.v,
                          (self.d * other.v - self.v * other.d) / other.v**2)
    def __radd__(self, other): return Scalar(other) + self
    def __rsub__(self, other): return Scalar(other) - self
    def __rmul__(self, other): return Scalar(other) * self
    def __rdiv__(self, other): return Scalar(other) / self

    def __repr__(self):
        if self.d == 0:
            return repr(self.v)
        else:
            return '(%r, %r)' % (self.v, self.d)

def promote(value):
    return value if isinstance(value, DualNumber) else Scalar(value)

def Scalar(c):
    return DualNumber(c, 0)

def Variable(value):
    return DualNumber(value, 1)

x = Variable(2)

## x*x*x
#. (8, 12)
