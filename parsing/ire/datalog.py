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

_builtins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
program_semantics = {k: v for k, v in _builtins.items() if callable(v)}
program_semantics.update(globals())

def parse(string, semantics=None):
    if semantics is None: semantics = program_semantics
    return program_pattern.match(string).do(semantics)


# Analyze

def program_is_safe(clauses):
    return all(map(clause_is_safe, clauses))

def clause_is_safe(clause):
    "It's safe if all variables from its head are also in its body."
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
    assert isinstance(constant, Constant), constant
    return subst if term.value == constant.value else None


# Smoke test

## parse(r' Hello.')
#. (Hello().,)

## parse('Aloha :- Hello. Aloha :- GoodBye("cruel"), World(x, y, Z).')
#. (Aloha() :- Hello()., Aloha() :- GoodBye('cruel',), World(x, y, 'Z').)

eg_genealogy = """
Parent("Sansa Stark", "Eddard Stark").
Parent("Arya Stark", "Eddard Stark").
Parent("Eddard Stark", "Rickard Stark").

GrandParent(x, z) :-
    Parent(x, y),
    Parent(y, z).
"""

## genealogy_program = parse(eg_genealogy)
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

## paths_program = parse(eg_paths)
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


# Longer example

maze_data = """\
.#...
.#.##
.#...
...#.
##.#."""

# TODO edit the first # to . to connect a large region to (0,0)
#      (it hangs practically forever when I do)
# TODO it's way too slow:
maze_data2 = """\
...#######...............####..
###.#@#..#################..##.
#...###......................#.
#........########..####..##..#.
###.####.....#..####..####..##.
#@#.#..#.#.#.#.....#.....#...#.
#@#.#..#.....#.##..#.##..##..#.
###....###.###..#.##..#.##..##.
.#...#.#@#......#.....#.#....#.
.#...#.###..#####..####.#....#.
.#####...#####..#######.######.
.#...#.#.#@@#...............#..
##.#.#...#@@#..#######..##..#..
#....#########..#....#####.###.
#.#.............#.o........#@#.
#...#########..###.i#####..#@#.
#####.......####.####...######.
"""

maze_2d = maze_data.splitlines()
maze_height = len(maze_2d)
maze_width = len(maze_2d[0])

maze_facts = ['At(%d,%d,"%s").' % (x,y,ch)
              for y,line in enumerate(maze_2d)
              for x,ch in enumerate(line)]

add1_facts = ['Add1(%d,%d).' % (n,n+1)
              for n in range(max(maze_width, maze_height) - 1)]

# (hacked Neighbor to ensure program is safe)
# TODO add an automatic check of that condition

# TODO would Reachable be equally fast in the other ordering?
# Doesn't look like it

# TODO seminaive eval

maze_problem = """
Reachable(0, 0).
Reachable(x, y) :- Reachable(x1, y1), Arc(x1, y1, x, y).

Arc(x1,y, x2,y) :- At(x1,y,"."), Neighbors(x1, x2), At(x2,y,".").
Arc(x,y1, x,y2) :- At(x,y1,"."), Neighbors(y1, y2), At(x,y2,".").

Neighbors(n1, n2) :- Add1(n1, n2).
Neighbors(n1, n2) :- Add1(n2, n1).
"""

maze_source = '\n'.join([maze_problem] + maze_facts + add1_facts)
## maze_program = parse(maze_source)
# for line in maze_program: print line

## assert(program_is_safe(maze_program))

## results = saturate(maze_program)
## for c in sorted(results): print c
#. Add1(0, 1)
#. Add1(1, 2)
#. Add1(2, 3)
#. Add1(3, 4)
#. Arc(0, 0, 0, 1)
#. Arc(0, 1, 0, 0)
#. Arc(0, 1, 0, 2)
#. Arc(0, 2, 0, 1)
#. Arc(0, 2, 0, 3)
#. Arc(0, 3, 0, 2)
#. Arc(0, 3, 1, 3)
#. Arc(1, 3, 0, 3)
#. Arc(1, 3, 2, 3)
#. Arc(2, 0, 2, 1)
#. Arc(2, 0, 3, 0)
#. Arc(2, 1, 2, 0)
#. Arc(2, 1, 2, 2)
#. Arc(2, 2, 2, 1)
#. Arc(2, 2, 2, 3)
#. Arc(2, 2, 3, 2)
#. Arc(2, 3, 1, 3)
#. Arc(2, 3, 2, 2)
#. Arc(2, 3, 2, 4)
#. Arc(2, 4, 2, 3)
#. Arc(3, 0, 2, 0)
#. Arc(3, 0, 4, 0)
#. Arc(3, 2, 2, 2)
#. Arc(3, 2, 4, 2)
#. Arc(4, 0, 3, 0)
#. Arc(4, 2, 3, 2)
#. Arc(4, 2, 4, 3)
#. Arc(4, 3, 4, 2)
#. Arc(4, 3, 4, 4)
#. Arc(4, 4, 4, 3)
#. At(0, 0, '.')
#. At(0, 1, '.')
#. At(0, 2, '.')
#. At(0, 3, '.')
#. At(0, 4, '#')
#. At(1, 0, '#')
#. At(1, 1, '#')
#. At(1, 2, '#')
#. At(1, 3, '.')
#. At(1, 4, '#')
#. At(2, 0, '.')
#. At(2, 1, '.')
#. At(2, 2, '.')
#. At(2, 3, '.')
#. At(2, 4, '.')
#. At(3, 0, '.')
#. At(3, 1, '#')
#. At(3, 2, '.')
#. At(3, 3, '#')
#. At(3, 4, '#')
#. At(4, 0, '.')
#. At(4, 1, '#')
#. At(4, 2, '.')
#. At(4, 3, '.')
#. At(4, 4, '.')
#. Neighbors(0, 1)
#. Neighbors(1, 0)
#. Neighbors(1, 2)
#. Neighbors(2, 1)
#. Neighbors(2, 3)
#. Neighbors(3, 2)
#. Neighbors(3, 4)
#. Neighbors(4, 3)
#. Reachable(0, 0)
#. Reachable(0, 1)
#. Reachable(0, 2)
#. Reachable(0, 3)
#. Reachable(1, 3)
#. Reachable(2, 0)
#. Reachable(2, 1)
#. Reachable(2, 2)
#. Reachable(2, 3)
#. Reachable(2, 4)
#. Reachable(3, 0)
#. Reachable(3, 2)
#. Reachable(4, 0)
#. Reachable(4, 2)
#. Reachable(4, 3)
#. Reachable(4, 4)
