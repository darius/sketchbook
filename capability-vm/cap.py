import ivm

class Ref(object):
    def invoke(self, continuation, selector, data_args, cap_args):
        abstract

def parse_selector(selector):
    assert 0 <= selector < 2**32
    s, ind  = divmod(selector, 8)
    s, inc  = divmod(s, 8)
    s, outd = divmod(s, 8)
    s, outc = divmod(s, 8)
    data, reserved = divmod(s, 16)
    return ind, inc, outd, outc, reserved, data

def make_selector(ind, inc, outd, outc, reserved, data):
    return ((((data<<4 | reserved)<<3 | outc)<<3 | outd)<<3 | inc)<<3 | ind

class OutFile(object):
    selector = make_selector(1, 0, 0, 0, 0, 0)
    def __init__(self, file):
        self.file = file
    def invoke(self, continuation, selector, data_args, cap_args):
        assert selector == self.selector
        self.file.write(chr(0xFF & data_args[0]))
        return (), ()

class InFile(object):
    selector = make_selector(0, 0, 1, 0, 0, 0)
    def __init__(self, file):
        self.file = file
    def invoke(self, continuation, selector, data_args, cap_args):
        assert selector == self.selector
        c = self.file.read(1)
        if '' == c:
            result = ivm.unsigned(-1)
        else:
            result = ord(c)
        return (result,), ()

class Stty(object):
    selector = make_selector(1, 0, 0, 0, 0, 0)
    def invoke(self, continuation, selector, data_args, cap_args):
        assert selector == self.selector
        arg = data_args[0]
        if arg == 0:
            os.system('stty sane')
        elif arg == 1:
            os.system('stty raw')
        else:
            pass
        return (), ()

import sys
def make_initial_caps():
    return [OutFile(sys.stdout),
            InFile(sys.stdin),
            Stty()]
