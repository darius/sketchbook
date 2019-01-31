"""
An example program in the nameless Forth dialect.
It's a port of an example from Ichbins which prints
a Lisp list.
"""

import cap
import compiling as c
import stepper

p = c.make_program()

p.constant('nil',    0)
p.constant('a_char', 1)
p.constant('a_pair', 2)

p.variable('hp')
p.label('heap'); p.zeroes(1024)

p.constant('emitselector', cap.OutFile.selector)
p.define('c emit', '0 c-push emitselector invoke ;0')

p.define('cs type',
         'cs b@', c.If('( cs b@ emit)  cs 1 + type;',
                       ';0'))
p.define('newline', '10 emit;')

p.label('blurt'); p.cstring('Panic!\n')
p.define('panic', '( blurt type)  0 syscall')

p.define('x >tag',    '3 and ;1')
p.define('x detag',   '2 >>> ;1')
p.define('v t entag', 'v 2 <<  t or ;1')

p.define('c make-char', 'c a_char entag;')

# TODO: take out "heap +", it's a no-op:
p.define('x <car>', '3 and 1 <<  heap +  @')
p.define('x <cdr>', '3 and 1 <<  heap + 4 +  @')

p.label('nilstr'); p.cstring('()')
p.define('x write',
         c.Cond(('x nil =', 'nilstr type;'),
                ('( x >tag) a_char =',
                 '( $\\ emit)  ( x detag) emit;'),
                ('( x >tag) a_pair -', 'panic;'),
                default='( $( emit) '
                        '( ( x <car>) write) '
                        '( x <cdr>)'))
                                     # XXX need to replace x by top-of-stack
                                     # write falls through to write-tail
p.define('xs write-tail',
         c.Cond(('( xs >tag) a_pair =',
                 '( 32 emit)  ( ( xs <car>) write)  ( xs <cdr>) write-tail;'),
                default='$) emit;'))

p.define('main',
         '( ( $A make-char)  write)  ( newline)',
         '( nil write)  ( newline)',
         '0 syscall')


def main():
    stepper.run(p)

main()
#. \A
#. ()
