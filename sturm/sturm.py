"""
Simple console terminal interaction.
"""

import contextlib, os, select, sys, time

ROWS, COLS = 24, 80

def note_screen_size():
    global ROWS, COLS
    ROWS, COLS = map(int, os.popen('stty -F /dev/tty size', 'r').read().split())

# It'd be a little simpler to clear the screen before each repaint,
# but that causes occasional flicker, so we instead start each repaint
# with home and then incrementally clear_to_right on each line, and
# finally clear_to_bottom.
#
# OTOH it's still noticeably bad if you repaint many times a second;
# the next step up in complexity would be to remember, after each
# frame, a list of the lines showing on the screen, and then only send
# to the screen the lines that change in the new frame.

esc = chr(27)
home            = esc + '[H' # Go to the top left.
clear_to_right  = esc + '[K' # Erase the rest of the line.
clear_to_bottom = esc + '[J' # Erase the rest of the screen.
cursor_hide     = esc + '[?25l'
cursor_show     = esc + '[?25h'
cursor_save     = esc + '[s'
cursor_restore  = esc + '[u'

def raw_mode():    return mode('raw')
def cbreak_mode(): return mode('cbreak')

@contextlib.contextmanager
def mode(name):       # 'raw' or 'cbreak'
    # It looks like this could be done with the tty and termios
    # modules instead, but at least my code is shorter:
    # http://stackoverflow.com/questions/1394956/how-to-do-hit-any-key-in-python
    note_screen_size()
    os.system('stty -F /dev/tty {} -echo'.format(name))
    write(home + clear_to_bottom)
    yield
    sys.stdout.write(cursor_show)
    os.system('stty -F /dev/tty sane') # XXX save and restore instead

cursor = object()

def render(scene):
    cursor_seen = False
    out = sys.stdout.write
    out(home_and_hide)
    for part in scene:
        if part is cursor:
            cursor_seen = True
            out(cursor_save)
        else:
            out(part.replace('\n', newline))
    # TODO: save *this* cursor position too and restore it on mode-exit
    # XXX the clear_to_bottom works only in Python 2, not 3.
    #   Some unicode encoding thing?
    out(clear_to_bottom)
    if cursor_seen:
        out(restore_and_show)
    sys.stdout.flush()

home_and_hide    = home + cursor_hide
restore_and_show = cursor_restore + cursor_show
newline          = clear_to_right + '\r\n'

def write(s):
    sys.stdout.write(s.replace('\n', newline))


# Arrow keys, etc., are encoded as escape sequences:
key_map = {chr(127): 'backspace',
           esc+'[1~': 'home',  esc+'[A': 'up',    esc+'OA': 'up',
           esc+'[2~': 'ins',   esc+'[B': 'down',  esc+'OB': 'down',
           esc+'[3~': 'del',   esc+'[C': 'right', esc+'OC': 'right',
           esc+'[4~': 'end',   esc+'[D': 'left',  esc+'OD': 'left',
           esc+'[5~': 'pgup',  
           esc+'[6~': 'pgdn',  
           esc+'[17~': 'f6',   esc+'[20~': 'f9',  esc+'[23~': 'f11',
           esc+'[18~': 'f7',   esc+'[21~': 'f10', esc+'[24~': 'f12',
           esc+'[19~': 'f8'}
key_map.update({esc+'[1%d~'%n: 'f%d'%n for n in range(1, 6)})
keymap_prefixes = set(k[:i] for k in key_map for i in range(1, len(k)))
# N.B. in raw mode, the enter key is '\r'; in cbreak, it's '\n'.
# Just let the client deal with that, I guess.

def get_key(timeout=None):
    keys = get_key_unmapped(timeout)
    if keys is None:
        return None
    while keys in keymap_prefixes:
        key = get_key_unmapped(0)
        if key is None:
            # We assume the bytes of a mapped key-sequence must all be
            # available together; if not, the user must have hit the
            # escape key themself, and we'll just return that.
            break
        keys += key
    if keys in key_map:
        return key_map[keys]
    else:
        key_stack.extend(reversed(keys))
        return key_stack.pop()

def get_key_unmapped(timeout):
    return key_stack.pop() if key_stack else get_key_timed(timeout)

key_stack = []

def get_key_timed(timeout):
    if timeout is None or wait_for_input(sys.stdin.fileno(), timeout):
        return sys.stdin.read(1)
    else:
        return None

def wait_for_input(fd, timeout):
    "Return true if fd is ready to read; wait for timeout at most."
    while True:
        r, w, e = [fd], [], [fd]
        try:
            r, w, e = select.select(r, w, e, timeout)
        except select.error as err:
            if err[0] == errno.EINTR:
                timeout = 0  # TODO: is it worth the trouble to adjust this correctly?
                continue
            raise
        return not not (r or e)
