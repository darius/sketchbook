import cap
import ivm


def make_program():
    return Compiler(ivm.VM(cap.make_initial_caps()), 0, Env())


class Env(object):

    def __init__(self):
        self.t = {}

    def define(self, name, value, arity):
        "Declare a name. It's a function if 0<=arity, else a numeric constant." # XXX right?
        self.t[name] = (arity, value)

    def has(self, name):
        return name in self.t

    def has_entry(self, name):
        return name in self.t and 0 <= self.t[name][0]

    def get_entry(self, name):
        return self.t[name]

    def get_value(self, name):
        return self.t[name][1]
        

class Compiler(object):

    def __init__(self, vm, origin, env):
        self.vm   = vm
        self.here = origin  # Code gets assembled into increasing addresses starting at 'here'.
        self.env  = env

    def define(self, header, *args):
        """Define an entry. The header is of the form "varname
        varname... entryname" and *args is the code sequence that
        assembles to the body. When entryname is called at runtime,
        the body runs with the varnames bound to the parameters
        passed on the stack."""
        h = header.split()
        assert 1 <= len(h)
        name   = h[-1]
        params = h[:-1]
        body   = parse(args)
        self.env.define(name, self.here, len(params))
        sink = Sink(self.env, params)
        body.pour(sink)
        for byte in sink.flush():
            self.appendb(byte)

    def cstring(self, bytes_):
        "Assemble a constant string, plus a nul-terminator."
        for c in bytes_:
            self.appendb(ord(c))
        self.appendb(0)

    def zeroes(self, n):
        "Assemble a block of n zero-bytes."
        for i in range(n):
            self.appendb(0)

    def variable(self, name):
        "Assemble a one-word named variable, initially 0."
        self.label(name)
        self.zeroes(4)

    def label(self, name):
        "Declare a name for the current address."
        self.constant(name, self.here)

    def constant(self, name, value):
        "Declare a numeric constant."
        self.env.define(name, value, -1)

    def has_entry(self, name):  return self.env.has_entry(name)
    def get_entry(self, name):  return self.env.get_entry(name)
    def get_value(self, name):  return self.env.get_value(name)

    def appendb(self, byte):
        "Assemble a single byte."
        self.vm.putb(self.here, byte)
        self.here += 1

    def enter(self, name='main'):
        "Start running at the named entry."
        self.vm.go(self.get_value(name)) # XXX require has_entry?

    def disassemble1(self, addr):
        "Return a string disassembling the instruction at addr."
        insn = self.vm.getb(addr)
        opcode, arg = divmod(insn, 16)
        return self.disassemble2(addr + 1, opcode, arg)

    def disassemble2(self, addr, opcode, arg): # XXX ugh, rename
        op = ivm.op_names[opcode]
        if op is 'bin':    return _dis(ivm.bin_names, arg)
        elif op is 'misc': return _dis(ivm.misc_names, arg)
        elif op in ('lit', 'branch', 'jump', 'local', 'arity',
                    'call', 'tailcall', 'ret'):
            return '%s:%d' % (op, arg)
        elif op is 'extend4':
            arg4 = self.vm.getw(addr)
            return self.disassemble2(addr + 4, arg, arg4)
        else:
            return 'unknown:%d:%d' % (opcode, arg)

def _dis(names, i):
    try:
        return names[i]
    except IndexError:
        return 'unknown:%d' % i


class Sink(object):

    def __init__(self, env, vars):
        self.env   = env
        self.vars  = vars
        self.bytes = []

    def flush(self):
        return reversed(self.bytes)

    def sprout(self, vars):     # talk about your mixed metaphors...
        return Sink(self.env, vars)

    def reap(self, sproutling):
        for byte in sproutling.bytes:
            self.prependb(byte)

    def has_entry(self, name): return self.env.has_entry(name)
    def get_entry(self, name): return self.env.get_entry(name)
    def get_value(self, name): return self.env.get_value(name)

    def here(self):
        return len(self.bytes)

    def branch(self, there):   self._jump('branch', there)
    def jump(self, there):     self._jump('jump', there)

    def tailcall(self, arity): self._extendibly('tailcall', arity)
    def call(self, arity):     self._extendibly('call', arity)
    def ret(self, n):          self._extendibly('ret', n)

    def lit(self, value):      self._extendibly('lit', value)

    def word(self, t):
        if t in self.vars:
            self._extendibly('local', self.vars.index(t))
        elif self.env.has(t):
            if self.env.has_entry(t):
                print 'Warning: %s referenced without calling' % t
            self.lit(self.env.get_value(t))
        else:
            self.primitive(t)

    def primitive(self, op):
        if op in ivm.bin_codes:
            self.prepend('bin', ivm.bin_codes[op])
        elif op in ivm.misc_codes:
            self.prepend('misc', ivm.misc_codes[op])
        else:
            raise 'Unknown primitive: ' + op

    def _jump(self, op, there):
        offset = self.here() - there
        assert 0 <= offset
        self._extendibly(op, offset)

    def _extendibly(self, op, arg):
        if 0 <= arg < 16:
            self.prepend(op, arg)
        else:
            self.prependw(arg)
            self.prepend('extend4', ivm.op_codes[op])

    def prepend(self, op, arg):
        code = ivm.op_codes[op]
        assert 0 <= code < 16
        assert 0 <= arg < 16
        self.prependb((code << 4) | arg)

    def prependw(self, w):
        assert 0 <= w <= ivm.wordmask
        w3, b0 = divmod(w, 256)
        w2, b1 = divmod(w3, 256)
        b3, b2 = divmod(w2, 256)
        self.prependb(b3)
        self.prependb(b2)
        self.prependb(b1)
        self.prependb(b0)

    def prependb(self, b):
        self.bytes.append(b)

        
def parse(x):
    if isinstance(x, str):
        return parse_sequence(map(Token, x.split()))
    if isinstance(x, (list, tuple)):
        return parse_sequence(x)
    return x

def parse_sequence(xs):
    if 1 == len(xs):
        return parse(xs[0])
    return Sequence(*xs)


class Token(object):
    def __init__(self, name):
        self.name = name
    def pour(self, sink):
        t = self.name
        if t.startswith(';'):
            nresults = int(t[1:])
            sink.ret(nresults)
        elif t.startswith('$') and 1 < len(t):
            sink.lit(ord(t[1:2])) # XXX what about the rest of t?
        elif t.endswith(';'):
            t = t[:-1]
            arity, addr = sink.get_entry(t)
            sink.tailcall(arity) # XXX check nonnegative arity?
            sink.lit(addr)
        elif t.endswith(')'):
            t = t[:-1]
            arity, addr = sink.get_entry(t)
            sink.call(arity) # XXX check nonnegative arity?
            sink.lit(addr)
        else:
            try:
                value = int(t)
            except ValueError:
                sink.word(t)
            else:
                if value < 0:
                    value = unsigned(value)
                sink.lit(value)

class Literal(object):
    def __init__(self, value):
        self.value = value
    def pour(self, sink):
        sink.lit(self.value)

class Sequence(object):
    def __init__(self, *stmts):
        self.stmts = map(parse, stmts)
    def pour(self, sink):
        for stmt in reversed(self.stmts):
            stmt.pour(sink)

class If(object):
    def __init__(self, iftrue, anyway):
        self.iftrue = parse(iftrue)
        self.anyway = parse(anyway)
    def pour(self, sink):
        # BRANCH iftrue [TARGET] anyway
        self.anyway.pour(sink)
        target = sink.here()
        self.iftrue.pour(sink)
        sink.branch(target)

def Cond(*pairs, **kwargs):     # XXX why kwargs when only 'default' is used?
    default = kwargs['default']
    e = default
    for pair in reversed(pairs):
        test, iftrue = pair
        e = Sequence(test, If(iftrue, e))
    return e

class With(object):
    def __init__(self, vars, *args):
        self.vars = vars
        self.body = parse(args)
    def pour(self, sink):
        subsink = sink.sprout(self.vars)
        self.body.pour(subsink)
        sink.reap(subsink)
