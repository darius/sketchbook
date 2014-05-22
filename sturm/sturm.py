"""
Simple console terminal interaction.
TODO: example apps to see what's missing
TODO: app that needs timed events, e.g. tetris

Thanks to Dave Long for helpful discussion of the key-reading
code.
"""

import contextlib, os, sys

# Reading and writing the console:
#
# The most standard way to code a console app like this is with curses,
# but curses kind of earns its name. And there are better libraries
# now, but I'm not familiar with them yet. (Soon!) Maybe you'll enjoy seeing
# how to do without? We use http://en.wikipedia.org/wiki/ANSI_escape_code
# and raw mode
# http://en.wikipedia.org/wiki/Seventh_Edition_Unix_terminal_interface#Input_modes
#
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

@contextlib.contextmanager
def mode(name):       # 'raw' or 'cbreak'
    # It looks like this could be done with the tty and termios
    # modules instead, but at least my code is shorter:
    # http://stackoverflow.com/questions/1394956/how-to-do-hit-any-key-in-python
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

def write(s):
    sys.stdout.write(s.replace('\n', ansi_clear_to_right + '\r\n'))


# Arrow keys are encoded as escape sequences:
key_map = {esc+'[A': 'up',    esc+'OA': 'up',
           esc+'[B': 'down',  esc+'OB': 'down',
           esc+'[C': 'right', esc+'OC': 'right',
           esc+'[D': 'left',  esc+'OD': 'left'}
keymap_prefixes = set(k[:i] for k in key_map for i in range(1, len(k)))

def get_key():
    keys = get_raw_key()
    while keys in keymap_prefixes:
        keys += get_raw_key()
    if keys in key_map:
        return key_map[keys]
    else:
        key_stack.extend(reversed(keys))
        return get_raw_key()

def get_raw_key():              # XXX 'raw' is a confusing name here
    return key_stack.pop() if key_stack else sys.stdin.read(1)

key_stack = []
