"""
Type something in while a stopwatch counts, and show your typing speed.
"""

import time

import sturm

def main(argv):
    with sturm.cbreak_mode():
        interact()
    return 0

def interact():
    start = time.time()
    strokes = ''
    while True:
        banner = '%5.1f' % (time.time() - start)
        sturm.render(banner + '\n\n' + strokes)
        key = sturm.get_key(timeout=0.1)
        if key is None:
            continue
        elif key == 'q':
            break
        strokes += key

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
