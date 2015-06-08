"""
machine    = assignment*.
assignment = lvalue _? '=' _? expr _? '\n'.
expr       = lvalue _ lvalue _ lvalue.
lvalue     = name ('.' literal)*.
literal    = '0' | '1' | name.

name = /[^.]+/.
_    = /\s+/.
"""

def eval_hdl(text, env):
    """`text` is a machine description following the grammar above.
    `env` is a dict, for two purposes:
       * sequential-circuit state (and RAM)
       * I/O devices
    To use this for a particular machine, call eval_hdl() in a loop,
    once for each most-basic machine cycle, reading/writing the data
    of any special devices from/to env."""
    env['0'] = 0
    env['1'] = 1
    def key(lvalue):
        if '.' not in lvalue: return lvalue
        name, subscrs = lvalue.split('.', 1)
        return (name,) + tuple(env.get(s, 0) for s in subscrs)
    for line in text.splitlines():
        if '#' in line: line = line[:line.index('#')]
        if not line: continue
        dest, eq, test, if0, if1 = line.split()
        assert eq == '='
        env[key(dest)] = env.get(key(if1 if env.get(key(test)) else if0),
                                 0)

import sys

def run_stdio_hdl(text):
    """Run a machine hooked up to stdin/stdout via these devices:
    halt: Set this to 1 to end execution at the end of this cycle.
    stdin-any: 1 if you have ever requested an input byte yet, via:
    stdin-getchar: Set this to 1 to read the next byte, available in the next cycle.
    stdin-byte.b2.b1.b0: 8 bits holding the most recent byte read from stdin.
                         (all 1's on EOF)
    stdin-eof: 1 if no more input is available.
    stdout-putchar: Set this to 1 to write the next byte, using:
    stdout-byte.b2.b1.b0
    """
    def bit_key(name, bit):
        return name, (bit>>2)&1, (bit>>1)&1, bit&1
    env = {}
    env['stdin-any'] = 0
    while not env.get('halt'):
        if env.get('stdin-getchar'):
            env['stdin-any'] = 1
            ch = stdin.read(1)  # XXX make sure it's a byte, not unicode...
            if not ch:
                env['stdin-eof'] = 1
            else:
                env['stdin-eof'] = 0
                for bit in range(8):
                    env[bit_key('stdin-byte', bit)] = (ord(ch)>>bit)&1
        if env.get('stdout-putchar'):
            byte = sum(env.get(bit_key('stdout-putchar', bit), 0) << bit
                       for bit in range(8))
            sys.stdout.write(chr(byte))
        env['stdin-getchar'] = 0
        env['stdout-putchar'] = 0
        eval_hdl(text, env)

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        run_stdio_hdl(f.read())
