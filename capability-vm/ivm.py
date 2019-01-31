import sys

import cap


wordmask = (1 << 32) - 1
min_signed = -(1 << 31)
max_signed = (1 << 31) - 1

def signed(w):
    assert 0 <= w <= wordmask
    if max_signed < w:
        return w - (word_mask + 1)
    else:
        return w

def unsigned(v):
    assert min_signed <= v <= max_signed
    return wordmask & v

for i in range(1000) + range(2**31 - 1000, 2**31):
    assert i == signed(i)
    assert i == unsigned(i)

for i in range(-999, 0) + range(-2**31, -2**31 + 1000):
    assert unsigned(i) - i == 2**32

def make_flag(flag):
    if flag:
        return wordmask
    else:
        return 0


def _enum(string):
    names = map(intern, string.split())
    return (names,
            dict(map(reversed, enumerate(names))))

op_names, op_codes = _enum("""
  bin misc lit branch 
  jump local arity call
  tailcall ret extend4""")

bin_names, bin_codes = _enum("""
  + - * u*
  and or xor <<
  >> >>> = <
  u<""")

misc_names, misc_codes = _enum("""
  @ ! b@ b!
  /mod u/mod drop (
  syscall invoke resume make-entry
  c-push c-drop c-set c-depth""")


class VM(object):

    def __init__(self, c_list):
        size       = 65536
        stacksize  = 8192
        cstacksize = 32
        self.M = [0] * size     # Memory -- holds unsigned bytes
        self.pc = 0
        self.sp = size
        self.bp = self.sp
        self.stack_limit = self.sp - stacksize
        self.cstack = c_list + [None] * (cstacksize - len(c_list))
        self.csp    = -1 + len(c_list)

    def go(self, addr):
        self.pc = addr
        self.run()

    def run(self):
        while self.step():
            pass

    def step(self):
        insn = self.getb(self.pc)
        self.pc += 1    # XXX wrap around?
        opcode, arg = divmod(insn, 16)
        return self.run1(opcode, arg)

    def run1(self, opcode, arg):
        op = op_names[opcode]
        if op == 'bin':
            return self.bin(arg)
        elif op == 'misc':
            return self.misc(arg)
        elif op == 'lit':
            self.push(arg)
        elif op == 'branch':
            if 0 == self.pop():
                self.pc += arg    # TODO: arg + 1
        elif op == 'jump':
            self.pc += arg        # TODO: arg + 1
# A stack frame looks like this, growing downwards in memory:
#      bp[4]:    old bp  (to be replaced eventually by any return values, upon 'ret')
#      bp[0]:    return address
#      bp[-4]:   leftmost argument
#      ...
#      bp[-4*n]: rightmost argument (where n is the number of arguments)
#      ...temporaries...
#      sp[0]:    'topmost' temporary
# When we first enter the function, there are no temporaries; by the time of exit,
# there should be at least as many values in the frame as the 'ret' instruction consumes.
        elif op == 'local':
            self.push(self.getw(self.bp - 4 * (arg+1)))
        elif op == 'arity':
            if 4 * arg != self.bp - self.sp:
                raise 'Bad arity'
        elif op == 'call':
            addr = self.pop()
            self.bp = self.sp + 4 * arg
            #assert 0 == self.getw(self.bp)
            self.putw(self.bp, self.pc)
            self.pc = addr
        elif op == 'tailcall':
            addr = self.pop()
            for i in range(arg):
                self.putw(self.bp - 4 * (i+1),
                          self.getw(self.sp + 4*arg - 4 * (i+1)))
            self.sp = self.bp - 4*arg
            self.pc = addr
        elif op == 'ret':
            assert 4 * arg <= self.bp - self.sp
            src  = self.sp
            self.sp = self.bp + 8 - 4 * arg
            self.pc = self.getw(self.bp)
            self.bp = self.getw(self.bp + 4)
            for i in range(arg):
                self.putw(self.sp + 4 * i, self.getw(src + 4 * i))
        elif op == 'extend4':
            arg4 = self.getw(self.pc)
            self.pc += 4
            return self.run1(arg, arg4)
        else:
            assert False
        return True

    def bin(self, code):
        op = bin_names[code]
        R = self.pop()
        L = self.top()
        if op == '+':
            v = wordmask & (L + R)
        elif op == '-':
            v = wordmask & (L - R)
        elif op == '*':
            v = wordmask & (signed(L) * signed(R))
        elif op == 'u*':
            v = wordmask & (L * R)
        elif op == 'and':
            v = L & R
        elif op == 'or':
            v = L | R
        elif op == 'xor':
            v = L ^ R
        elif op == '<<':
            v = L << R
        elif op == '>>':
            v = unsigned(signed(L) >> R)
        elif op == '>>>':
            v = L >> R
        elif op == '=':
            v = make_flag(L == R)
        elif op == '<':
            v = make_flag(signed(L) == signed(R))
        elif op == 'u<':
            v = make_flag(L < R)
        else:
            print op
            assert False
        self.set_top(v)
        return True

    def misc(self, code):
        op = misc_names[code]
        if op == '@':
            self.set_top(self.getw(self.top()))
        elif op == '!':
            addr = self.pop()
            self.putw(addr, self.pop())
        elif op == 'b@':
            self.set_top(self.getb(self.top()))
        elif op == 'b!':
            addr = self.pop()
            self.putb(addr, self.pop())
        elif op == '/mod':
            d = signed(self.pop())
            n = signed(self.top())
            q, r = divmod(n, d)
            self.set_top(unsigned(r))
            self.push(unsigned(q))
        elif op == 'u/mod':
            d = self.pop()
            n = self.top()
            q, r = divmod(n, d)
            self.set_top(r)
            self.push(q)
        elif op == 'drop':
            self.drop(1)
        elif op == '(':
            self.push(self.bp)
            self.push(0)
        elif op == 'syscall':
            return self.syscall(self.pop())
        elif op == 'invoke':
            selector = self.pop()
            nd, nc, _1, _2, _3, data = cap.parse_selector(selector)
            # XXX check the nd args are on the stack, etc.
            data_args = list(reversed([self.pop() for i in range(nd)]))
            receiver = self.cap_pop()
            cap_args = list(reversed([self.cap_pop() for i in range(nc)]))
            # XXX trampoline instead
            data_results, cap_results = \
                receiver.invoke(self, selector, data_args, cap_args)
            for cr in cap_results:
                self.cap_push(cr)
            for dr in data_results:
                self.push(dr)
        elif op == 'resume':
            XXX
        elif op == 'make-entry':
            XXX
        elif op == 'c-push':
            k = self.pop()
            if self.csp + 1 < k:
                raise 'bad index into capability stack'
            if len(self.cstack) <= self.csp + 1:
                raise 'capability stack overflow'
            self.csp += 1
            self.cstack[self.csp] = self.cstack[k]
        elif op == 'c-drop':
            n = self.pop()
            if self.csp + 1 < n:
                raise 'capability stack underflow'
            self.csp -= n
        elif op == 'c-set':
            k = self.pop()
            if self.csp < k:
                raise 'bad index into capability stack'
            self.cstack[k] = self.cstack[self.csp]
            self.csp -= 1
        elif op == 'c-depth':
            self.push(self.csp + 1)
        else:
            print op
            assert False
        return True

    def cap_push(self, cap):
        if len(self.cstack) <= self.csp + 1:
                raise 'capability stack overflow'
        self.csp += 1
        self.cstack[self.csp] = cap

    def cap_pop(self):
        if self.csp < 0:
            raise 'capability stack underflow'
        r = self.cstack[self.csp]
        self.csp -= 1
        return r

    def syscall(self, code):
        if code == 0:
            # Halt
            return False
        else:
            raise 'Unknown syscall'
        return True

    def set_top(self, w):
        assert self.stack_limit <= self.sp
        self.putw(self.sp, w)
        
    def push(self, w):
        self.sp -= 4
        self.set_top(w)

    def top(self):
        return self.getw(self.sp)

    def pop(self):
        r = self.top()
        self.drop(1)
        return r

    def drop(self, n):
        self.sp += 4 * n
        assert self.sp <= len(self.M)

    def getb(self, addr):
        return self.M[addr]

    def putb(self, addr, b):
        assert 0 <= b < 256
        self.M[addr] = b

    def getw(self, addr):
        # Little-endian
        M = self.M
        x = (((((M[addr+3] << 8) | M[addr+2]) << 8) | M[addr+1]) << 8) | M[addr]
        return x

    def putw(self, addr, w):
        assert 0 <= w <= wordmask
        M = self.M
        w3, M[addr] = divmod(w, 256)
        w2, M[addr+1] = divmod(w3, 256)
        M[addr+3], M[addr+2] = divmod(w2, 256)
