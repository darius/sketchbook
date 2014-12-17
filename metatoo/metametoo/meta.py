#!/usr/bin/env python
'''
A virtual machine inspired by Val Shorre's Meta II.
This began as Simon Forman's code at
http://comments.gmane.org/gmane.comp.lang.smalltalk.fonc/3642
but little of that is left.
'''

import itertools, re, sys

def main(argv):
    trace = False
    if argv[1:2] == ['-trace']:
        trace = True
        del argv[1]
    assert 2 <= len(argv), "usage: %s [-trace] asm-file [input-file...]" % argv[0]

    vm = Meta_VM(trace)
    with open(argv[1]) as f:
        vm.load(f)
    input_text = ''
    if argv[2:]:
        for filename in argv[2:]:
            with open(filename) as f:
                input_text += f.read()
    else:
        input_text += sys.stdin.read()

    sys.stdout.write(vm.run(input_text))
    sys.stdout.flush()
    if vm.poisoned:
        vm.inspect()
    return vm.poisoned

class Meta_VM(object):
    def __init__(self, trace=False):
        self.code = []
        self.labels = {}
        self.trace = trace

    def load(self, lines):
        for line in lines:
            line = line.rstrip()
            if not line:
                pass
            elif line[0].isspace():
                self.load_instruction(*line.split(None, 1))
            else:
                assert line not in self.labels, "Duplicate label: " + line
                self.labels[line] = len(self.code)
            
    def load_instruction(self, op, *args):
        self.code.append((getattr(self, op.upper()), args))

    def run(self, input_text):
        # Appropriate terminology for a hylomorphism:
        self.feed = input_text
        self.bite = None
        self.poop = ''
        self.win = False
        self.stack = []
        self.calls = [-1, 'start']
        self.gensym = itertools.count().next
        self.poisoned = False
        self.pc = 0
        while not self.poisoned and 0 <= self.pc:
            cur_pc = self.pc
            op, args = self.code[cur_pc]
            self.pc += 1
            op(*args)
            if self.trace:
                self.print_instruction(cur_pc, '  ' + self.state_gist())
        return self.poop

    def match(self, regex):
        self.feed = self.feed.lstrip()
        m = re.match(regex, self.feed)
        if m:
            self.eat(m.end())
        else:
            self.win = False

    def eat(self, nchars):
        self.win, self.bite, self.feed = True, self.feed[:nchars], self.feed[nchars:]

    def decode_literal(self, arg):
        assert arg[:1] == arg[-1:] == "'"
        return arg[1:-1]

    def write(self, string):
        self.poop += string
        self.win = True

    # The instructions:

    def READ(self, string):
        self.match(re.escape(self.decode_literal(string)))

    def READ_EOF(self):
        self.feed = self.feed.lstrip()
        self.win = self.feed == ''

    def READ_ID(self):
        self.match(r'[a-zA-Z_]\w*')

    def READ_QSTRING(self):
        self.match(r"'[^']*'")

    def READ_DECIMAL(self):
        self.match(r'\d+')

    def GOTO(self, addr):
        self.pc = self.labels[addr]

    def IF_WIN(self, addr):
        if self.win:
            self.GOTO(addr)

    def WIN_LOOP(self, addr):
        self.IF_WIN(addr)
        self.win = True

    def IF_LOSE(self, addr):
        if not self.win:
            self.GOTO(addr)

    def WIN_OR_DIE(self):
        if not self.win:
            self.poisoned = True

    def CALL(self, addr):
        self.calls.extend((self.pc, addr))
        self.GOTO(addr)

    def RETURN(self):
        self.pc = self.calls[-2]
        del self.calls[-2:]

    def WRITE(self, string):
        self.write(self.decode_literal(string))

    def WRITE_Q(self):
        self.write("'")

    def WRITE_NL(self):
        self.write('\n')

    def WRITE_IT(self):
        self.write(self.bite)

    def WRITE_TOP(self):
        self.write(str(self.stack[-1]))

    def WRITE_POP(self):
        self.write(str(self.stack.pop()))

    def DO_GENSYM(self):
        self.stack.append(self.gensym())

    def DO_IT(self):
        self.stack.append(self.bite)

    def DO_SWAP(self):
        y, z = self.stack[-2:]
        self.stack[-2:] = [z, y]

    # Debugging/introspection.

    def inspect(self):
        print >> sys.stderr, 'stack:', self.stack
        print >> sys.stderr, 'calls:', ' '.join(self.calls[1::2])
        print >> sys.stderr, 'feed:', repr(self.feed[:40])
        self.list(self.pc-2, self.pc+1)

    def list(self, lo=0, hi=None):
        for addr in range(lo, hi or len(self.code)):
            self.print_instruction(addr)

    def print_instruction(self, addr, suffix=''):
        labels = ' '.join(k for k, v in self.labels.items() if v == addr)
        if labels:
            print >> sys.stderr, labels + ':'
        op, args = self.code[addr]
        print >> sys.stderr, ('     %3d %-18s%s'
                              % (addr,
                                 op.__name__.lower() + ' ' + ''.join(args),
                                 suffix))

    def state_gist(self):
        calls = ' '.join(self.calls[3::2])
        # TODO show the stack too -- how to format?
        return '%s %-10r %s' % ('yn'[self.win], self.feed[:8], calls)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
