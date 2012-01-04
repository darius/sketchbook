import os, sys
import ansi

filename = sys.argv[1]
cols, rows = 80, 24             # XXX query window size somehow

try:            f = open(filename)
except IOError: text = ''
else:           text = f.read(); f.close()

def C(ch): return chr(ord(ch.upper()) - 64)

point, origin = 0, 0

def redisplay(new_origin, write):
    write(ansi.hide_cursor + ansi.home)
    p, x, y = new_origin, 0, 0
    found_point = False
    while y < rows:
        if p == point:
            write(ansi.save_cursor_pos)
            found_point = True
        if p == len(text):
            write(ansi.clear_to_bottom)
            break
        ch = text[p]
        if ch == '\n':
            write(ansi.clear_to_eol + '\r\n')
            x, y = 0, y+1
        else:
            if ch == '\t':
                glyphs = ' ' * (8 - x % 8)
            elif 32 <= ord(ch) < 126:
                glyphs = ch
            else:
                glyphs = '\\%03o' % ord(ch)
            for glyph in glyphs:
                write(glyph)
                x += 1
                if x == cols: x, y = 0, y+1
        p += 1
    if found_point:
        write(ansi.show_cursor + ansi.restore_cursor_pos)
    return found_point

def move_char(d):
    global point
    point = max(0, min(point + d, len(text)))

def insert(s):
    global text, point
    text = text[:point] + s + text[point:]
    point += len(s)

keybindings = {}

def set_key(ch, fn):
    keybindings[ch] = fn
    return fn

def bind(ch): return lambda fn: set_key(ch, fn)

@bind(chr(127))
def backward_delete_char():
    global text, point
    if 0 == point: return
    text = text[:point-1] + text[point:]
    point -= 1

@bind(C('b'))
def backward_move_char(): move_char(-1)

@bind(C('f'))
def forward_move_char(): move_char(1)

os.system('stty raw -echo')
try:

    sys.stdout.write(ansi.clear_screen)
    while True:

        if not redisplay(origin, lambda s: None):
            for origin in range(max(0, point - cols * rows), point+1):
                if redisplay(origin, lambda s: None):
                    break
        redisplay(origin, sys.stdout.write)

        ch = sys.stdin.read(1)
        if ch in ('', C('x'), C('q')):
            break
        if ch in keybindings:
            keybindings[ch]()
        else:
            insert('\n' if ch == '\r' else ch)

    if ch != C('q'):
        open(filename, 'w').write(text)

finally:
    os.system('stty sane')
