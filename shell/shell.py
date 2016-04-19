"""
A basic Unix shell.
Based on an example from a workshop at Recurse Center.
"""

import os, re, sys

def shell():
    while True:
        try:
            line = raw_input('shell.py$ ')
        except EOFError:
            break
        try:
            command = map(expand, line.split())
            if command: run(command[0], command)
        except Exception as e:
            sys.stderr.write("%s: %r\n" % (sys.argv[0], e))

def expand(s):
    return expand_env_vars(os.path.expanduser(s))

def expand_env_vars(s):
    return re.sub(r'\${(.*?)}',
                  lambda m: os.environ[m.group(1)],
                  s)

def run(command_name, args):
    if command_name in BUILTINS:
        BUILTINS[command_name](args)
    else:
        pid = os.fork()
        if pid == 0:
            os.execvp(command_name, args)
        else:
            os.waitpid(pid, 0)

def export(args):
    os.environ.update(spec.split('=', 1) for spec in args[1:])

BUILTINS = {
    'cd': lambda args: os.chdir(args[1]),
    'exit': lambda args: exit(0),
    'export': export
}

if __name__ == '__main__':
    shell()
