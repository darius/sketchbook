"""
Like `more`, but really crude.
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

rows, cols = 25, 80             # XXX query for them
row, col = 0, 0

def page(f):
    while True:
        c = f.read(1)
        if not c: return
        write(c)
        if rows-1 <= row:
            sturm.write("--more--")
            k = sturm.get_key()
            sturm.write('\b' * len("--more--"))  # XXX clear it too
            if k == 'q':
                sys.exit()
            global row, col
            row, col = 0, 0

def write(c):
    global row, col
    sturm.write(c)
    if c == '\n':
        row, col = row+1, 0
    else:
        col += 1

if __name__ == '__main__':
    sys.exit(main(sys.argv))
