#!/usr/bin/env python
'''
An interpreter for Val Shorre's Meta II virtual machine.
This began as Simon Forman's code at
http://comments.gmane.org/gmane.comp.lang.smalltalk.fonc/3642
but it's been heavily hacked by Darius Bacon -- anything you dislike
about this code is probably his fault.
'''
# Differences from Schorre's design:
#   * Changed all the instruction names.
#   * No ADR or END instructions. We start at address 0 and end by
#     returning. Just s/ADR/B/ in your compiler.
#   * Also no SET instruction; subsumed by new WRITE_Q and WIN_LOOP instructions.
#   * The WRITE instructions set the success flag.
#   * New READ_EOF and WRITE_Q instructions.
#   * READ_DECIMAL (the old NUM) only matches integers now.
#   * Stack frames are always 4 wide, including, for helpful
#     backtrace on error, the destination label. Schorre focused
#     on saving memory instead.
#   * There's a tracing mode. TODO: add an instruction to turn it on or off.

import itertools, sys

def main(argv):
    trace = False
    if argv[1:2] == ['-trace']:
        trace = True
        del argv[1]
    assert len(argv) == 3, "usage: %s [-trace] asm-file source-file" % argv[0]
    vm = Meta_II_VM(trace)
    vm.load(open_for_read(argv[1]).read())
    sys.stdout.write(vm.run(open_for_read(argv[2]).read()))
    sys.stdout.flush()
    if vm.poisoned:
        vm.inspect()
    return vm.poisoned

def open_for_read(filename):
    return sys.stdin if filename == '-' else open(filename)

class Meta_II_VM(object):
    def __init__(self, trace=False):
        self.code = []
        self.labels = {}
        self.trace = trace

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
            if self.trace:
                self.print_instruction(cur_pc, '  ' + self.state_gist())
        return self.poop

    def eat(self, nchars):
        self.success, self.bite, self.feed = True, self.feed[:nchars], self.feed[nchars:]

    def decode_literal(self, arg):
        assert arg[:1] == arg[-1:] == "'"
        return arg[1:-1]

    # The instructions:

    def READ(self, string):
        self.feed = self.feed.lstrip()
        string = self.decode_literal(string)
        if self.feed.startswith(string):
            self.eat(len(string))
        else:
            self.success = False

    def READ_EOF(self):
        self.feed = self.feed.lstrip()
        self.success = self.feed == ''

    def READ_ID(self):
        self.feed = self.feed.lstrip()
        if self.feed[:1].isalpha():
            i = 1
            while self.feed[i:i+1].isalnum():
                i += 1
            self.eat(i)
        else:
            self.success = False

    def READ_SQUOTE(self):
        self.feed = self.feed.lstrip()
        if self.feed.startswith("'"):
            i = self.feed.find("'", 1)
            if i != -1:
                self.eat(i+1)
                return
        self.success = False

    def READ_DECIMAL(self):
        self.feed = self.feed.lstrip()
        i = 0
        while self.feed[i:i+1].isdigit():
            i += 1
        if i:
            self.eat(i)
        else:
            self.success = False

    def GOTO(self, addr):
        self.pc = self.labels[addr]

    def IF_WIN(self, addr):
        if self.success:
            self.GOTO(addr)

    def WIN_LOOP(self, addr):
        self.IF_WIN(addr)
        self.success = True

    def IF_LOSE(self, addr):
        if not self.success:
            self.GOTO(addr)

    def WIN_OR_DIE(self):
        if not self.success:
            self.poisoned = True

    def CALL(self, addr):
        self.stack.extend((self.pc, addr, None, None))
        self.GOTO(addr)

    def RETURN(self):
        self.pc = self.stack[-4]
        del self.stack[-4:]

    def WRITE(self, string):
        self.poop += self.decode_literal(string)
        self.success = True

    def WRITE_Q(self):
        self.poop += "'"
        self.success = True

    def WRITE_IT(self):
        self.poop += self.bite
        self.success = True

    def WRITE_LABEL1(self):
        if self.stack[-1] is None:
            self.stack[-1] = self.next_label()
        self.poop += self.stack[-1]
        self.success = True
        
    def WRITE_LABEL2(self):
        if self.stack[-2] is None:
            self.stack[-2] = self.next_label()
        self.poop += self.stack[-2]
        self.success = True

    def WRITE_NL(self):
        self.poop += '\n'
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
        print >> sys.stderr, ('     %3d %-18s%s'
                              % (addr,
                                 op.__name__.lower() + ' ' + ''.join(args),
                                 suffix))

    def state_gist(self):
        calls = ' '.join(((self.stack[i+1] if 0 < i else '')
                          + ''.join('-'+label if label else '.'
                                    for label in [self.stack[i+2], self.stack[i+3]]))
                         for i in range(0, len(self.stack), 4))
        return '%s %-10r %s' % ('yn'[self.success], self.feed[:8], calls)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
