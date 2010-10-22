"""
Skeleton of Ward Cunningham's txtzyme language for embedded controllers.
"""

import re

## run('42p 5p')
#. 42
#. 5
#. 

## run('5{3p}')
#. 3
#. 3
#. 3
#. 3
#. 3
#. 

## run('5{kp}')
#. 4
#. 3
#. 2
#. 1
#. 0
#. 

## tokenize('5{kp} 42p')
#. ['5', '{', 'k', 'p', '}', '42', 'p']

def tokenize(s):
    return [token
            for token in re.findall(r'\d+|\s+|.', s)
            if not token.isspace()]

def run(s):
    tokens = tokenize(s)
    acc = i = 0
    pc = 0
    loop_start = 0
    while pc < len(tokens):
        c = tokens[pc]
        if c.isdigit():
            acc = int(c)
        elif c == 'p':
            print acc
        elif c == '{':
            i = acc
            loop_start = pc + 1
            pc = tokens.index('}', pc)
            continue
        elif c == '}':
            if 0 < i:
                i -= 1
                pc = loop_start
                continue
        elif c == 'k':
            acc = i
        else:
            raise Exception('Unexpected character: %s' % c)
        pc += 1
