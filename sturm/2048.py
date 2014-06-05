"""
Modeled after https://github.com/fewf/curtsies_2048
"""

import random, time

import sturm

def main():
    with sturm.cbreak_mode():
        board = make_board()
        while True:
            heading = "Use the arrow keys, or Q to quit.\n\n"
            game_over = not any(list(move(board)) for move in [up,down,left,right])
            score = "You win!" if is_won(board) else "You lose!" if game_over else ""
            sturm.render((heading, view(board), score, "\n"))
            if game_over: break
            key = sturm.get_key()
            if key.upper() == 'Q': break
            elif key in globals(): # Hacky hacky, sorry. :P
                sliding = list(globals()[key](board))
                if sliding:
                    for board in sliding:
                        sturm.render((heading, view(board)))
                        time.sleep(1./30)
                    board = plop(board, 2 if random.random() < .9 else 4)

# A board is a tuple of 4 rows;
# a row is a tuple of 4 values;
# a value is 0 for empty, or a positive number.

def make_board(): return plop(plop(empty_board, 2), 2)

empty_board = ((0,)*4,)*4

def view(board):
    for row in board:
        for v in row:
            yield ' '
            yield colors[v]
        yield '\n\n'

S = sturm
colors = {0:                              '  . ',
          2:    S.yellow(                 '  2 '),
          4:    S.red(                    '  4 '),
          8:    S.blue(                   '  8 '),
          16:   S.green(                  ' 16 '),
          32:   S.bold(S.yellow(          ' 32 ')),
          64:   S.bold(S.red(             ' 64 ')),
          128:  S.bold(S.blue(            '128 ')),
          256:  S.bold(S.green(           '256 ')),
          512:  S.on_blue(S.bold(S.yellow('512 '))),
          1024: S.on_green(S.bold(S.red(  '1024'))),
          2048: S.on_red(S.bold(S.blue(   '2048'))),
          4096: S.bold(                   '4096'),
          8192: S.bold(                   '8192')}

def is_won(board): return any(row.count(2048) for row in board)

# Pre: board is not full.
def plop(board, v):
    return update(board, random_empty_square(board), v)

def random_empty_square(board):
    return random.choice([(r,c)
                          for r, row in enumerate(board)
                          for c, v in enumerate(row)
                          if v == 0])

def update(board, pos, new_v):
    return tuple(tuple(new_v if (r,c) == pos else v
                       for c, v in enumerate(row))
                 for r, row in enumerate(board))

def flipv(board): return board[::-1]                # vertical flip
def flipd(board): return tuple(zip(*board))         # diagonal
def fliph(board): return flipd(flipv(flipd(board))) # horizontal

# Arrow-key actions. Each returns an iterable of boards animating
# the move, empty if there's no move in that direction.
def up(board):    return map(flipd, left( flipd(board)))
def down(board):  return map(flipd, right(flipd(board)))
def right(board): return map(fliph, left( fliph(board)))
def left(board):
    states = tuple((0, row) for row in board)
    while True:
        states = tuple(collapsing(lo, row) for lo,row in states)
        if all(lo == 4 for lo,_ in states):
            break
        yield tuple(row for _,row in states)

def collapsing(lo, row):
    for i in range(lo+1, 4):
        if row[i-1] == 0 and row[i] != 0:
            break
        if lo < i and row[i-1] and row[i-1] == row[i]:
            lo = i
            break
    else:
        return 4, row
    return lo, row[:i-1] + (row[i-1] + row[i],) + row[i+1:] + (0,)


# Let's test collapsing:
def test_left(row):
    for row, in left((row,)):
        print(row)

## test_left((0, 0, 0, 0))
## test_left((2, 4, 2, 2))
#. (2, 4, 4, 0)
## test_left((2, 2, 2, 2))
#. (4, 2, 2, 0)
#. (4, 4, 0, 0)
## test_left((0, 2, 0, 2))
#. (2, 0, 2, 0)
#. (2, 2, 0, 0)
#. (4, 0, 0, 0)
## test_left((2, 0, 2, 0))
#. (2, 2, 0, 0)
#. (4, 0, 0, 0)
## test_left((2, 0, 0, 2))
#. (2, 0, 2, 0)
#. (2, 2, 0, 0)
#. (4, 0, 0, 0)
## test_left((0, 0, 0, 2))
#. (0, 0, 2, 0)
#. (0, 2, 0, 0)
#. (2, 0, 0, 0)
## test_left((0, 2, 4, 4))
#. (2, 4, 4, 0)
#. (2, 8, 0, 0)
## test_left((0, 2, 2, 4))
#. (2, 2, 4, 0)
#. (4, 4, 0, 0)
## test_left((2, 2, 2, 4))
#. (4, 2, 4, 0)
## test_left((2, 2, 4, 4))
#. (4, 4, 4, 0)
#. (4, 8, 0, 0)


if __name__ == '__main__':
    main()
