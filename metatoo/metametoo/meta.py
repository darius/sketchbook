#!/usr/bin/env python
'''
An interpreter inspired by Val Shorre's Meta II virtual machine.
This began as Simon Forman's code at
http://comments.gmane.org/gmane.comp.lang.smalltalk.fonc/3642
but it's been heavily hacked by Darius Bacon -- anything you dislike
about this code is probably his fault.
'''
# Differences from Schorre's design:
#   * Separate value and call stacks make it Forthier. The value
#     stack and its operations replace the LABEL1/LABEL2 instructions.
#   * The call stack includes, for helpful backtrace on error, the
#     destination label.
#   * Changed all the instruction names.
#   * No ADR or END instructions. We start at address 0 and end by
#     returning. Just s/ADR/GOTO/ in your compiler.
#   * Also no SET instruction; subsumed by new WRITE_Q and WIN_LOOP instructions.
#   * The WRITE instructions set the success flag.
#   * New READ_EOF and WRITE_Q instructions.
#   * READ_DECIMAL (the old NUM) only matches integers now.
#   * READ_ID allows underscores.
#   * There's a trace mode. TODO: add an instruction to turn it on or off.

import itertools, re, sys

def main(argv):
    trace = False
    if argv[1:2] == ['-trace']:
        trace = True
        del argv[1]
    assert len(argv) == 3, "usage: %s [-trace] asm-file source-file" % argv[0]
    vm = Meta_II_VM(trace)
    with open_for_read(argv[1]) as f:
        vm.load(f.read())
    with open_for_read(argv[2]) as f:
        sys.stdout.write(vm.run(f.read()))
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
        self.win = False
        self.stack = []
        self.calls = [-1, 'start']
        self.gensym = itertools.count().next
        self.poisoned = False
        self.pc = 0
        while not self.poisoned and 0 <= self.pc:
            cur_pc = self.pc
            op, args = self.code[self.pc]
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
