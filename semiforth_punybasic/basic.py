"""
BASIC interpreter, inspired by Tiny BASIC.
"""

import bisect, operator
from semiforth import (Parser, Unparsable, primitives, 
                       mkaction, mkprim, mkstacker, null)

def repl():
    print "I am Puny Basic. Enter 'bye' to dismiss me."
    while True:
        try: text = raw_input('> ')
        except EOFError: break
        if text.strip() == 'bye': break
        try: run_line(text)
        except Exception, e:
            # TODO: put the current line# in the prompt instead, if any;
            #  should work nicely with a resumable STOP statement
            print e, ('' if pc is None else 'at line %d' % lines[pc][0])

def run_line(text, rule='top'):
    return Parser(basic_grammar, **primitives)(text, rule)

def run_stmt(text):
    return run_line(text, 'stmt')


lines = []       # A sorted array of (line_number, source_line) pairs.
pc = None        # The program counter: an index into lines[], or None.

def listing():
    for n, line in lines:
        print n, line

def store_line(n, text):
    i = bisect.bisect(lines, (n, ''))
    if i < len(lines) and lines[i][0] == n:
        if text.strip(): lines[i] = (n, text)
        else:            lines.pop(i)
    else:
        if text.strip(): lines.insert(i, (n, text))
    return ()

def goto(n):
    i = bisect.bisect(lines, (n, ''))
    if i < len(lines) and lines[i][0] == n: return i
    else: raise Exception("Missing line", n)

def if_goto(flag, n):
    return goto(n) if flag else next_line(pc)

def next_line(a_pc):
    return None if a_pc is None or a_pc+1 == len(lines) else a_pc+1

def run():
    global pc
    pc = 0 if lines else None
    return_stack[:] = []
    env.clear()
    go()

def go():
    while pc is not None:       # TODO: check for stopped, instead
        step()

def step():
    global pc
    _, line = lines[pc]
    pc, = run_stmt(line)


env = {}
fetch = env.__getitem__
store = env.__setitem__

return_stack = []      # A stack of line numbers of GOSUBs in progress.

def gosub(n):
    target = goto(n)
    return_stack.append(lines[pc][0])
    return target

def do_return():
    return next_line(goto(return_stack.pop()))
    

primitives['fetch']   = mkprim(1, fetch)
primitives['store']   = mkstacker(2, lambda var, val: null(store(var, val)))
primitives['input']   = mkstacker(1, lambda var: null(store(var, int(raw_input(var+'? ')))))
primitives['store_line'] = mkstacker(2, store_line)
primitives['goto']    = mkprim(1, goto)
primitives['if_goto'] = mkprim(2, if_goto)
primitives['gosub']   = mkprim(1, gosub)
primitives['return']  = mkprim(0, do_return)
primitives['eq']      = mkprim(2, operator.eq)
primitives['ne']      = mkprim(2, operator.ne)
primitives['<']       = mkprim(2, operator.lt)
primitives['<=']      = mkprim(2, operator.le)
primitives['>=']      = mkprim(2, operator.ge)
primitives['>']       = mkprim(2, operator.gt)
primitives['end']     = mkprim(0, lambda: None)
primitives['list']    = mkaction(listing)
primitives['run']     = mkaction(run)
primitives['next']    = mkprim(0, lambda: next_line(pc))

basic_grammar = r"""
top       = _ (\d+) _ int (.*)            $ store_line
          | _ run\b _                     $ run
          | _ stmt
          | _                             $

stmt      = print\b _ maybemore           $ next
          | \? _      maybemore           $ next
          | let\b _ id \= _ exp0  store   $ next
          | input\b _ id          input   $ next
          | goto\b _ exp0                 $ goto
          | if\b _ relexp then\b _ exp0   $ if_goto
          | gosub\b _ exp0                $ gosub
          | return\b _                    $ return
          | end\b _                       $ end
          | list\b _              list    $ next
          | rem\b .*                      $ next

writes    = \; _       maybemore
          | \, _ space maybemore
          | newline
maybemore = display writes
          | 
display   = exp0 write
          | " string " _
string    = "(")   write string
          | ([^"]) write string
          | 

relexp    = exp0 relop
relop     = \<> _ exp0 neq
          | \<= _ exp0 <=
          | \<  _ exp0 <
          | \=  _ exp0 eq
          | \>= _ exp0 >=
          | \>  _ exp0 >

exp0      = exp1 terms
terms     = \+ _ exp1 +   terms
          | \- _ exp1 -   terms
          | 
exp1      = exp2 factors
factors   = \* _ exp2 *   factors
          | \/ _ exp2 //  factors
          | \% _ exp2 %   factors
          | 
exp2      = primary raising
raising   = \^ _ exp2 **
          | 

primary   = \- _ exp1 negate
          | (\d+) _ int
          | id fetch
          | \( _ exp0 \) _

id        = ([a-z]) _
_         = \s*
"""

if __name__ == '__main__':
    repl()

## run_line('100 print "hello"')
#. ()
## lines
#. [(100, 'print "hello"')]
## run_line('100 print "goodbye"')
#. ()
## lines
#. [(100, 'print "goodbye"')]
## run_line('99 print 42,')
#. ()
## lines
#. [(99, 'print 42,'), (100, 'print "goodbye"')]

## run_line('run')
#. 42 goodbye
#. ()


## run_line('print')
#. (None,)
## run_line('let x = 5')
#. (None,)
## run_line('print x*x')
#. 25
#. (None,)
## run_line('print 2+2; -5, "hi"')
#. 4-5 hi
#. (None,)
## run_line('? 42 * (5-3) + -2^2')
#. 80
#. (None,)
## run_line('print 2^3^2, ')
#. 512 
#. (None,)
## run_line('print 5-3-1')
#. 1
#. (None,)
## run_line('print 3/2')
#. 1
#. (None,)
