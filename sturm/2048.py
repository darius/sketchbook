"""
Modeled after https://github.com/fewf/curtsies_2048
"""

import random

import sturm

def main():
    board = make_board()
    with sturm.cbreak_mode():
        while True:
            game_over = all(move(board) == board for move in [up,down,left,right])
            score = "You win!" if is_won(board) else "You lose!" if game_over else ""
            sturm.render("Use the arrow keys, or 'q' to quit.\n\n"
                         + view(board) + "\n\n"
                         + score + "\n")
            if game_over: break
            key = sturm.get_key()
            if key == 'q': break
            elif key in globals(): # Hacky hacky, sorry. :P
                slid_board = globals()[key](board)
                if slid_board != board:
                    board = plop(slid_board, 2 if random.random() < .9 else 4)

# A board is a tuple of 4 rows;
# a row is a tuple of 4 values;
# a value is 0 for empty, or a positive number.

def make_board(): return plop(plop(empty_board, 2), 2)

empty_board = ((0,)*4,)*4

# Pre: board has at least one empty square.
def plop(board, v):
    assert not all(all(row) for row in board)
    while True:
        r, c = random.randint(0, 3), random.randint(0, 3)
        if board[r][c] == 0:
            return update(board, (r, c), v)

def update(board, pos, new_v):
    return tuple(tuple(new_v if (r,c) == pos else v
                       for c, v in enumerate(row))
                 for r, row in enumerate(board))

def view(board):
    return '\n\n'.join(' '.join(('%d' % v if v else '.').center(4)
                                for v in row)
                       for row in board)

## print(view(update(empty_board, (3, 2), 4)))
#.  .    .    .    .  
#. 
#.  .    .    .    .  
#. 
#.  .    .    .    .  
#. 
#.  .    .    4    .  
## is_won(update(empty_board, (3, 2), 2048))
#. True

def is_won(board):  return any(row.count(2048) for row in board)

# Arrow-key actions:
def left(board):  return tuple(map(collapse, board))
def right(board): return fliph(left(fliph(board)))
def up(board):    return flipd(left(flipd(board)))
def down(board):  return flipd(right(flipd(board)))

def flipv(board): return board[::-1]                # vertical flip
def flipd(board): return tuple(zip(*board))         # diagonal
def fliph(board): return flipd(flipv(flipd(board))) # horizontal

def collapse(row):
    i, vs = 0, [0]*4
    for v in filter(None, row):
        if vs[i] != v and vs[i]: i += 1
        vs[i] += v
        if vs[i] == v+v:         i += 1
    return tuple(vs)

## collapse((0, 0, 0, 0))
#. (0, 0, 0, 0)
## collapse((0, 0, 0, 2))
#. (2, 0, 0, 0)
## collapse((0, 2, 0, 2))
#. (4, 0, 0, 0)
## collapse((0, 2, 4, 4))
#. (2, 8, 0, 0)
## collapse((0, 2, 2, 4))
#. (4, 4, 0, 0)
## collapse((2, 2, 2, 4))
#. (4, 2, 4, 0)
## collapse((2, 2, 4, 4))
#. (4, 8, 0, 0)

if __name__ == '__main__':
    main()
