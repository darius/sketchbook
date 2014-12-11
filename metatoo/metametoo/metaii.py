#!/usr/bin/env python
'''
An interpreter for Val Shorre's Meta II virtual machine.
This began as Simon Forman's code at
http://comments.gmane.org/gmane.comp.lang.smalltalk.fonc/3642
but it's been heavily hacked by Darius Bacon -- anything you dislike
about this code is probably his fault.
'''
# Differences from Schorre's design:
#   * No ADR or END instructions. We start at address 0 and end by
#     returning. Just s/ADR/B/ in your compiler.
#   * Also no SET instruction; subsumed by new CQ and BTT instructions.
#   * The OUT instruction sets the success flag.
#   * A new EOF instruction.
#   * Stack frames are always 4 wide, including, for helpful
#     backtrace on error, the destination label. Schorre focused
#     on saving memory instead.
#   * There's a tracing mode. TODO: add an instruction to turn it on or off.
# TODO: modernize the instruction names

import itertools, sys

def main(argv):
    tracing = False
    if argv[1:2] == '-tracing':
        tracing = True
        del argv[1:2]
    assert len(argv) == 3, "usage: %s [-trace] asm-file source-file" % argv[0]
    vm = Meta_II_VM(tracing)
    vm.load(open_for_read(argv[1]).read())
    sys.stdout.write(vm.run(open_for_read(argv[2]).read()))
    sys.stdout.flush()
    if vm.poisoned:
        vm.inspect()
    return vm.poisoned

def open_for_read(filename):
    return sys.stdin if filename == '-' else open(filename)

class Meta_II_VM(object):
    def __init__(self, tracing=False):
        self.code = []
        self.labels = {}
        self.tracing = tracing

    def load(self, source_code):
        for line in source_code.splitlines():
            if not line or line.isspace():
                pass
            elif line[0].isspace():
                self.load_line(*line.split(None, 1))
            else:
                label = line.strip()
                assert label not in self.labels, "Duplicate label: " + label
                self.labels[label] = len(self.code)
            
    def load_line(self, op, *args):
        self.code.append((getattr(self, op.upper()), args))

    def run(self, input_text):
        # Appropriate terminology for a hylomorphism:
        self.feed = input_text
        self.bite = None
        self.turd = '\t'
        self.poop = ''
        self.success = False
        self.poisoned = False
        self.next_label = ('L%d' % n for n in itertools.count(1)).next
        self.stack = [-1, 'start', None, None]
        self.pc = 0
        while not self.poisoned and 0 <= self.pc:
            cur_pc = self.pc
            op, args = self.code[self.pc]
            self.pc += 1
            op(*args)
            if self.tracing:
                self.print_instruction(cur_pc, '    ' + self.state_gist())
        if self.poisoned:
            self.inspect()
            sys.exit(1)
        return self.poop

    def eat(self, nchars):
        self.success, self.bite, self.feed = True, self.feed[:nchars], self.feed[nchars:]

    def decode_literal(self, arg):
        assert arg[:1] == arg[-1:] == "'"
        return arg[1:-1]

    # The instructions:

    def EOF(self):
        self.feed = self.feed.lstrip()
        self.success = self.feed == ''

    def TST(self, string):
        self.feed = self.feed.lstrip()
        string = self.decode_literal(string)
        if self.feed.startswith(string):
            self.eat(len(string))
        else:
            self.success = False

    def ID(self):
        self.feed = self.feed.lstrip()
        if self.feed[:1].isalpha():
            n = 1
            while self.feed[n:n+1].isalnum():
                n += 1
            self.eat(n)
        else:
            self.success = False

    def NUM(self):
        self.feed = self.feed.lstrip()
        n = 0
        while self.feed[n:n+1] in '0123456789.':
            n += 1
        if (n and self.feed[0] != '.' and self.feed[n-1] != '.'
                and '..' not in self.feed[:n]):
            self.eat(n)
        else:
            self.success = False

    def SR(self):
        self.feed = self.feed.lstrip()
        if self.feed.startswith("'"):
            n = self.feed.find("'", 1)
            if n != -1:
                self.eat(n+1)
                return
        self.success = False

    def B(self, addr):
        self.pc = self.labels[addr]

    def BT(self, addr):
        if self.success:
            self.B(addr)

    def BTT(self, addr):
        self.BT(addr)
        self.success = True

    def BF(self, addr):
        if not self.success:
            self.B(addr)

    def BE(self):
        if not self.success:
            self.poisoned = True

    def CLL(self, addr):
        self.stack.extend((self.pc, addr, None, None))
        self.B(addr)

    def R(self):
        self.pc = self.stack[-4]
        del self.stack[-4:]

    def GN1(self):
        if self.stack[-1] is None:
            self.stack[-1] = self.next_label()
        self.turd += self.stack[-1]
        
    def GN2(self):
        if self.stack[-2] is None:
            self.stack[-2] = self.next_label()
        self.turd += self.stack[-2]

    def CQ(self):
        self.turd += "'"

    def CI(self):
        self.turd += self.bite

    def CL(self, string):
        self.turd += self.decode_literal(string)

    def LB(self):
        self.turd = self.turd.lstrip()

    def OUT(self):
        self.poop += self.turd.rstrip() + '\n'
        self.turd = '\t'
        self.success = True

    # Debugging/introspection.

    def inspect(self):
        print >> sys.stderr, 'stack:', self.stack
        print >> sys.stderr, 'Calls:', ' '.join(self.stack[1::4])
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
        print >> sys.stderr, ('     %3d %-3s %-10s%s'
                              % (addr, op.__name__, ''.join(args), suffix))

    def state_gist(self):
        calls = ' '.join(((self.stack[i+1] if 0 < i else '')
                          + ''.join('-'+label if label else '.'
                                    for label in [self.stack[i+2], self.stack[i+3]]))
                         for i in range(0, len(self.stack), 4))
        return '%s %-10s %s' % ('yn'[self.success], self.feed[:8], calls)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
