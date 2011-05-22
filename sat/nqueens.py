"""
The N-queens problem as a SAT problem.
"""

def queens_problem(n):
    grid = [range(1+r*n, 1+(r+1)*n) for r in range(n)]
    return conjoin(
        flatten(exactly_one(row) for row in grid),
        flatten(at_most_one(col) for col in transpose(grid)),
        flatten(at_most_one(diag) for diag in rising_diagonals(grid)),
        flatten(at_most_one(diag) for diag in falling_diagonals(grid)))

## queens_problem(1)
#. [[1]]
## queens_problem(2)
#. [[1, 2], [-1, -2], [3, 4], [-3, -4], [-1, -3], [-2, -4], [-4, -1], [-2, -3]]
## queens_problem(3)
#. [[1, 2, 3], [-1, -2], [-1, -3], [-2, -3], [4, 5, 6], [-4, -5], [-4, -6], [-5, -6], [7, 8, 9], [-7, -8], [-7, -9], [-8, -9], [-1, -4], [-1, -7], [-4, -7], [-2, -5], [-2, -8], [-5, -8], [-3, -6], [-3, -9], [-6, -9], [-8, -4], [-9, -5], [-9, -1], [-5, -1], [-6, -2], [-2, -4], [-3, -5], [-3, -7], [-5, -7], [-6, -8]]

## grid1 = [[1]]
## grid3 = [[1,2,3],[4,5,6],[7,8,9]]
## transpose(grid3)
#. [(1, 4, 7), (2, 5, 8), (3, 6, 9)]

def falling_diagonals(grid):
    n = len(grid)
    for total in range(2*n-1):
        yield [grid[r][c]
               for r in range(min(total+1, n))
               for c in [total-r]
               if c < n]

## list(falling_diagonals(grid1))
#. [[1]]
## list(falling_diagonals(grid3))
#. [[1], [2, 4], [3, 5, 7], [6, 8], [9]]

def rising_diagonals(grid):
    return falling_diagonals(grid[::-1])

## list(rising_diagonals(grid3))
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
