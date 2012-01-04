"""
ANSI terminal control
XXX copy me to:
 /home/darius/oldgit/spaced-out/deck-player/ansi.py
 /home/darius/oldgit/spellmell/ansi.py
"""

prefix = '\x1b['

home            = prefix + 'H'
clear_to_bottom = prefix + 'J'
clear_screen    = prefix + '2J' + home
clear_to_eol    = prefix + 'K'

save_cursor_pos = prefix + 's'
restore_cursor_pos = prefix + 'u'

show_cursor = prefix + '?25h'
hide_cursor = prefix + '?25l'

def goto(x, y):
    return prefix + ('%d;%dH' % (y, x))

black, red, green, yellow, blue, magenta, cyan, white = range(8)

def bright(color):
    return 60 + color

def set_foreground(color):
    return (prefix + '%dm') % (30 + color)

def set_background(color):
    return (prefix + '%dm') % (40 + color)
