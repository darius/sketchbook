"""
Modeled after https://github.com/fewf/curtsies_2048
TODO: Background colors, boldness for different numbers
"""

import random, time

import sturm

def main():
    board = make_board()
    with sturm.cbreak_mode():
        while True:
            heading = "Use the arrow keys, or Q to quit.\n\n"
            game_over = not any(list(move(board)) for move in [up,down,left,right])
            score = "You win!" if is_won(board) else "You lose!" if game_over else ""
            sturm.render(heading + view(board) + "\n\n" + score + "\n")
            if game_over: break
            key = sturm.get_key()
            if key.upper() == 'Q': break
            elif key in globals(): # Hacky hacky, sorry. :P
                sliding = list(globals()[key](board))
                if sliding:
                    for board in sliding:
                        sturm.render(heading + view(board))
                        time.sleep(.04)
                    board = plop(board, 2 if random.random() < .9 else 4)

# A board is a tuple of 4 rows;
# a row is a tuple of 4 values;
# a value is 0 for empty, or a positive number.

def make_board(): return plop(plop(empty_board, 2), 2)

empty_board = ((0,)*4,)*4

# Pre: board has at least one empty square.
def plop(board, v):
    return update(board, random_empty(board), v)

def random_empty(board):
    return random.choice([(r,c)
                          for r, row in enumerate(board)
                          for c, v in enumerate(row)
                          if v == 0])

def update(board, pos, new_v):
    return tuple(tuple(new_v if (r,c) == pos else v
                       for c, v in enumerate(row))
                 for r, row in enumerate(board))

def view(board):
    return '\n\n'.join(' '.join(('%d' % v if v else '.').center(4)
                                for v in row)
                       for row in board)

def is_won(board): return any(row.count(2048) for row in board)

def flipv(board): return board[::-1]                # vertical flip
def flipd(board): return tuple(zip(*board))         # diagonal
def fliph(board): return flipd(flipv(flipd(board))) # horizontal

# Arrow-key actions. Each returns an iterable of boards animating
# the move, empty if there's no move in that direction.
def up(board):    return map(flipd, left(flipd(board)))
def down(board):  return map(flipd, right(flipd(board)))
def right(board): return map(fliph, left(fliph(board)))
def left(board):
    states = tuple((0, row) for row in board)
    while True:
        states = tuple(collapsing(lo,row) for lo,row in states)
        if all(lo is None for lo,_ in states):
            break
        yield tuple(row for _,row in states)

def collapsing(lo, row):
    if lo is None:
        return lo, row
    for i in range(1, 4):
        if row[i-1] == 0 and row[i] != 0:
            break
        if lo < i and row[i-1] and row[i-1] == row[i]:
            lo = i
            break
    else:
        return None, row
    return lo, row[:i-1] + (row[i-1] + row[i],) + row[i+1:] + (0,)


# For testing
def collapse(row):
    lo = 0
    while True:
        lo, row = collapsing(lo, row)
        if lo is None: break
        print(row)

## collapse((0, 0, 0, 0))
## collapse((2, 4, 2, 2))
#. (2, 4, 4, 0)
## collapse((2, 2, 2, 2))
#. (4, 2, 2, 0)
#. (4, 4, 0, 0)
## collapse((0, 2, 0, 2))
#. (2, 0, 2, 0)
#. (2, 2, 0, 0)
#. (4, 0, 0, 0)
## collapse((2, 0, 2, 0))
#. (2, 2, 0, 0)
#. (4, 0, 0, 0)
## collapse((2, 0, 0, 2))
#. (2, 0, 2, 0)
#. (2, 2, 0, 0)
#. (4, 0, 0, 0)
## collapse((0, 0, 0, 2))
#. (0, 0, 2, 0)
#. (0, 2, 0, 0)
#. (2, 0, 0, 0)
## collapse((0, 2, 4, 4))
#. (2, 4, 4, 0)
#. (2, 8, 0, 0)
## collapse((0, 2, 2, 4))
#. (2, 2, 4, 0)
#. (4, 4, 0, 0)
## collapse((2, 2, 2, 4))
#. (4, 2, 4, 0)
## collapse((2, 2, 4, 4))
#. (4, 4, 4, 0)
#. (4, 8, 0, 0)


if __name__ == '__main__':
    main()
