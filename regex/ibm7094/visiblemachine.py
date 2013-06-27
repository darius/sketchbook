"""
A virtual machine meant to share enough of the IBM 7094's character to
run Thompson's code in an obvious direct translation, but to be easier
to quickly explain and visually animate. So the 'machine words' are
fixed-length strings with fields holding instruction mnemonics and
decimal numbers.
"""

def put_number(vh, vn):
    vl = '%02d' % vn
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
