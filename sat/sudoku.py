"""
Generalized Sudoku as a SAT problem.
"""

import sys
sys.setrecursionlimit(5000)

import indexedsat as solver
from sat import conjoin, flatten, exactly_one, at_most_one
from itertools import count

## sudoku(2)
#. 4 3 2 1
#. 2 1 4 3
#. 3 4 1 2
#. 1 2 3 4
#. 
## sudoku(3)
#. 9 8 7 6 5 4 3 2 1
#. 6 5 4 3 2 1 9 8 7
#. 3 2 1 9 8 7 6 5 4
#. 8 9 6 7 4 5 2 1 3
#. 7 4 5 2 1 3 8 9 6
#. 2 1 3 8 9 6 7 4 5
#. 5 7 9 4 6 8 1 3 2
#. 4 6 8 1 3 2 5 7 9
#. 1 3 2 5 7 9 4 6 8
#. 

def sudoku(n):
    
    problem = []
    def add_permutation(slots):
        for variables in transpose(slots):
            problem.extend(at_most_one(variables))

    make_variable = count(1).next
    def make_slot():
        slot = [make_variable() for i in range(n*n)]
        problem.extend(exactly_one(slot))
        return slot
    def make_block():
        block = [[make_slot() for c in range(n)] for r in range(n)]
        add_permutation(flatten(block))
        return block

    superblock = [[make_block() for c in range(n)] for r in range(n)]
    rows = flatten([map(flatten, transpose(row)) for row in superblock])

    for row in rows:
        add_permutation(row)
    for column in transpose(rows):
        add_permutation(column)

    model = solver.solve(problem)
    for row in rows:
        for slot in row:
            for i, v in enumerate(slot):
                if model[v]:
                    print i+1,
        print

def transpose(grid):
    return zip(*grid)
