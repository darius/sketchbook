"""
A UI for cryptogram puzzles.
Incomplete in many ways, the worst being that we can't see the cursor!
"""

import sturm

def main():
    with sturm.cbreak_mode():
        puzzle('nggnpx ng qnja')

def puzzle(cryptogram):
    def my(): pass
    decoder = {}
    my.cursor = 0               # A hack to get a mutable-nonlocal var.
    size = sum(c.isalpha() for c in cryptogram)
    assert 0 < size

    def erase():     del decoder[read_code_at_cursor()]
    def jot(letter): decoder[read_code_at_cursor()] = letter

    def read_code_at_cursor():
        code = ''.join(c for c in cryptogram if c.isalpha())
        return code[my.cursor]

    def shift_by(offset):
        my.cursor = (my.cursor + offset) % size

    def view():
        # Assume 1 line, for now.
        result = '\n'
        result += ''.join(decoder.get(c, ' ') for c in cryptogram) + '\n'
        result += ''.join(' -'[c.isalpha()]   for c in cryptogram) + '\n'
        result += cryptogram + '\n\n'
        return result

    while True:
        sturm.render(view())
        key = sturm.get_key()
        if   key == 'right':
            shift_by(1)
        elif key == 'left':
            shift_by(-1)
        elif key == 'backspace':
            shift_by(-1)
            erase()
        elif key == 'del':
            erase()
            shift_by(1)
        elif key.isalpha():
            jot(key)
            shift_by(1)
        elif key == '\n':
            break

if __name__ == '__main__':
    main()
