"""
Generalized Sudoku as a SAT problem.
"""

import indexedsat as solver
from sat import conjoin, flatten, exactly_one, at_most_one
from itertools import count

## sudoku(2)
#. {1: False, 2: False, 3: False, 4: True, 5: False, 6: False, 7: True, 8: False, 9: False, 10: True, 11: False, 12: False, 13: True, 14: False, 15: False, 16: False, 17: False, 18: True, 19: False, 20: False, 21: True, 22: False, 23: False, 24: False, 25: False, 26: False, 27: False, 28: True, 29: False, 30: False, 31: True, 32: False, 33: False, 34: False, 35: True, 36: False, 37: False, 38: False, 39: False, 40: True, 41: True, 42: False, 43: False, 44: False, 45: False, 46: True, 47: False, 48: False, 49: True, 50: False, 51: False, 52: False, 53: False, 54: True, 55: False, 56: False, 57: False, 58: False, 59: True, 60: False, 61: False, 62: False, 63: False, 64: True}
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

    print solver.solve(problem)

def transpose(grid):
    return zip(*grid)
