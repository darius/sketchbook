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
    os.system('stty {} -echo'.format(name))
    write(home + clear_to_bottom)
    yield
    sys.stdout.write(cursor_show)
    os.system('stty sane') # XXX save and restore instead

def write(s):
    sys.stdout.write(s.replace('\n', newline))


# Rendering with styles and cursor marker.
# I know, this is way too much code.

cursor = object()

def render(scene):
    out = sys.stdout.write
    out(home_and_hide)
    cursor_seen = top_paint(scene)
    # TODO: save *this* cursor position too and restore it on mode-exit
    # XXX the clear_to_bottom works only in Python 2, not 3.
    #   Some unicode encoding thing?
    out(clear_to_bottom)
    if cursor_seen:
        out(restore_and_show)
    sys.stdout.flush()

def top_paint(scene):
    state = default_state.copy()
    paint(screen_state, state, scene)
    assert state == default_state
    paint(screen_state, state, '')
    assert state == default_state
    assert screen_state.fg == default_state.fg
    assert screen_state.bg == default_state.bg
    assert screen_state.styles == default_state.styles
    return screen_state.cursor_seen

home_and_hide    = home + cursor_hide
restore_and_show = cursor_restore + cursor_show
newline          = clear_to_right + '\r\n'

def sgr(num): return '\x1b[%dm' % num

class State(object):
    def __init__(self, fg, bg, styles, cursor_seen):
        self.fg = fg
        self.bg = bg
        self.styles = styles
        self.cursor_seen = cursor_seen
    def copy(self):
        return State(self.fg, self.bg, self.styles, self.cursor_seen)
    def __eq__(self, other):
        return (isinstance(other, State)
                and self.fg == other.fg
                and self.bg == other.bg
                and self.styles == other.styles
                and self.cursor_seen == other.cursor_seen)

def paint(screen, state, scene):
    if isinstance(scene, str):    # XXX py2/3
        if screen.styles != state.styles:
            sys.stdout.write(sgr(0)); screen.fg = 39; screen.bg = 49
            if state.styles & (1 << 1): sys.stdout.write(sgr(1))
            if state.styles & (1 << 4): sys.stdout.write(sgr(4))
            if state.styles & (1 << 5): sys.stdout.write(sgr(5))
            if state.styles & (1 << 7): sys.stdout.write(sgr(7))
            screen.styles = state.styles
        if screen.fg != state.fg:
            sys.stdout.write(sgr(state.fg))
            screen.fg = state.fg
        if screen.bg != state.bg:
            sys.stdout.write(sgr(state.bg))
            screen.bg = state.bg
        sys.stdout.write(scene.replace('\n', newline))
    elif scene is cursor:
        sys.stdout.write(cursor_save)
        screen.cursor_seen = True
    elif hasattr(scene, 'paint'):
        scene.paint(screen, state)
    else:
        for part in scene:
            paint(screen, state, part)

class Painter(object):
    def __init__(self, paint):
        self.paint = paint

def ForegroundColor(code):
    def Attribute(subscene):
        def subpaint(screen, state):
            fg = state.fg
            state.fg = code
            try:
                paint(screen, state, subscene)
            finally:
                state.fg = fg
        return Painter(subpaint)
    return Attribute

def BackgroundColor(code):
    def Attribute(subscene):
        def subpaint(screen, state):
            bg = state.bg
            state.bg = code
            try:
                paint(screen, state, subscene)
            finally:
                state.bg = bg
        return Painter(subpaint)
    return Attribute

def Style(code):
    mask = 1 << code
    def Attribute(subscene):
        def subpaint(screen, state):
            styles = state.styles
            state.styles |= mask
            try:
                paint(screen, state, subscene)
            finally:
                state.styles = styles
        return Painter(subpaint)
    return Attribute

black, red, green, yellow, blue, magenta, cyan, white = map(ForegroundColor, range(30, 38))
fg_default = ForegroundColor(39)
on_black, on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white = map(BackgroundColor, range(40, 48))
on_default = BackgroundColor(49)
bold, underlined, blinking, inverted = map(Style, (1, 4, 5, 7))

default_state = State(39, 49, 0, False)
screen_state  = default_state.copy()


# Keyboard input

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
