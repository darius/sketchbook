"""
A virtual machine meant to share enough of the IBM 7094's character to
run Thompson's code in an obvious direct translation, but to be easier
to quickly explain and visually animate. So the 'machine words' are
fixed-length strings with fields holding instruction mnemonics and
decimal numbers.
"""

from assembler import assemble
import re

## v = load('thompson.vm.s', '')
## v.run(0)
#.               0   r2                r4                r6                r8             
#. r1                r3                r5                r7                r9             
#. 
#.  0 init           ==>smash 0 0 20   20 set   7 0  0   40 noop  0 0  0   60                80             
#.  1 xchg            1 aload 7 0 20   21 set   3 4  0   41 ifne  1 A 27   61                81             
#.  3 x1              2 set   6 0  0   22 fetch 5 0 38   42 jump  4 0 20   62                82             
#.  9 x2              3 ifeq  7 0  9   23 add   3 5  0   43 found 0 0  0   63                83             
#. 16 jumpcmd         4 set   7 7 -1   24 store 3 7 80   44                64                84             
#. 20 nnode           5 fetch 3 7 80   25 set   7 7  1   45                65                85             
#. 27 fail            6 store 3 6 60   26 smash 7 0 20   46                66                86             
#. 28 cnode           7 set   6 6  1   27 jump  0 2  0   47                67                87             
#. 38 callcmd         8 jump  0 0  3   28 set   7 0  0   48                68                88             
#. 40 code            9 fetch 3 0 16   29 fetch 3 7 60   49                69                89             
#. 60 clist          10 store 3 6 60   30 store 3 7 61   50                70                90             
#. 80 nlist          11 smash 7 0 28   31 set   3 4  0   51                71                91             
#.                   12 smash 0 0 20   32 fetch 5 0 38   52                72                92             
#.                   13 getch 1 0  0   33 add   3 5  0   53                73                93             
#.                   14 jump  2 0 40   34 store 3 7 60   54                74                94             
#.                   15 jump  0 0 60   35 set   7 7  1   55                75                95             
#.                   16 jump  0 0  1   36 smash 7 0 28   56                76                96             
#.                   17                37 jump  0 4  2   57                77                97             
#.                   18                38 jump  2 0  0   58                78                98             
#.                   19                39                59                79                99             
#. 

def toplevel(filename, inputs=''):
    vm = load(filename, inputs)
    vm.show()

def load(filename, inputs):
    env = dict(('r%d'%i, i) for i in range(1, 10))
    words = assemble(assemble1, open(filename), env)
    return VM(words, inputs, env)

def show_env(env):
    return ['%2d %-12s' % (value, label)
            for label, value in sorted(env.items(), key=lambda (k,v): v)
            if not re.match(r'r[1-9]|__here__', label)]

def assemble1(tokens, env):
    mnemonic, rest = tokens[0].lower(), ' '.join(tokens[1:])
    fields = [field.strip() or '0' for field in rest.split(',')]
    args = [eval(operand, {}, env) for operand in fields]
    if mnemonic == 'zeroes':
        assert len(args) == 1
        return [' '*9] * args[0]
    else:
        while len(args) < 3:
            args.append('0')
        assert len(args) == 3
        return ['%-5s%s%s%02s' % (mnemonic, args[0], args[1], int(args[2]))]

def put_number(vh, vn):
    assert len(vh) == 7
    assert isinstance(vn, int)
    vl = '%2d' % vn
    assert len(vl) == 2, vn
    return vh + vl

def get_number(v):
    assert len(v) == 9
    vh, vl = v[:7], v[7:]
    assert len(vl) == 2, repr(v)
    return vh, int('0' if vl == '  ' else vl)

def add(u, v):
    uh, un = get_number(u)
    vh, vn = get_number(v)
    rn = (un + vn + 100) % 100
    if not uh.strip(): return put_number(vh, rn)
    if not vh.strip(): return put_number(uh, rn)
    assert False

class VM(object):

    def __init__(self, program, input_chars, env):
        self.pc = put_number(' '*7, 0)
        self.M = [' '*9] * 100
        self.R = [' '*8+'0'] + [' '*9] * 9
        self.input_chars = iter(input_chars)
        self.env = env
        for addr, value in enumerate(program):
            assert len(value) == 9
            self.store(put_number(' '*7, addr), value)

    def show(self):
        regs = map(self.show_reg, range(10))
        print '\n'.join(format_columns(regs, 5))
        print
        defs = pad(show_env(self.env), 20)
        insns = map(self.show_cell, range(100))
        print '\n'.join(format_columns(defs + insns, 6))

    def show_reg(self, i):
        r = '  ' if i == 0 else 'r%d' % i
        word = self.R[i]
        return '%s %s %s %s %s' % (r, word[:5], word[5], word[6], word[7:])

    def show_cell(self, i):
        word = self.M[i]
        addr = '==>' if i == get_number(self.pc)[1] else '%2d ' % i
        return '%s%s %s %s %s' % (addr, word[:5], word[5], word[6], word[7:])

    def fetch(self, addr):
        ah, an = get_number(addr)
        return self.M[an]

    def store(self, addr, value):
        ah, an = get_number(addr)
        self.M[an] = value

    def get(self, r):
        return self.R[int(r)]

    def set(self, r, value):
        if int(r) != 0:
            self.R[int(r)] = value

    def run(self, nsteps):
        for _ in range(nsteps):
            self.show()
            self.step()
        self.show()

    def step(self):
        insn = self.fetch(self.pc)
        self.pc = add(self.pc, put_number(' '*7, 1))
        op, r1, r2, addr = insn[:5], insn[5], insn[6], insn[7:]

        def ea():
            return add(self.get(r2), ' '*7 + addr)

        if   op == 'fetch':
            self.set(r1, self.fetch(ea()))
        elif op == 'store':
            self.store(ea(), self.get(r1))
        elif op == 'aload':
            cell = self.fetch(ea())
            ch, cn = get_number(cell)
            self.set(r1, put_number(' '*7, cn))
        elif op == 'smash':
            i = ea()
            cell = self.fetch(i)
            new_cell = cell[:7] + self.get(r1)[7:]
            self.store(i, new_cell)
        elif op == 'set  ':
            self.set(r1, ea())
        elif op == 'add  ':
            self.set(r1, add(self.get(r1), ea()))
        elif op == 'jump ':
            self.set(r1, self.pc)
            self.pc = ea()
        elif op == 'ifeq ':
            value = ' '*8 + r2
            if self.get(r1) == value:
                self.pc = ' '*7 + addr
        elif op == 'ifne ':
            value = ' '*8 + r2
            if self.get(r1) != value:
                self.pc = ' '*7 + addr
        elif op == 'getch':
            ch = next(self.input_chars, None)
            if ch is None:
                raise Halt('Out of input')
            self.set(r1, ' '*8 + ch)
        elif op == 'noop ':
            pass
        elif op == 'found':
            raise Halt('Found')
        else:
            assert False

class Halt(Exception): pass

def format_columns(items, ncols, sep='   '):
    items = list(items)
    assert items 
    assert all(len(item) == len(items[0]) for item in items)
    nrows = (len(items) + ncols-1) // ncols
    items = pad(items, nrows * ncols)
    columns = [items[i:i+nrows] for i in range(0, len(items), nrows)]
    return map(sep.join, zip(*columns))

def pad(items, n):
    return items + [' ' * len(items[0])] * (n - len(items))

## for row in format_columns(map(str, range(10)), 3): print row
#. 0   4   8
#. 1   5   9
#. 2   6    
#. 3   7    
#. 


if __name__ == '__main__':
    import sys
    toplevel(sys.argv[1])
