"""
Read or write the DIMACS CNF file format.
"""

def save(filename, problem):
    save_file(open(filename, 'w'), problem)

def save_file(f, problem):
    nvariables = reduce(max,
                        (abs(literal) for clause in problem for literal in clause),
                        0)
    nclauses = len(problem)
    print >>f, 'p cnf', nvariables, nclauses
    for clause in problem:
        for literal in clause:
            print >>f, literal,
        print >>f, 0

def load(filename):
    return load_file(open(filename))

def load_file(f):
    nvariables = None
    nclauses = None
    clauses = []
    clause = []
    for line in f:
        if line.startswith('c'):
            continue
        if line.startswith('p'):
            f1, f2, f3, f4 = line.split()
            if f1 != 'p' or f2 != 'cnf':
                raise Exception('Not in DIMACS CNF format')
            nvariables = int(f3)
            nclauses = int(f4)
        else:
            lits = map(int, line.split())
            for lit in lits:
                if lit == 0:
                    clauses.append(clause)
                    clause = []
                else:
                    assert 1 <= abs(lit) <= nvariables
                    clause.append(lit)
    if clause:
        clauses.append(clause)
    assert nclauses == len(clauses)
    return nvariables, clauses
