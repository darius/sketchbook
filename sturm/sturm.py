"""
Simple console terminal interaction.
"""

import contextlib, os, select, sys, time

ROWS, COLS = 24, 80

def note_screen_size():
    global ROWS, COLS
    ROWS, COLS = map(int, os.popen('stty size', 'r').read().split())

# It'd be a little simpler to clear the screen before each repaint,
# but that causes occasional flicker, so we instead start each repaint
# with ansi_home and then incrementally clear_to_right on each line, and
# finally clear_to_bottom.
#
# OTOH it's still noticeably bad if you repaint many times a second;
# the next step up in complexity would be to remember, after each
# frame, a list of the lines showing on the screen, and then only send
# to the screen the lines that change in the new frame.

esc = chr(27)
ansi_home            = esc + '[H' # Go to the top left.
ansi_clear_to_right  = esc + '[K' # Erase the rest of the line.
ansi_clear_to_bottom = esc + '[J' # Erase the rest of the screen.
ansi_hide_cursor     = esc + '[?25l'
ansi_show_cursor     = esc + '[?25h'

def raw_mode():    return mode('raw')
def cbreak_mode(): return mode('cbreak')

@contextlib.contextmanager
def mode(name):       # 'raw' or 'cbreak'
    # It looks like this could be done with the tty and termios
    # modules instead, but at least my code is shorter:
    # http://stackoverflow.com/questions/1394956/how-to-do-hit-any-key-in-python
    note_screen_size()
    os.system('stty {} -echo'.format(name))
    write(ansi_home + ansi_clear_to_bottom)
    try:
        yield
    finally:
        os.system('stty sane') # XXX save and restore instead

def render(string):
    write(ansi_home + ansi_hide_cursor)
    write(string)
    write(ansi_clear_to_bottom + ansi_show_cursor) # XXX TODO: show optional, placed where wanted
    # XXX the clear_to_bottom works only in Python 2, not 3.
    #   Some unicode encoding thing?
    sys.stdout.flush()

def write(s):
    sys.stdout.write(s.replace('\n', ansi_clear_to_right + '\r\n'))


# Arrow keys, etc., are encoded as escape sequences:
key_map = {esc+'[1~': 'home',  esc+'[A': 'up',    esc+'OA': 'up',
           esc+'[2~': 'ins',   esc+'[B': 'down',  esc+'OB': 'down',
           esc+'[3~': 'del',   esc+'[C': 'right', esc+'OC': 'right',
           esc+'[4~': 'end',   esc+'[D': 'left',  esc+'OD': 'left',
           esc+'[5~': 'pgup',   
           esc+'[6~': 'pgdn',
           chr(127):  'backspace'}
keymap_prefixes = set(k[:i] for k in key_map for i in range(1, len(k)))
# N.B. in raw mode, the enter key is '\r'; in cbreak, it's '\n'.
# Should we just let the client deal with that?
# TODO: detect bare escape (with no following char-codes available yet)

def get_key(timeout=None):
    deadline = None if timeout is None else time.time() + timeout
    keys = get_key_unmapped(deadline)
    if keys is None:
        return None
    while keys in keymap_prefixes:
        key = get_key_unmapped(deadline)
        if key is None:
            key_stack.extend(reversed(keys))
            return None
        keys += key
    if keys in key_map:
        return key_map[keys]
    else:
        key_stack.extend(reversed(keys))
        return key_stack.pop()

def get_key_unmapped(deadline):
    return key_stack.pop() if key_stack else get_key_on_deadline(deadline)

key_stack = []

def get_key_on_deadline(deadline):
    if deadline is None or wait_for_input(sys.stdin.fileno(), deadline):
        return sys.stdin.read(1)
    else:
        return None

def wait_for_input(fd, deadline):
    "Return true if fd is ready to read; wait till deadline at latest."
    while True:
        r, w, e = [fd], [], [fd]
        timeout = max(0, deadline - time.time())
        try:
            r, w, e = select.select(r, w, e, timeout)
        except select.error as err:
            if err[0] == errno.EINTR:
                continue
            raise
        return not not (r or e)
