"""
Example: txh fail, 1, -'A'
The -'A' must be the D field, right?
Is 1 the T field?
And fail the Y?
Seems like it, except the - sign is odd:
so: branchop Y, T, D
txh Transfer on indeX High (:= hi_op = 3) -> ((D < XR[T]) -> IC <- Y)
But it looks like the index registers are holding the - of values
in general...

insn   insn<S, 1:35>    I guess S means separate sign bit
op     op<S, 1:11> := insn<S, 1:11>
hi_op  hi_op<0:2> := insn<S, 1, 2>
D      D<3:17> := insn<3:17>   decrement part of insn
T      T<18:20> := insn<18:20>
Y      Y<21:35> := insn<21:35>
"""

from collections import defaultdict
## eval('hi', defaultdict(int))
#. 0

## d = {}
## UnionDict(d, defaultdict(int))['hi']
#. 0

## eval('hi', {}, UnionDict(d, defaultdict(int)))
#. 0

def assemble(lines, env, origin=0):
    forward_refs = defaultdict(int)
    assembler_pass(lines, UnionDict(env, forward_refs), origin)
    if any(key not in env for key in forward_refs):
        raise Exception("Unresolved ref")
    return assembler_pass(lines, env, origin), env

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
    words, here = [], origin
    for line in lines:
        label, tokens = tokenize(line)
        if label:
            if env.get(label, here) != here:
                raise Exception("Multiply-defined")
            env[label] = here
        if not tokens: continue
        env['__here__'] = here
        words.append(assemble1(tokens, env))
        here += 1
    return words

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

def assemble1(tokens, env={}):
    mnemonic, rest = tokens[0].upper(), ' '.join(tokens[1:])
    fields = [field.strip() for field in rest.split(',')]
    # TODO: resolve '*' as __here__
    # TODO: what is '**'? seems to mean just 0, weird.
    args = [eval(operand, {}, env) for operand in fields[1:]]
    if mnemonic in branch_mnemonics:
        return encode_branch(branch_mnemonics[mnemonic], *args)
    else:
        return encode(mnemonics[mnemonic], *args)


## assemble([' acl 0,1', 'foo CLA '], {})
#. ([4043309057L, 5368709120L], {'__here__': 1, 'foo': 1})

branch_mnemonics = dict(TXI=1, TXH=3,
                        TXL=7) # -3 'really'
mnemonics = dict(ACL=0361,
                 AXC=-0774,       # XXX
                 CAL=-0500,       # XXX
                 CLA=0500,
                 LAC=0535,
                 PAC=0737,
                 PCA=0756,
                 SCA=0636,
                 SLW=0602,
                 TRA=020)

def encode(op, Y=0, T=0):
    word = 0
    word = word_set(word, 0, 11, op)
    word = word_set(word, 18, 20, T)
    word = word_set(word, 21, 35, Y)
    return word

def encode_branch(hi_op, Y=0, T=0, D=0):
    word = 0
    word = word_set(word,  0,  2, hi_op)
    word = word_set(word,  3, 17, D)
    word = word_set(word, 18, 20, T)
    word = word_set(word, 21, 35, Y)
    return word

def word_set(word, left, right, value):
    shift, mask = word_field(left, right)
    return (word & ~mask) | ((value << shift) & mask)

def word_bits(word, left, right):
    shift, mask = word_field(left, right)
    return (word & mask) >> shift

def word_field(left, right):
    shift = 35 - right
    width = right+1 - left
    return shift, (~(~0 << width)) << shift
