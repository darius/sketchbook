"""
Play Sokoban on the tty.
"""

def parse(grid_string):
    lines = grid_string.splitlines()
    assert lines and all(len(line) == len(lines[0]) for line in lines)
    return list(grid_string)

def unparse(grid):
    return ' '.join(grid).replace('\n ', '\r\n')

def play(grid):
    write(ansi_hide_cursor)
    trail = []
    while True:
        write(ansi_clear_screen + unparse(grid) + '\r\n\r\n')
        write("Move with the arrow keys or HJKL. U to undo, Q to quit.\r\n")
        if won(grid): break
        key = read_key().lower()
        if key in 'qx':
            break
        elif key == 'u':
            if trail: grid = trail.pop()
        elif key in directions:
            previously = grid[:]
            push(grid, directions[key])
            if grid != previously: trail.append(previously)
    write(ansi_show_cursor)

def won(grid): return 'o' not in grid

up    = lambda width: -width
down  = lambda width:  width
left  = lambda width: -1
right = lambda width:  1
directions = dict(h    = left, j    = down, k  = up, l     = right,
                  left = left, down = down, up = up, right = right)

def push(grid, direction):
    "Update grid, trying to move the player in the direction."
    i = grid.index('i' if 'i' in grid else 'I')
    d = direction(grid.index('\n')+1)
    move(grid, 'o@', i+d, i+d+d) # First push any neighboring box.
    move(grid, 'iI', i, i+d)     # Then move the player.

def move(grid, thing, src, dst):
    "Move thing from src to dst if possible."
    # N.B. dst is always in bounds when grid[src] in thing because our
    # grids have '#'-borders.
    if grid[src] in thing and grid[dst] in ' .':
        clear(grid, src)
        drop(grid, dst, thing)

def clear(grid, i):
    "Remove any thing (box or player) from position i."
    grid[i] = ' .'[grid[i] in '.@I']

def drop(grid, i, thing):
    "At a clear position, put thing."
    grid[i] = thing['.' == grid[i]]


# Terminal stuff

import os, sys

esc = chr(27)
ansi_clear_screen = esc + '[2J\x1b[H'
ansi_hide_cursor  = esc + '[?25l'
ansi_show_cursor  = esc + '[?25h'
write = sys.stdout.write

def with_raw(reacting):
    os.system('stty raw -echo')
    try:
        reacting()
    finally:
        os.system('stty sane')

keys = {esc+'[A': 'up',    esc+'OA': 'up',
        esc+'[B': 'down',  esc+'OB': 'down',
        esc+'[C': 'right', esc+'OC': 'right',
        esc+'[D': 'left',  esc+'OD': 'left'}
key_prefixes = set(k[:i] for k in keys for i in range(1, len(k)))

def read_key():
    k = sys.stdin.read(1)
    while k in key_prefixes:
        k1 = sys.stdin.read(1)
        if not k1: break
        k += k1
    return keys.get(k, k)


if __name__ == '__main__':
    puzzle = """\
#######
#.i # #
#o@ o #
#   o #
# ..  #
#  @  #
#######"""
    grid = parse(puzzle)
    with_raw(lambda: play(grid))
