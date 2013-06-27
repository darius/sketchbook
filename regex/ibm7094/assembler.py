"""
Generic 2-pass assembler.
"""

from collections import defaultdict
## eval('hi', defaultdict(int))
#. 0

## d = {}
## UnionDict(d, defaultdict(int))['hi']
#. 0

## eval('hi', {}, UnionDict(d, defaultdict(int)))
#. 0

def assemble(assemble1, lines, env, origin=0):
    lines = list(lines)
    forward_refs = defaultdict(int)
    for tokens in assembler_pass(lines, UnionDict(env, forward_refs), origin):
        assemble1(tokens, env)
    if set(forward_refs) - set(env):
    #if any(key not in env for key in forward_refs):
        raise Exception("Unresolved ref")
    return [assemble1(tokens, env) 
            for tokens in assembler_pass(lines, env, origin)]

## ',4'.split(',')
#. ['', '4']

class UnionDict(object):
    def __init__(self, dict1, dict2):
        self.dict1, self.dict2 = dict1, dict2
#    def __contains__(self, key):
#        try: self[key]
#        except KeyError: 
    def __getitem__(self, key):
        try:
            return self.dict1[key]
        except KeyError:
            return self.dict2[key]
    def __setitem__(self, key, value):
        self.dict1[key] = value
    def get(self, key, default=None):
        try:
            return self.dict1[key]
        except KeyError:
            return self.dict2.get(key, default)

def assembler_pass(lines, env, origin):
    here = origin
    for line in lines:
        label, tokens = tokenize(line)
        if label:
            if env.get(label, here) != here:
                raise Exception("Multiply-defined")
            env[label] = here
        if not tokens:
            continue
        env['__here__'] = here
        yield tokens
        here += 1

def starts_comment(string):
    return string.startswith(';')

def tokenize(line):
    tokens = line.split()
    if line[:1].isspace() or starts_comment(line):
        label = ''
    else:
        label = tokens.pop(0)
    for i, token in enumerate(tokens):
        if starts_comment(token):
            tokens = tokens[:i]
            break
    return label, tokens
