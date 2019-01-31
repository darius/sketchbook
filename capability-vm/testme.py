"""
Another example program in the nameless Forth dialect.
"""

import cap
import compiling as c

def main():
    p = c.make_program()
    p.constant('emitselector', cap.OutFile.selector)
    p.label('hello')
    p.cstring('Gdkkn,vnqkc \t')
    p.define('c emit', '0 c-push emitselector invoke ;0')
    p.define('n add1', '1 + ;1')
    p.define('p writing',
             'p b@', c.If('( ( p b@ add1) emit)  p 1 + writing;',
                          ';0'))
    p.define('main',
             '( hello writing)  0 syscall')
    p.enter()

main()
#. Hello-world!
