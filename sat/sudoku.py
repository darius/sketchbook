"""
Generalized Sudoku as a SAT problem.
"""

from itertools import count
import math
import sys
sys.setrecursionlimit(5000)

import indexedsat as solver
from sat import flatten, exactly_one, at_most_one

## unconstrained_sudoku(2)
#. 4 3 | 2 1
#. 2 1 | 4 3
#. ---------
#. 3 4 | 1 2
#. 1 2 | 3 4
#. 
## unconstrained_sudoku(3)
#. 9 8 7 | 6 5 4 | 3 2 1
#. 6 5 4 | 3 2 1 | 9 8 7
#. 3 2 1 | 9 8 7 | 6 5 4
#. ---------------------
#. 8 9 6 | 7 4 5 | 2 1 3
#. 7 4 5 | 2 1 3 | 8 9 6
#. 2 1 3 | 8 9 6 | 7 4 5
#. ---------------------
#. 5 7 9 | 4 6 8 | 1 3 2
#. 4 6 8 | 1 3 2 | 5 7 9
#. 1 3 2 | 5 7 9 | 4 6 8
#. 

easy1 = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
hard1 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'

## solve(easy1)
#. 4 8 3 | 9 2 1 | 6 5 7
#. 9 6 7 | 3 4 5 | 8 2 1
#. 2 5 1 | 8 7 6 | 4 9 3
#. ---------------------
#. 5 4 8 | 1 3 2 | 9 7 6
#. 7 2 9 | 5 6 4 | 1 3 8
#. 1 3 6 | 7 9 8 | 2 4 5
#. ---------------------
#. 3 7 2 | 6 8 9 | 5 1 4
#. 8 1 4 | 2 5 3 | 7 6 9
#. 6 9 5 | 4 1 7 | 3 8 2
#. 

def unconstrained_sudoku(n):
    rows, problem = make_sudoku_grid(n)
    model = solver.solve(problem)
    print_sudoku_solution(rows, model)

def solve(form):
    rows, problem = read_sudoku_problem(form)
    model = solver.solve(problem)
    print_sudoku_solution(rows, model)

def read_sudoku_problem(form):
    rows, problem = make_sudoku_grid(int(len(form) ** (1./4)))
    constrain_to_form(problem, rows, form)
    return rows, problem

def constrain_to_form(problem, rows, form):
    form_chars = iter(form)
    for row in rows:
        for slot, c in zip(row, form_chars):
            if c in '123456789':
                digit = int(c)
                problem.append([slot[digit-1]])

def print_sudoku_solution(rows, model):
    divider = int(math.sqrt(len(rows)))
    for r, row in enumerate(rows):
        if 0 < r and r % divider == 0:
            print '-' * (2 * divider * (divider+1) - 3)
        for c, slot in enumerate(row):
            if 0 < c and c % divider == 0:
                print '|',
            print slot_value(slot, model),
        print

def slot_value(slot, model):
    for i, v in enumerate(slot):
        if model[v]: return i+1

def make_sudoku_grid(n):
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

    return rows, problem

def transpose(grid):
    return zip(*grid)
