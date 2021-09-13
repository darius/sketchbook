"""
A term-rewriting interpreter as an example
TODO nontrivial test
"""

from structs import Struct, Visitor
import ire 

# AST

class Rule(Struct('pat expr')):
    def __repr__(self):
        return "%r >> %r" % (self.pat, self.expr)

class Term(Struct('symbol arguments')):
    def __repr__(self):
        return "%s%r" % (self.symbol, self.arguments)

class Variable(Struct('name')):
    def __repr__(self):
        return self.name


# Parser

grammar = r"""  _ program .end

- program:	rule*

- rule:         \:/_ term \>>/_ term   :Rule

- term:         sname [argument* :hug] :Term

- argument:     constant
              | variable
              | \(/_ term \)/_

- constant:	sname [:hug]           :Term
- variable:     vname                  :Variable

- sname:        `([A-Z][a-z_0-9A-Z]*\b)` _    # symbol name
- vname:        `([a-z_][a-z_0-9]*\b)` _      # variable name

- _:            .spaces
"""

def hug(*vals): return vals

program_pattern = ire.compile(grammar)
program_semantics = globals()

def parse(string):
    return program_pattern.match(string).do(program_semantics)


# Rewriter
# TODO use a visitor?
# TODO better naming

def run(program):
    def ev(term):
        while True:
            term = Term(term.symbol, map(ev, term.arguments))
            for rule in program:
                env = match(rule.pat, term, {})
                if env is not None:
                    term2 = subst(rule.expr, env)
                    if 1:
                        print rule, ':::', term, '...', term2
                    term = term2
                    break
            else:
                return term
    def match(pat, term, env):
        if isinstance(pat, Variable):
            val = env.get(pat.name)
            if val is None:
                env[pat.name] = term # mutation should be OK since any mismatch bails it all
                return env
            elif term == val:
                return env
            else:
                return None
        elif isinstance(pat, Term):
            if pat.symbol == term.symbol and len(pat.arguments) == len(term.arguments):
                for p, t in zip(pat.arguments, term.arguments):
                    if None is match(p, t, env):
                        return None
                return env
            else:
                return None
        else:
            assert 0
    def subst(expr, env):
        if isinstance(expr, Variable):
            return env[expr.name]
        elif isinstance(expr, Term):
            return Term(expr.symbol, [subst(arg, env) for arg in expr.arguments])
        else:
            assert 0
        
    return ev(Term('Main', []))


# Smoke test

## parse(': F x (Y z w) >> B')
#. (F(x, Y(z, w)) >> B(),)

p = parse("""
: Main >> Hash (Point X Y)
: Hash (Point a b) >> Times a b
""")

## run(p)
#. Main() >> Hash(Point(X(), Y()),) ::: Main[] ... Hash[Point[X[], Y[]]]
#. Hash(Point(a, b),) >> Times(a, b) ::: Hash[Point[X[], Y[]]] ... Times[X[], Y[]]
#. Times[X[], Y[]]
