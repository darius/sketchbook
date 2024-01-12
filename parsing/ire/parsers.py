"""
Parsing with parser objects
TODO:
- fix scope-mixing bug
  - actually, is there any?
- is there any problem with linking the same parser object into multiple roots?
  (from mutability)
- make ParseOutcome look more like a Match object
- nicer semantics API
- the Extern/link stuff could be simpler
- maybe change %any/%eol to be link-refs to a default global namespace
- maybe modular grammars with link-refs
- more builtin conveniences like %any
"""

import re

class Parsing(object):
    def __init__(self, rules, subject_str):
        self.rules = rules
        self.subject = subject_str
        self.chart = [{} for _ in xrange(len(subject_str)+1)]

    def parse(self, rule_name):
        return ParseOutcome(self, rule_name, self.call(0, self.rules, rule_name))

    def call(self, i, rules, name):
        column = self.chart[i]
        memo = column.get(name) # XXX this mixes the names from different scopes
        if memo is None:
            column[name] = cyclic
            column[name] = memo = rules[name](self, i)
        elif memo is cyclic:
            raise Exception("Left-recursive rule", name)
        return memo

cyclic = object()

class ParseOutcome(object):
    """
    What to do with the result of a parse.
    """
    def __init__(self, parsing, rule, memo):
        self.parsing = parsing
        self.rule = rule        # TODO use this
        self.memo = memo

    def __nonzero__(self):   # N.B. in py3 this'd be __bool__
        "Did the parse succeed?"
        return self.prefix() is not None

    def is_full(self):          # TODO naming
        return self.prefix() == len(self.parsing.subject)

    def prefix(self): # TODO maybe make these properties instead of methods
        return self.memo[0]

    def inspected(self):
        return self.memo[1]

    def assert_full(self):
        if not self.is_full():
            hop, far, ops = self.memo
            if hop is None:
                raise Exception("Unparsable", far, self.parsing.subject)
            else:
                raise Exception("Incomplete parse", hop, self.parsing.subject)

    def groups(self):
        return self.do(base_semantics)

    def do(self, semantics):
        # self.surely_full() # TODO but it's legitimate to interpret a prefix parse...
        if not self: self.assert_full() # Raise a proper exception
        if not isinstance(semantics, dict):
            semantics = DictSemantics(semantics)
        frames = []
        values = []
        ops = self.memo[2]
        for insn in ops:
            op = insn[0]
            if op == '[':
                frames.append(values)
                values = []
            elif op == ']':
                parent = frames.pop()
                parent.extend(values)
                values = parent
            elif op == 'do':
                fn = semantics[insn[1]]
#                print 'fn', fn
#                print 'values', values
#                print type(values)
#                print 'fn(*values)...'
#                print '  ', fn(*values)
                values[:] = [fn(*values)]
            elif op == 'lit':
                values.append(insn[1])
            elif op == 'groups':
                values.extend(insn[1])
            else:
                assert 0
        assert not frames
        return tuple(values)

    def __repr__(self):
        return 'ParseOutcome<%r,%r,%r>' % (self.memo)

def DictSemantics(*dictlikes):
    result = {}
    for d in dictlikes:
        if isinstance(d, type(re)):
            d = d.__dict__   # Treat <type 'module'> like a dict too for convenience.
        result.update(d)
    return result

base_semantics = DictSemantics(__builtins__)  # TODO Parson conveniences like `hug`


# You call a parser p by p(parsing, i) and get back hop, far, ops.
# parsing: a Parsing object -- holds the input and the chart (the memo table)
# i: what input offset to start parsing p from
# hop: None on failure, displacement on success
# far: how far forward from i we got in our best *partial* parse
# ops: tuple of operations encoding the semantics

class Parser(object):
    kids = ()          # overridden in the subclasses with actual kids
    def link(self, rules, kwargs):
        for i, kid in enumerate(self.kids):
            self.kids[i] = self.kids[i].link(rules, kwargs)
        return self

class Extern(Parser):
    def __init__(self, name):
        self.name = name
    def link(self, rules, kwargs):
        return kwargs[self.name].rules[None] # XXX ugh
    def __call__(self, parsing, i):
        raise Exception("Unresolved external ref")

class Call(Parser):
    def __init__(self, name):
        self.name = name
        self.rules = None
    def link(self, rules, kwargs):
        self.rules = rules
        return self
    def __call__(self, parsing, i):
        return parsing.call(i, self.rules, self.name)

class Ops(Parser):
    def __init__(self, ops):
        self.ops = ops
    def __call__(self, parsing, i):
        return 0, 0, self.ops

class FailParser(Parser):
    def __call__(self, parsing, i):
        return None, 0, ()
fail = FailParser()
def Fail(): return fail

def Empty(): return empty
empty = Ops(())

class Any(Parser):
    def __call__(self, parsing, i):
        ch = parsing.subject[i:i+1]
        if ch: return 1, 1, ()
        else:  return None, 0, ()

class Regex(Parser):
    # Pre: regex match length is always 1 on success
    def __init__(self, regex):
        self.re = re.compile(regex)
        self.source = regex
    def __call__(self, parsing, i):
        m = self.re.match(parsing.subject, i)
        if not m: return None, 0, ()
        length = m.end()-i
        groups = m.groups()
        ops = (('groups', groups),) if groups else ()  # the conditional is just an optimization
        return length, length, ops

class Nix(Parser):
    def __init__(self, p):
        self.kids = [p]
    def __call__(self, parsing, i):
        hop, _, ops = self.kids[0](parsing, i)
        if hop is None: return 0, 0, ()
        else:           return None, 0, ()

class Grab(Parser):
    def __init__(self, p):
        self.kids = [p]
    def __call__(self, parsing, i):
        hop, far, ops = result = self.kids[0](parsing, i)
        if hop is None:
            return result
        else:
            return hop, far, ops + (('lit', parsing.subject[i:i+hop]),)

class Seclude(Parser):
    def __init__(self, p):
        self.kids = [p]
    def __call__(self, parsing, i):
        hop, far, ops = result = self.kids[0](parsing, i)
        if hop is None:
            return result
        else:
            return hop, far, (('[',),) + ops + ((']',),)

class Either(Parser):
    def __init__(self, p, q):
        self.kids = [p, q]
    def __call__(self, parsing, i):
        hop, far0, ops = result = self.kids[0](parsing, i)
        if hop is not None: return result
        hop, far1, ops = self.kids[1](parsing, i)
        return hop, max(far0, far1), ops

class Then(Parser):
    def __init__(self, p, q):
        self.kids = [p, q]
    def __call__(self, parsing, i):
        hop0, far0, ops0 = result1 = self.kids[0](parsing, i)
        if hop0 is None: return result1
        hop1, far1, ops1 = self.kids[1](parsing, i+hop0)
        far = max(far0, hop0+far1)
        if hop1 is None: return None, far, ()
        else:            return hop0+hop1, far, ops0+ops1

class Repeat(Parser):
    def __init__(self, p):
        self.kids = [p]
    def __call__(self, parsing, i):
        hop, far, ops = 0, 0, ()
        while True:
            hop2, far2, ops2 = self.kids[0](parsing, i+hop)
            far = max(far, hop+far2)
            if hop2 is None:
                return hop, far, ops
            if hop2 == 0: raise Exception("Stuck on repeat", parsing, i+hop)
            hop += hop2
            ops += ops2
    

# Helpers

def foldr(f, z, xs):
    for x in reversed(xs):
        z = f(x, z)
    return z


# Derived parsers

def Do(name):      return Ops((('do',name),))
def Push(literal): return Ops((('lit',literal),))

def Chain(*ps):  return foldr(Chain2, empty, ps)
def Choice(*ps): return foldr(Choice2, fail, ps)

def Chain2(p, q):
    if p is empty: return q
    if q is empty: return p
    return Then(p, q)

def Choice2(p, q):
    if p is fail: return q
    if q is fail: return p
    return Either(p, q)

def Literal(s):
    return Regex(re.escape(s))

def Keyword(s):
    return Regex(re.escape(s) + r'\b')

def Maybe(p):
    return Choice(p, empty)

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

skip = Any()

eoi = Nix(skip)  # (renamed to not conflict with Parson's `end`)

eol = Choice(Literal('\n'), Nix(skip))

letter = Regex(r'[A-Za-z]')

udecimal = Seclude(Then(Regex(r'(\d+)'), Do('int')))
decimal  = Seclude(Then(Regex(r'(-?\d+)'), Do('int')))

spaces = Regex(r'\s*')

handy_prims = {
    'any': skip,
    'c': skip,
    'd': decimal,
    'end': eoi,    # N.B. different
    'eol': eol,
    'letter': letter,
    'spaces': spaces,  # TODO 0-or-more vs. 1-or-more
    'u': udecimal,
}
def BuiltIn(name):
    return handy_prims[name]
