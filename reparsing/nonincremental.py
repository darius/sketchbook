"""
Baseline, not yet incremental.
"""

from parson import Grammar as ParsonGrammar

# Parser objects
# You call a parser p by p(parsing, i) and get back di, far, ops.
# parsing: a Parsing object -- holds the input and the chart (the memo table)
# i: what input offset to start parsing p from
# di: None on failure, displacement on success
# far: how far forward in parsing we looked from i
# ops: tuple of operations encoding the semantics

class Call(object):
    def __init__(self, rule):
        self.rule = rule
    def __call__(self, parsing, i):
        return parsing.call(i, self.rule)

class Fail(object):
    def __call__(self, parsing, i):
        return None, 0, ()

class Empty(object):
    def __call__(self, parsing, i):
        return 0, 0, ()

fail = Fail()
empty = Empty()

class Do(object):
    def __init__(self, name):
        self.ops = (('do',name),)
    def __call__(self, parsing, i):
        return 0, 0, self.ops

class Range(object):
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
    def __call__(self, parsing, i):
        ch = parsing.text(i, i+1)
        if ch == '':
            return None, 0, ()
        else:
            return (1 if self.lo <= ch <= self.hi else None), 1, ()

class Nix(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        di, far, ops = self.p(parsing, i)
        return (0 if di is None else None), far, ()

class Grab(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        di, far, ops = result = self.p(parsing, i)
        if di is None:
            return result
        else:
            return di, far, ops + (('grab',i,di),)

class Seclude(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        di, far, ops = result = self.p(parsing, i)
        if di is None:
            return result
        else:
            return di, far, (('[',),) + ops + ((']',),)

class Either(object):
    def __init__(self, p, q):
        self.p, self.q = p, q
    def __call__(self, parsing, i):
        di, far1, ops = result = self.p(parsing, i)
        if di is not None: return result
        di, far2, ops = self.q(parsing, i)
        return di, max(far1, far2), ops

class Chain(object):
    def __init__(self, p, q):
        self.p, self.q = p, q
    def __call__(self, parsing, i):
        di1, far1, ops1 = result1 = self.p(parsing, i)
        if di1 is None: return result1
        di2, far2, ops2 = self.q(parsing, i+di1)
        far = max(far1, di1+far2)
        if di2 is None: return None, far, ()
        else:           return di1+di2, far, ops1+ops2

class Repeat(object):
    def __init__(self, p):
        self.p = p
    def __call__(self, parsing, i):
        di, far, ops = 0, 0, ()
        while True:
            di2, far2, ops2 = self.p(parsing, i+di)
            far = max(far, di+far2)
            if di2 is None:
                return di, far, ops
            di += di2
            ops += ops2
    

# Derived parsers

def Literal(s):
    result = empty
    for ch in reversed(s):
        parser = Range(ch, ch)
        result = parser if result is empty else Chain(parser, result)
    return result

def Maybe(p):
    return Either(p, empty)

def Plus(p, separator=None):
    if separator is None:
        return Chain(p, Repeat(p))
    else:
        return Chain(p, Repeat(Chain(separator, p)))

def Star(p, separator=None):
    if separator is None:
        return Repeat(p)
    else:
        return Maybe(Plus(p, separator))


# Concrete syntax

meta_grammar = r""" rule+ :end.

rule         :  name ('='             pe
                     |':'~whitespace [pe :Seclude])
                '.'                        :hug.

pe           :  term ('|' pe :Either)?
             |                             :Empty.
term         :  factor (term :Chain)?.
factor       :  '!' factor                 :Nix
             |  primary ('**' primary :Star
                        |'++' primary :Plus
                        |'*' :Star
                        |'+' :Plus
                        |'?' :Maybe)?.
primary      :  '(' pe ')'
             |  '[' pe ']'                 :Seclude
             |  '{' pe '}'                 :Grab
             |  qstring ('..' qstring :Range
                        |             :Literal)
             |  ':'~name                   :Do
             |  name                       :Call.

name         :  /([A-Za-z_]\w*)/.

FNORD       ~:  whitespace?.
whitespace  ~:  /(?:\s|#.*)+/.

qstring     ~:  /'/  quoted_char* /'/ FNORD :join.
quoted_char ~:  /\\(.)/ | /([^'])/.
"""
parser_peg = ParsonGrammar(meta_grammar)(**globals())


# Top level

class Grammar(object):
    def __init__(self, grammar_str):
        self.grammar = dict(parser_peg(grammar_str))
    def parsing(self, subject_str):
        return Parsing(self.grammar, subject_str)
    
class Parsing(object):
    def __init__(self, grammar, subject_str):
        self.grammar = grammar
        self.subject = subject_str
        self.chart = [{} for _ in range(len(subject_str)+1)]

    def text(self, lo, hi):
        return self.subject[lo:hi]

    def replace(self, lo, hi, replacement):
        assert lo <= hi <= len(self.subject)
        self.subject = self.subject[:lo] + replacement + self.subject[hi:]
        self.chart = [{} for _ in range(len(self.subject)+1)]

    def parse(self, rule='start'):
        di, far, ops = self.call(0, rule)
        if di is None:
            raise Exception("Unparsable", far, self.subject)
        if di != len(self.subject):
            raise Exception("Incomplete parse", far, self.subject)
        return ops

    def interpret(self, ops, semantics):
        stack = []
        frame = []
        for insn in ops:
            op = insn[0]
            if op == '[':
                stack.append(frame)
                frame = []
            elif op == ']':
                parent = stack.pop()
                parent.extend(frame)
                frame = parent
            elif op == 'do':
                fn = semantics[insn[1]]
                frame[:] = [fn(*frame)]
            elif op == 'grab':
                i, di = insn[1:]
                frame.append(self.subject[i:i+di])
            else:
                assert 0
        assert not stack
        return tuple(frame)

    # Used by parsers, not by clients:
    def call(self, i, rule):
        column = self.chart[i]
        memo = column.get(rule)
        if memo is None:
            column[rule] = cyclic
            column[rule] = memo = self.grammar[rule](self, i)
        elif memo is cyclic:
            raise Exception("Left-recursive rule", rule)
        return memo

cyclic = object()


# Varieties of semantics

def DictSemantics(*dicts):
    result = {}
    for d in dicts: result.update(d)
    return result

base_semantics = DictSemantics(__builtins__)  # TODO Parson conveniences like `hug`

def ModuleSemantics(module):
    # TODO keep up with any updates to the module instead of just copying the dict
    return DictSemantics(module.__dict__)

class ASTSemantics(object):
    def __getitem__(self, name):
        return lambda *args: (name,) + args
    def get(self, name, default=None):
        return self[name]

ast_semantics = ASTSemantics()

class ComboSemantics(object): # TODO is there a dictlike class that already does this?
    def __init__(self, *semanticses):
        self.sems = list(semanticses)
        self.sems.reverse()
    def __getitem__(self, name):
        value = self.get(name)
        if value is None: raise KeyError(name)
        return value
    def get(self, name, default=None):
        for sem in self.sems:
            value = sem.get(name)
            if value is not None:
                return value
        return default


# Example

import operator

calc = r"""
start =  exp0.
exp0  :  exp1 ( '+'  exp1 :add
              | '-'  exp1 :sub )*.
exp1  :  exp2 ( '*'  exp2 :mul
              | '//' exp2 :div
              | '/'  exp2 :truediv
              | '%'  exp2 :mod )*.
exp2  :  exp3 ( '^'  exp2 :pow )?.
exp3  :  '(' exp0 ')'
      |  '-' exp1 :neg
      |  {digit+} :int.
digit =  '0'..'9'.
"""
calc_grammar = Grammar(calc)
calc_semantics = ComboSemantics(base_semantics, ModuleSemantics(operator))

def calc(s):
    parser = calc_grammar.parsing(s)
    return parser.interpret(parser.parse(), calc_semantics)[0]

## calc('(2-3)*4')
#. -4

## s0 = '2*8-5/2'
## calc(s0)
#. 13.5

## parsing = calc_grammar.parsing(s0)
## parse = parsing.parse()
## parsing.interpret(parse, calc_semantics)
#. (13.5,)
## parsing = calc_grammar.parsing(s0)
## parsing.interpret(parse, ast_semantics)
#. (('sub', ('mul', ('int', '2'), ('int', '8')), ('truediv', ('int', '5'), ('int', '2'))),)
## parsing.replace(1, 2, '0')
## parsing.text(0, len(parsing.subject))
#. '208-5/2'
## parsing.interpret(parsing.parse(), calc_semantics)
#. (205.5,)
