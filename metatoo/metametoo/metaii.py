#!/usr/bin/env python
'''
An interpreter for Val Shorre's Meta II virtual machine.
Original, by Simon Forman, from
http://comments.gmane.org/gmane.comp.lang.smalltalk.fonc/3642
A few bugfixes and lots more general messing around by Darius Bacon;
anything you dislike about this code is probably his fault.
'''
# Some slight differences from Schorre's design:
#   * No ADR or END instructions. We start at address 0 and end by
#     returning. Just s/ADR/B/ in your compiler. An EOF instruction
#     tests for end of input.
#   * His had two variables: the switch and what I'm calling the
#     bite. I have only the bite; the switch is deemed true when bite
#     is not None. As used in the compilers we've seen, this
#     difference doesn't matter; it would if you ran the CI
#     instruction after a failed test.
#   * Stack frames are always 4 wide, including, for helpful
#     backtrace on error, the destination label. Schorre focused
#     on saving memory instead.

import itertools, sys

def main(argv):
  assert len(argv) == 3, "usage: %s asm-file source-file" % argv[0]
  vm = Meta_II_VM()
  vm.load(open_for_read(argv[1]).read())
  sys.stdout.write(vm.run(open_for_read(argv[2]).read()))
  sys.stdout.flush()
  if vm.poisoned:
    vm.inspect()
  return vm.poisoned

def open_for_read(filename):
  return sys.stdin if filename == '-' else open(filename)

class Meta_II_VM(object):
  def __init__(self):
    self.code = []
    self.labels = {}

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
    self.poisoned = False
    self.next_label = ('L%d' % n for n in itertools.count(1)).next
    self.stack = [-1, 'start', None, None]
    self.pc = 0
    while not self.poisoned and 0 <= self.pc:
      op, args = self.code[self.pc]
      self.pc += 1
      op(*args)
    return self.poop

  def eat(self, nchars):
    self.bite, self.feed = self.feed[:nchars], self.feed[nchars:]

  def decode_literal(self, arg):
    assert arg[:1] == arg[-1:] == "'"
    return arg[1:-1]

  # The machine's "order codes" (assembly instructions).

  def SET(self):
    self.bite = ''

  def EOF(self):
    self.feed = self.feed.lstrip()
    self.bite = None if self.feed else ''

  def TST(self, string):
    self.feed = self.feed.lstrip()
    string = self.decode_literal(string)
    if self.feed.startswith(string):
      self.eat(len(string))
    else:
      self.bite = None

  def ID(self):
    self.feed = self.feed.lstrip()
    if self.feed[:1].isalpha():
      n = 1
      while self.feed[n:n+1].isalnum():
        n += 1
      self.eat(n)
    else:
      self.bite = None

  def NUM(self):
    self.feed = self.feed.lstrip()
    n = 0
    while self.feed[n:n+1] in '0123456789.':
      n += 1
    if (n and self.feed[0] != '.' and self.feed[n-1] != '.'
        and '..' not in self.feed[:n]):
      self.eat(n)
    else:
      self.bite = None

  def SR(self):
    self.feed = self.feed.lstrip()
    if self.feed.startswith("'"):
      n = self.feed.find("'", 1)
      if n != -1:
        self.eat(n+1)
        return
    self.bite = None

  def B(self, addr):
    self.pc = self.labels[addr]

  def BT(self, addr):
    if self.bite is not None:
      self.B(addr)

  def BF(self, addr):
    if self.bite is None:
      self.B(addr)

  def BE(self):
    if self.bite is None:
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

  def CI(self):
    self.turd += self.bite

  def CL(self, string):
    self.turd += self.decode_literal(string)

  def LB(self):
    self.turd = self.turd.lstrip()

  def OUT(self):
    self.poop += self.turd.rstrip() + '\n'
    self.turd = '\t'

  # Debugging/introspection.

  def inspect(self):
    print >> sys.stderr, 'stack:', self.stack
    print >> sys.stderr, 'Calls:', ' '.join(self.stack[1::4])
    print >> sys.stderr, 'feed:', repr(self.feed[:40])
    self.list(self.pc-2, self.pc+1)

  def list(self, lo=0, hi=None):
    for addr in range(lo, hi or len(self.code)):
      self.print_instruction(addr)

  def print_instruction(self, addr):
    labels = ' '.join(k for k, v in self.labels.items() if v == addr)
    if labels:
      print >> sys.stderr, labels + ':'
    op, args = self.code[addr]
    print >> sys.stderr, '   %3d %-3s %s' % (addr, op.__name__, ''.join(args))

if __name__ == '__main__':
  sys.exit(main(sys.argv))
