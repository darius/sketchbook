"""
Peter Norvig's lis.py hacked with lower-level data representations.
Plus a few other tweaks like support for the 'quote' read macro.
To do: add a garbage collector and clean up the added code.
This will be more work than I thought because the recursive eval
needs to make its local variables known to the garbage collector --
silly of me to have forgotten that. (The issue didn't come up in 
awklisp because it was already using a stack.)
"""

from __future__ import division

def tag_of(x):
    return x[0]

def untag(tag, x):
    assert x[0] == tag
    return x[1]

nil = 'nil', None

false = 'bool', False
true  = 'bool', True
def Bool(flag): return true if flag else false
def tester(op): return 'prim', lambda *args: Bool(op(*args))

def arith(op):
    return 'prim', lambda *args: ('num',
                                  op(*[untag('num', arg) for arg in args]))

def unnum(op):
    return lambda *args: op(*[untag('num', arg) for arg in args])

symbols = {}
def Symbol(name):
    if name not in symbols:
        symbols[name] = 'symbol', name
    return symbols[name]

heap_size = 1*1000
cars = [None] * heap_size
cdrs = [None] * heap_size
heap_ptr = 0

def cons(a, d):
    global heap_ptr
    if heap_size <= heap_ptr:
        collect_garbage(a, d)
    cars[heap_ptr] = a
    cdrs[heap_ptr] = d
    heap_ptr += 1
    return 'pair', heap_ptr - 1

def collect_garbage(a, d):
    assert False                # XXX

def car(x): return cars[untag('pair', x)]
def cdr(x): return cdrs[untag('pair', x)]

def explode(x):
    "Make a Python list from a Lisp list."
    result = []
    while x is not nil:
        result.append(car(x))
        x = cdr(x)
    return result

def implode(x):
    "Make a Lisp list from a Python list."
    result = nil
    for v in reversed(x):
        result = cons(v, result)
    return result

################ Lispy: Scheme Interpreter in Python

### (c) Peter Norvig, 2010; See http://norvig.com/lispy.html

################ Symbol, Env classes

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms,args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        if var in self: return self
        if not self.outer: assert False, var
        return self.outer.find(var)

def add_globals(env):
    "Add some Scheme standard procedures to an environment."
    import math, operator as op
    env.update((Symbol(name), arith(f))  # sin, sqrt, ...
               for name, f in vars(math).items()
               if type(f) == type(op.add))
    env.update(
     {Symbol('+'): arith(op.add),
      Symbol('-'): arith(op.sub),
      Symbol('*'): arith(op.mul),
      Symbol('/'): arith(op.div),
      Symbol('not'): tester(lambda x: x is false),
      Symbol('>'): tester(unnum(op.gt)),
      Symbol('<'): tester(unnum(op.lt)),
      Symbol('>='): tester(unnum(op.ge)),
      Symbol('<='): tester(unnum(op.le)),
      Symbol('='): tester(unnum(op.eq)),
#      Symbol('equal?'): op.eq,
      Symbol('eq?'): tester(op.is_),
#      Symbol('length'): len, 
      Symbol('cons'): ('prim', cons),
      Symbol('car'): ('prim', car),
      Symbol('cdr'): ('prim', cdr),
#      Symbol('append'): op.add,  
#      Symbol('list'): lambda *x: reduce(cons, ...
      Symbol('pair?'): tester(lambda x: tag_of(x) == 'pair'),
      Symbol('null?'): tester(lambda x: x is nil),
      Symbol('symbol?'): tester(lambda x:  tag_of(x) == 'symbol')})
    return env

global_env = add_globals(Env())

def isa(x, tag): return tag_of(x) == tag

################ eval

quote_, if_, set_, define_, lambda_, begin_ = (
    map(Symbol, 'quote if set! define lambda begin'.split()))

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isa(x, 'symbol'):             # variable reference
        return env.find(x)[x]
    elif not isa(x, 'pair'):         # constant literal
        return x                
    elif car(x) is quote_:          # (quote exp)
        (_, exp) = explode(x)
        return exp
    elif car(x) is if_:             # (if test conseq alt)
        (_, test, conseq, alt) = explode(x)
        return eval((alt if eval(test, env) is false else conseq), env)
    elif car(x) is set_:           # (set! var exp)
        (_, var, exp) = explode(x)
        env.find(var)[var] = eval(exp, env)
        return false
    elif car(x) is define_:         # (define var exp)
        (_, var, exp) = explode(x)
        env[var] = eval(exp, env)
        return false
    elif car(x) is lambda_:         # (lambda (var*) exp)
        (_, vars, exp) = explode(x)
        return 'fun', untag('pair', implode([exp, vars, env]))
    elif car(x) is begin_:          # (begin exp*)
        val = false
        for exp in explode(x)[1:]:
            val = eval(exp, env)
        return val
    else:                          # (proc exp*)
        args = [eval(exp, env) for exp in explode(x)]
        proc = args.pop(0)
        if isa(proc, 'prim'):
            return untag('prim', proc)(*args)
        if isa(proc, 'fun'):
            (exp, vars, env) = explode(('pair', untag('fun', proc)))
            return eval(exp, Env(explode(vars), args, env))
        raise ValueError("Call to non-procedure")

################ parse, read, and user interaction

def read(s):
    "Read a Scheme expression from a string."
    return read_from(tokenize(s))

parse = read

def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(',' ( ').replace(')',' ) ').replace("'", " ' ").split()

def read_from(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from(tokens))
        tokens.pop(0) # pop off ')'
        return implode(L)
    elif ')' == token:
        raise SyntaxError('unexpected )')
    elif "'" == token:
        return implode([quote_, read_from(tokens)])
    else:
        return atom(token)

def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try: return 'num', int(token)
    except ValueError:
        try: return 'num', float(token)
        except ValueError:
            return Symbol(token)

def to_string(x):
    "Convert a Python object back into a Lisp-readable string."
    if x is nil:         return '()'
    if isa(x, 'bool'):   return '#t' if untag('bool', x) else '#f'
    if isa(x, 'num'):    return str(untag('num', x))
    if isa(x, 'symbol'): return str(untag('symbol', x))
    if isa(x, 'pair'):   return '('+' '.join(map(to_string, explode(x)))+')' 
    if isa(x, 'fun'):    return '#<fun>' # XXX more
    if isa(x, 'prim'):   return '#<'+str(untag('prim', x))+'>' 
    assert False

def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        val = eval(parse(raw_input(prompt)))
        if val is not None: print to_string(val)
