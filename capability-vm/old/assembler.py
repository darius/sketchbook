"""
I forget what I was doing with this. It might be
completely superseded by the code in the parent dir,
but I'm not sure; so here it is just in case.
"""

import ivm


def compile(program):
    vm = ivm.VM([])
    asm = Assembler(vm)
    asm.compile(program)
    return asm


class Assembler:                # Rather a misnomer...

    def __init__(self, vm):
        self.vm = vm
        self.here = 0
        self.entries = {}

    def enter(self, name):
        self.vm.go(self.get_value(name))

    def compile(self, defns):
        for d in defns:
            d.compile(self)

    def appendb(self, byte):
        self.vm.putb(self.here, byte)
        self.here += 1

    def append_zeroes(self, n):
        for i in range(n):
            self.appendb(0)

    def add_symbol(self, name, value):
        self.entries[name] = (-1, value)

    def get_value(self, name):
        return self.get_entry(name)[1]
        
    def has_symbol(self, name):
        return name in self.entries

    def add_label(self, name):
        self.add_symbol(name, self.here)

    def add_entry(self, name, arity):
        self.entries[name] = (arity, self.here)

    def has_entry(self, name):
        return name in self.entries and 0 <= self.entries[name][0]

    def get_entry(self, name):
        if name not in self.entries:
            raise 'Not found: ' + name
        return self.entries[name]

    def disassemble1(self, addr):
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


class Sink:

    def __init__(self, assembler, vars):
        self.asm   = assembler
        self.vars  = vars
        self.bytes = []

    def flush(self):
        for byte in reversed(self.bytes):
            self.asm.appendb(byte)

    def sprout(self, vars):     # talk about your mixed metaphors...
        return Sink(self.asm, vars)

    def reap(self, sproutling):
        for byte in sproutling.bytes:
            self.prependb(byte)

    def has_entry(self, name): return self.asm.has_entry(name)
    def get_entry(self, name): return self.asm.get_entry(name)
    def get_value(self, name): return self.asm.get_value(name)

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
        elif self.asm.has_symbol(t):
            if self.asm.has_entry(t):
                print 'Warning: %s referenced without calling' % t
            self.lit(self.asm.get_value(t))
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

        
class Constant:
    def __init__(self, name, value):
        self.name  = name
        self.value = value
    def compile(self, assembler):
        assembler.add_symbol(self.name, self.value)

class Variable:
    def __init__(self, name):
        self.name = name
    def compile(self, assembler):
        assembler.add_label(self.name)
        assembler.append_zeroes(4)

class Zeroes:
    def __init__(self, n):
        self.n = n
    def compile(self, assembler):
        assembler.append_zeroes(self.n)

class Label:
    def __init__(self, name):
        self.name = name
    def compile(self, assembler):
        assembler.add_label(self.name)

class CString:
    def __init__(self, literal):
        self.literal = literal
    def compile(self, assembler):
        for c in self.literal:
            assembler.appendb(ord(c))
        assembler.appendb(0)

class Def:
    def __init__(self, header, *args):
        h = header.split()
        assert 1 <= len(h)
        self.name   = h[-1]
        self.params = h[:-1]
        self.body   = parse(args)
    def compile(self, assembler):
        assembler.add_entry(self.name, self.arity())
        sink = Sink(assembler, self.params)
        self.body.pour(sink)
        sink.flush()
    def arity(self):
        return len(self.params)

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


class Token:
    def __init__(self, name):
        self.name = name
    def pour(self, sink):
        t = self.name
        if t.startswith(';'):
            nresults = int(t[1:])
            sink.ret(nresults)
        elif t.endswith(';'):
            t = t[:-1]
            arity, addr = sink.get_entry(t)
            sink.tailcall(arity)
            sink.lit(addr)
        elif t.endswith(')'):
            t = t[:-1]
            arity, addr = sink.get_entry(t)
            sink.call(arity)
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

class Literal:
    def __init__(self, value):
        self.value = value
    def pour(self, sink):
        sink.lit(self.value)

class SymVal:
    def __init__(self, symbol):
        self.symbol = symbol
    def pour(self, sink):
        sink.lit(sink.get_value(self.symbol))

class Sequence:
    def __init__(self, *stmts):
        self.stmts = map(parse, stmts)
    def pour(self, sink):
        for stmt in reversed(self.stmts):
            stmt.pour(sink)

class If:
    def __init__(self, iftrue, anyway):
        self.iftrue = parse(iftrue)
        self.anyway = parse(anyway)
    def pour(self, sink):
        # BRANCH iftrue [TARGET] anyway
        self.anyway.pour(sink)
        target = sink.here()
        self.iftrue.pour(sink)
        sink.branch(target)

def Cond(*pairs, **kwargs):
    default = kwargs['default']
    e = default
    for pair in reversed(pairs):
        test, iftrue = pair
        e = Sequence(test, If(iftrue, e))
    return e

class With:
    def __init__(self, vars, *args):
        self.vars = vars
        self.body = parse(args)
    def pour(self, sink):
        subsink = sink.sprout(self.vars)
        self.body.pour(subsink)
        sink.reap(subsink)
