"""
Boolean logic built on if-then-else as the basic operator (instead of
AND/OR/NOT).

Here I was trying to be very concrete -- to dispel the homunculus you
naturally think in terms of when dealing with expressions in logic,
which "knows what they mean" and does the right thing according to the
interpretation -- and so here instead of True and False or 1 and 0,
variables take the values 'left' and 'right' (written '<' and
'>'). The choice-expression (A M Z) is like if-then-else, equal to A
when M equals '<', or to Z when M equals '>'. (M can be an expression,
not just a variable.)

~A means '<' if A is '>', etc.

I don't remember why I wrote this using a worklist instead of a
continuation function. I think it's equivalent. In the logic
literature what this is doing is called searching for a tableau proof
(but they explain it in terms of rules for each of AND, OR, etc.,
where here there's just one type of compound expression).

Of course another angle on if-then-else logic is BDDs. There's some
BDD-ish code here mostly under Maker, but see bdd.py for a more
dedicated codebase.
"""

class Choice:
    def __init__(self, left, test, right):
        self.test = test
        self.args = (left, right)
    def __repr__(self):
        return '(%r %r %r)' % (self.args[0], self.test, self.args[1])
    def __invert__(self):
        return Choice(~self.args[0], self.test, ~self.args[1])
    def flip(self):
        return Choice(self.args[1].flip(),
                      self.test.flip(),
                      self.args[0].flip())
    def get_variables(self):
        return frozenset.union(*[v.get_variables()
                                 for v in self.args + (self.test,)])
    def eval(self, env):
        return self.test.eval(env).choose(*self.args).eval(env)
    def subst(self, v, c, maker):
        assert isinstance(self.test, Variable)
        if self.test is v:
            return c.choose(self.args[0], self.args[1])
        elif maker.rank(v) < maker.rank(self):
            return self
        else:
            return maker.cons(self.subst(self.args[0], v, c, maker),
                              self.test,
                              self.subst(self.args[1], v, c, maker))
    def satisfy(self, value, env, worklist):
        return (
               worklist.add(self.args[0], value).add(self.test, L).satisfy(env)
            or worklist.add(self.args[1], value).add(self.test, R).satisfy(env))

class Literal(Choice):
    def __init__(self, left, name, right):
        Choice.__init__(self, left, self, right)
        self.name = name
    def __repr__(self):
        return self.name

class Constant(Literal):
    def __init__(self, name, dir):
        Literal.__init__(self, self, name, self)
        self.dir = dir
    def __invert__(self):
        return R if self is L else L
    def flip(self):
        return ~self
    def get_variables(self):
        return frozenset()
    def eval(self, env):
        return self
    def choose(self, left, right):
        return (left, right)[self.dir]
    def subst(self, v, c, maker):
        return self
    def satisfy(self, value, env, worklist):
        return worklist.satisfy(env) if self is value else None

L = Constant('<', 0)
R = Constant('>', 1)

class Variable(Literal):
    def __init__(self, name):
        Literal.__init__(self, L, name, R)
    def __invert__(self):
        return Choice(R, self.test, L)
    def flip(self):
        return self
    def get_variables(self):
        return frozenset([self])
    def eval(self, env):
        return env[self] if self in env else self
    def choose(self, left, right):
        return Choice(left, self, right)
    def subst(self, v, c, maker):
        return c if v is self else self
    def satisfy(self, value, env, worklist):
        v = env.get(self)
        if v: return v.satisfy(value, env, worklist)
        else: return worklist.satisfy(env.extend(self, value))

## a, b, c, p, q, x, y, z = map(Variable, 'abcpqxyz')
## (L, a)
#. (<, a)
## Choice(a, L, z)
#. (a < z)
## Choice(a, L, z).eval({})
#. a
### Choice(a, b, z).eval({a: R})  # XXX
## Choice(a, b, z).eval({b: R})
#. z
## ~a
#. (> a <)
## ~Choice(a, b, z)
#. ((> a <) b (> z <))

## satisfy(L, R)
## satisfy(L, L)
#. _
## satisfy(a, R)
#. a->._
## satisfy(a, R, empty_env.extend(a, L))
## satisfy(a, R, empty_env.extend(a, R))
#. a->._

## empty_env.extend(a, L)[a]
#. <
### empty_env[a]

## satisfy(Choice(L, a, ~a), R)

def leftmost(a, b):  return Choice(L, a, b)
def rightmost(b, a): return Choice(b, a, R)
def majority(a, b, c): return Choice(leftmost(c, b), a, rightmost(b, c))

## majority(a, b, c).flip()
#. ((< c b) a (b c >))
## satisfy(majority(a, b, c), L)
#. c-<.a-<._
## satisfy(majority(a, b, c), R)
#. b->.c->.a-<._

class Env:
    def extend(self, var, value):
        return ExtendedEnv(var, value, self)
    def __getitem__(self, var):
        value = self.get(var)
        if value is None: raise KeyError(var)
        return value
    def __contains__(self, var):
        return self.get(var) is not None

class EmptyEnv(Env):
    def __repr__(self):
        return '_'
    def get(self, var):
        return None

empty_env = EmptyEnv()

class ExtendedEnv(Env):
    def __init__(self, var, value, parent):
        self.var = var
        self.value = value
        self.parent = parent
    def __repr__(self):
        return '%r-%r.%r' % (self.var, self.value, self.parent)
    def get(self, var):
        return self.value if var is self.var else self.parent.get(var)

def satisfy(e, value, env=empty_env):
    assert isinstance(value, Constant)
    return EmptyWorkList().add(e, value).satisfy(env)

class WorkList:
    def add(self, e, value):
        return ExtendedWorkList(self, e, value)

class EmptyWorkList(WorkList):
    def satisfy(self, env):
        return env

class ExtendedWorkList(WorkList):
    def __init__(self, parent, e, value):
        self.parent = parent
        self.e = e
        self.value = value
    def satisfy(self, env):
        return self.e.satisfy(self.value, env, self.parent)

## majority(a, b, c).get_variables()
#. frozenset([b, c, a])
## for m, n in tabulate(majority(a, b, c)): print m, n
#. ((< c b) a (b c >))
#. b-<.c-<.a-<._ <
#. b-<.c-<.a->._ <
#. b-<.c->.a-<._ <
#. b-<.c->.a->._ >
#. b->.c-<.a-<._ <
#. b->.c-<.a->._ >
#. b->.c->.a-<._ >
#. b->.c->.a->._ >
#. 

## env = empty_env.extend(a, L).extend(c, L).extend(b, L)
## env
#. b-<.c-<.a-<._
## foo = Choice(Choice(L, c, b), a, R)
## foo
#. ((< c b) a >)
## foo.eval(env)
#. <

def tabulate(e):
    print e
    for env in gen_settings(list(e.get_variables())):
        yield env, e.eval(env)

def gen_settings(vars):
    if not vars:
        yield empty_env
    else:
        v, vars = vars[0], vars[1:]
        for value in [L, R]:
            for env in gen_settings(vars):
                yield env.extend(v, value)

infinite_rank = 2**32-1

class Maker:

    def __init__(self, ranker):
        self.ranker = ranker
        self.variables = {}
        self.choices = {}

    def make_variable(self, name):
        if name not in self.variables:
            self.variables[name] = Variable(name)
        return self.variables[name]

    def rank(self, e):
        return infinite_rank if e in (L, R) else self.ranker(e.test)

    def choice(self, a, m, z):
        # Pre: a, m, and z are already hash-consed
        v = min(a, m, z, key=self.rank)
        amz = Choice(a, m, z)
        return self.cons(self.subst(amz, v, L),
                         v,
                         self.subst(amz, v, R))

    def cons(self, a, v, z):
        # Pre: a and z are already hash-consed
        # Pre: v is a variable preceding hd(a) and hd(z)
        if a is z: return a
        key = (a, v, z)
        if key not in self.choices:
            self.choices[key] = Choice(a, v , z)
        return self.choices[key]

    def subst(self, e, v, c):
        assert isinstance(v, Variable)
        assert self.rank(v) <= self.rank(e)
        assert c in (L, R)
        return e.subst(v, c, self)
