"""
See step-by-step running of the vm. Hit enter at each step.
"""

import ansi                     # from ../../editor/
import visiblemachine

def watch(filename, inputs):
    vm = visiblemachine.load(filename, inputs)
    while True:
        sys.stdout.write(ansi.clear_screen)
        vm.show()
        sys.stdin.read(1)
        try:
            vm.step()
        except visiblemachine.Halt, e:
            print e
            break

if __name__ == '__main__':
    import sys
    watch(sys.argv[1], sys.argv[2])
