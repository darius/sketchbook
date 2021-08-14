"""
Let's make a datalog as an example
TODO
- more examples
- querying
- stratified negation?
"""

from structs import Struct, Visitor
import ire 

# AST

class Clause(Struct('head body')):
    def __repr__(self):
        if self.body:
            return "%r :- %s." % (self.head, ', '.join(map(repr, self.body)))
        else:
            return "%r." % self.head

class Literal(Struct('symbol arguments')):
    def __repr__(self):
        return "%s%r" % (self.symbol, self.arguments)

class Constant(Struct('value')):
    def __repr__(self):
        return repr(self.value)

class Variable(Struct('name')):
    def __repr__(self):
        return self.name


# Parser

grammar = r"""  _ program .end

- program:	clause*

- clause:       literal [(\:-/_ literal++(\,/_))? :hug] \./_ :Clause

- literal:	sname [(\(/_ term**(\,/_) \)/_)? :hug] :Literal

- term: 	vname :Variable | constant :Constant

- constant:	sname | string | .d _      # TODO distinguish string from sname

- sname:        `([A-Z][a-z_0-9A-Z]*\b)` _    # symbol name
- vname:        `([a-z_][a-z_0-9]*\b)` _      # variable name

- string:       `"([^"\\]*)"` _     # TODO escapes

# TODO no fnord

- _:            .spaces
"""

def hug(*vals): return vals

program_pattern = ire.compile(grammar)
program_semantics = globals()


# Analyze

def program_is_safe(clauses):
    return all(map(clause_is_safe, clauses))

def clause_is_safe(clause):
    head_vars = literal_variables(clause.head)
    body_vars = set().union(*map(literal_variables, clause.body))
    return head_vars.issubset(body_vars)

def literal_variables(literal):
    return {term.name for term in literal.arguments if isinstance(term, Variable)}


# Evaluate
# (Naive forward-chaining algorithm)

def saturate(clauses):
    facts = set()
    while True:
        facts2 = consequences(clauses, facts)
        if facts == facts2:
            return facts
        facts = facts2

def consequences(clauses, facts):
    # TODO mutate facts instead, and return a flag
    results = set()
    for clause in clauses:
        for subst in infer_body(clause.body, facts, {}):
            results.add(instantiate(clause.head, subst))
    return results

class Instantiate(Visitor):
    "Replace variables with their substitutions from subst."
    def Literal(self, t, subst):
        return Literal(t.symbol, tuple(self(arg, subst) for arg in t.arguments))
    def Constant(self, t, subst):
        return t
    def Variable(self, t, subst):
        return subst.get(t.name, t)
instantiate = Instantiate()

def infer_body(literals, facts, subst):
    """Yield a subst for each way to make all of literals simultaneously
    supported by facts. A subst is a dict mapping variable names to constants."""
    if not literals:
        yield subst
    else:
        for subst0 in infer_literal(literals[0], facts, subst):
            for subst1 in infer_body(literals[1:], facts, subst0):
                yield subst1

def infer_literal(literal, facts, subst):
    for fact in facts:
        result = match_literal(literal, fact, subst)
        if result is not None:
            yield result

def match_literal(literal, fact, subst):
    "Try to unify a literal and a ground literal `fact`."
    if literal.symbol != fact.symbol or len(literal.arguments) != len(fact.arguments):
        return None
    for larg, farg in zip(literal.arguments, fact.arguments):
        subst = match_term(larg, farg, subst)
        if subst is None: break
    return subst

def match_term(term, constant, subst):
    "Try to unify a term and a ground term `constant`."
    # Would this be simpler if we instantiated term, first?
    if isinstance(term, Variable):
        t = subst.get(term.name)
        if t is None:
            result = dict(subst)
            result[term.name] = constant
            return result
        term = t
    assert isinstance(term, Constant)
    assert isinstance(constant, Constant)
    return subst if term.value == constant.value else None


# Smoke test

## program_pattern.match(r' Hello.').do(program_semantics)
#. (Hello().,)

## program_pattern.match(r'Aloha :- Hello. Aloha :- GoodBye("cruel"), World(x, y, Z).').do(program_semantics)
#. (Aloha() :- Hello()., Aloha() :- GoodBye('cruel',), World(x, y, 'Z').)

eg_genealogy = """
Parent("Sansa Stark", "Eddard Stark").
Parent("Arya Stark", "Eddard Stark").
Parent("Eddard Stark", "Rickard Stark").

GrandParent(x, z) :-
    Parent(x, y),
    Parent(y, z).
"""

## genealogy_program = program_pattern.match(eg_genealogy).do(program_semantics)
# for x in genealogy_program: print x

## program_is_safe(genealogy_program)
#. True

## cinf = saturate(genealogy_program)
## for c in sorted(cinf): print c
#. GrandParent('Arya Stark', 'Rickard Stark')
#. GrandParent('Sansa Stark', 'Rickard Stark')
#. Parent('Arya Stark', 'Eddard Stark')
#. Parent('Eddard Stark', 'Rickard Stark')
#. Parent('Sansa Stark', 'Eddard Stark')

eg_paths = """
Edge("a", "b").
Edge("b", "c").

Path(x, y) :-
    Edge(x, y).
Path(x, z) :-
    Path(x, y),
    Edge(y, z).
"""

## paths_program = program_pattern.match(eg_paths).do(program_semantics)
# for x in paths_program: print x

## program_is_safe(paths_program)
#. True

## cinf = saturate(paths_program)
## for c in sorted(cinf): print c
#. Edge('a', 'b')
#. Edge('b', 'c')
#. Path('a', 'b')
#. Path('a', 'c')
#. Path('b', 'c')
