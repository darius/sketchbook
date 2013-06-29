"""
A virtual machine meant to share enough of the IBM 7094's character to
run Thompson's code in an obvious direct translation, but to be easier
to quickly explain and visually animate. So the 'machine words' are
fixed-length strings with fields holding instruction mnemonics and
decimal numbers.
"""

from assembler import assemble

def toplevel(filename):
    env = dict(('r%d'%i, i) for i in range(1, 10))
    words = assemble(assemble1, open(filename), env)
    show(words)

def show(words):
    lines = ['%2d %s %s %s %s' % (addr, word[:5], word[5], word[6], word[7:])
             for addr, word in enumerate(words)]
    print '\n'.join(format_columns(lines, 5))

def format_columns(lines, ncols, sep='   '):
    assert lines 
    assert all(len(line) == len(lines[0]) for line in lines)
    nrows = (len(lines) + ncols-1) // ncols
    lines = list(lines)
    while len(lines) % nrows != 0:
        lines.append('')
    columns = [lines[i:i+nrows] for i in range(0, len(lines), nrows)]
    return map(sep.join, zip(*columns))

## for row in format_columns(map(str, range(10)), 3): print row
#. 0   4   8
#. 1   5   9
#. 2   6   
#. 3   7   
#. 

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
    vl = '%2d' % vn
    assert len(vl) == 2
    return vh + vl

def get_number(v):
    vh, vl = v[:7], v[7:]
    assert len(vl) == 2
    return vh, int(vl)

def add(u, v):
    uh, un = get_number(u)
    vh, vn = get_number(v)
    rn = (un + vn + 100) % 100
    if not uh.strip(): return put_number(vh, rl)
    if not vh.strip(): return put_number(uh, rl)
    assert False

class VM(object):

    def __init__(self, program, input_chars):
        self.pc = put_number(' '*7, 0)
        self.M = [' '*9] * 100
        self.R = [' '*9] * 10
        self.input_chars = iter(input_chars)
        for addr, value in enumerate(program):
            assert len(value) == 9
            self.store(addr, value)

    def fetch(self, addr):
        return self.M[get_number(addr)]

    def store(self, addr, value):
        self.M[get_number(addr)] = value

    def get(self, r):
        return self.R[int(r)]

    def set(self, r, value):
        if int(r) != 0:
            self.R[int(r)] = value

    def step(self):
        insn = self.fetch(self.pc)
        self.pc = add(self.pc, put_number(' '*7, 1))
        op, r1, r2, addr = insn[:5], insn[5], insn[6], insn[7:]

        def ea():
            return add(self.get(r2), addr)

        if   op == 'fetch':
            self.set(r1, self.fetch(ea()))
        elif op == 'store':
            self.store(ea(), self.get(r1))
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
                assert False
            self.set(r1, ' '*8 + ch)
        elif op == 'found':
            assert False
        else:
            assert False

vm = VM((), '')


if __name__ == '__main__':
    import sys
    toplevel(sys.argv[1])
