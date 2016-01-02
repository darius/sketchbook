"""
A basic demo of symbolic differentiation.
Just one variable, for simplicity.
"""

class Formula(object):
    def __neg__(self):         return Constant(-1) * self
    def __add__(self, other):  return add(self, promote(other))
    def __sub__(self, other):  return add(self, -promote(other))
    def __mul__(self, other):  return mul(self, promote(other))
    def __div__(self, other):  return div_(self, promote(other))
    def __radd__(self, other): return Constant(other) + self
    def __rsub__(self, other): return Constant(other) - self
    def __rmul__(self, other): return Constant(other) * self
    def __rdiv__(self, other): return Constant(other) / self

class Constant(Formula):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return repr(self.value)
    def eval(self, x):
        return self.value
    def d_dx(self):
        return Constant(0)

class Variable(Formula):
    "Just the one variable, x."
    def __repr__(self):
        return 'x'
    def eval(self, x):
        return x
    def d_dx(self):
        return Constant(1)

def add(e1, e2):
    if isinstance(e1, Constant) and isinstance(e2, Constant):
        return Constant(e1.value + e2.value)
    else:
        return Add(e1, e2)

def mul(e1, e2):
    if isinstance(e1, Constant) and isinstance(e2, Constant):
        return Constant(e1.value * e2.value)
    elif isinstance(e2, Constant):
        return mul(e2, e1)
    elif isinstance(e1, Constant) and e1.value == 1:
        return e2
    else:
        return Mul(e1, e2)

def div(e1, e2):
    return Div(e1, e2)   # Yeah, I'm getting tired of this.

class Add(Formula):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    def __repr__(self):
        return '(%r + %r)' % (self.e1, self.e2)
    def eval(self, x):
        return self.e1.eval(x) + self.e2.eval(x) 
    def d_dx(self):
        return self.e1.d_dx() + self.e2.d_dx() 

class Mul(Formula):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    def __repr__(self):
        return '(%r * %r)' % (self.e1, self.e2)
    def eval(self, x):
        return self.e1.eval(x) * self.e2.eval(x) 
    def d_dx(self):
        return self.e1.d_dx() * self.e2 + self.e1 * self.e2.d_dx()

class Div(Formula):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    def __repr__(self):
        return '(%r / %r)' % (self.e1, self.e2)
    def eval(self, x):
        return self.e1.eval(x) / self.e2.eval(x) 
    def d_dx(self):
        return (self.e1.d_dx() * self.e2 - self.e1 * self.e2.d_dx()) / (self.e2 * self.e2)

def promote(value):
    return value if isinstance(value, Formula) else Constant(value)

x = Variable()

x3 = x * x * x
## x3
#. ((x * x) * x)
## x3.eval(2)
#. 8
## x3.d_dx()
#. (((x + x) * x) + (x * x))
## x3.d_dx().eval(2)
#. 12
