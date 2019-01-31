import compiling
import ivm


def walk(compiler, entry='main'):
    Stepper(compiler).enter(entry)

def run(compiler, entry='main'):
    compiler.enter(entry)


class Stepper(object):

    def __init__(self, comp):
        self.comp = comp
        self.vm   = comp.vm

    def enter(self, name):
        self.go(self.comp.get_value(name))

    def go(self, addr):
        self.vm.pc = addr
        self.run()

    def run(self):
        while self.step():
            pass

    def step(self):
        self.show()
        return self.vm.step()

    def show(self):
        vm = self.vm
        left = '%8x-bp %8x-sp ' % (vm.bp, vm.sp)
        right = ' %-12s %8x-pc' % (self.comp.disassemble1(vm.pc), vm.pc)
        width0 = len(left) + len(right)
        stack_items = []
        for addr in range(vm.sp, vm.bp, 4):
            item = ' %x' % vm.getw(addr)
            if 79 < width0 + sum(map(len, stack_items)) + len(item):
                # XXX add in a '...' item (making sure there's space)
                break
            stack_items.append(item)
        print '%s%*s%s' % (left, 
                           79 - width0, ''.join(reversed(stack_items)), 
                           right)
