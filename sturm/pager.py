"""
Like `more`, but really crude.
XXX it's not nice of this program to clear the screen.
"""

import sys
import sturm

def main(argv):
    with sturm.cbreak_mode():
        filenames = argv[1:]
        if filenames:
            for filename in filenames:
                with open(filename) as f:
                    page(f)
                # XXX should we do something in between files?
        else:
            page(sys.stdin)
    return 0

row, col = 0, 0

def page(f):
    global row, col
    while True:
        c = f.read(1)
        if not c: return
        write(c)
        if sturm.ROWS-1 <= row:
            sturm.write("--more--")
            k = sturm.get_key()
            sturm.write('\b' * len("--more--"))  # XXX clear it too
            if k == 'q':
                sys.exit()
            row, col = 0, 0

def write(c):
    global row, col
    if c == '\n':
        sturm.write(c)
        row, col = row+1, 0
    else:                       # XXX tabs too
        if not is_printable(c):
            c = '?'             # XXX color it or something
        sturm.write(c)
        col += 1
        if sturm.COLS <= col:
            sturm.write('\n')
            row, col = row+1, 0

def is_printable(c):
    return 32 <= ord(c) < 127   # XXX unicode

if __name__ == '__main__':
    sys.exit(main(sys.argv))
