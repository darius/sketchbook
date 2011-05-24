"""
The N-queens problem as a SAT problem.
"""

import unitsat as sat

## queens(2)
#. none
#. 
## queens(4)
#. . . Q .
#. Q . . .
#. . . . Q
#. . Q . .
#. 

def queens(n):
    env = sat.solve(queens_problem(n))
    if env is None:
        print 'none'
    else:
        show_board(n, env)

def show_board(n, env):
    for row in make_board(n):
        for var in row:
            print '.Q'[env[var]],
        print

def queens_problem(n):
    board = make_board(n)
    return conjoin(
        flatten(exactly_one(row) for row in board),
        flatten(at_most_one(col) for col in transpose(board)),
        flatten(at_most_one(diag) for diag in rising_diagonals(board)),
        flatten(at_most_one(diag) for diag in falling_diagonals(board)))

def make_board(n):
    """Return a 2-d array of distinct variables: each means there's a
    queen at its position."""
    return [range(1+r*n, 1+(r+1)*n) for r in range(n)]

## queens_problem(1)
#. [[1]]
## queens_problem(2)
#. [[1, 2], [-1, -2], [3, 4], [-3, -4], [-1, -3], [-2, -4], [-4, -1], [-2, -3]]
## queens_problem(3)
#. [[1, 2, 3], [-1, -2], [-1, -3], [-2, -3], [4, 5, 6], [-4, -5], [-4, -6], [-5, -6], [7, 8, 9], [-7, -8], [-7, -9], [-8, -9], [-1, -4], [-1, -7], [-4, -7], [-2, -5], [-2, -8], [-5, -8], [-3, -6], [-3, -9], [-6, -9], [-8, -4], [-9, -5], [-9, -1], [-5, -1], [-6, -2], [-2, -4], [-3, -5], [-3, -7], [-5, -7], [-6, -8]]

## board1 = [[1]]
## board3 = [[1,2,3],[4,5,6],[7,8,9]]
## transpose(board3)
#. [(1, 4, 7), (2, 5, 8), (3, 6, 9)]

def falling_diagonals(board):
    n = len(board)
    for total in range(2*n-1):
        yield [board[r][c]
               for r in range(min(total+1, n))
               for c in [total-r]
               if c < n]

## list(falling_diagonals(board1))
#. [[1]]
## list(falling_diagonals(board3))
#. [[1], [2, 4], [3, 5, 7], [6, 8], [9]]

def rising_diagonals(board):
    return falling_diagonals(board[::-1])

## list(rising_diagonals(board3))
#. [[7], [8, 4], [9, 5, 1], [6, 2], [3]]

def at_least_one(literals):
    return [literals]

def at_most_one(literals):
    return [[-literals[j], -xi]
            for i, xi in enumerate(literals)
            for j in range(i)]

## at_most_one([9, 5, 1])
#. [[-9, -5], [-9, -1], [-5, -1]]

def exactly_one(literals):
    return at_least_one(literals) + at_most_one(literals)

## exactly_one([9, 5, 1])
#. [[9, 5, 1], [-9, -5], [-9, -1], [-5, -1]]

# XXX unused
def not_all(literals):
    return [[-v for v in literals]]

## not_all([9, 5, 1])
#. [[-9, -5, -1]]

def conjoin(*problems):
    return flatten(problems)

def flatten(xss):
    result = []
    for xs in xss:
        result.extend(xs)
    return result

def transpose(grid):
    return zip(*grid)
