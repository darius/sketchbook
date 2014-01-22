"""
Text Register Machine interpreter
http://www.indiana.edu/~iulg/trm/
Glossary:
  pc    program counter
  insn  instruction
  n     argument part of instruction
  reg   register
"""


# Smoke test

## show(parse('1#111##'))
#.     add_one 1 
#.   1 add_hash 3

## run(parse('1#111##'), make_regs('', '', ''), verbose=True)
#.     add_one 1 	r1: 
#.   1 add_hash 3	r2: 
#.               	r3: 
#. 
#.   1 add_one 1 	r1: 1
#.     add_hash 3	r2:  
#.               	r3:  
#. 
#.   2 add_one 1 	r1: 1
#.   1 add_hash 3	r2:  
#.               	r3: #
#. {1: '1', 2: '', 3: '#'}


# 4.1 Program to move register contents

## move_r2_r1 = parse('11#####111111###111###1##1111####1#111111####')
## show(move_r2_r1, 0, make_regs('', '1#1#11##'))
#.     case 2    	r1:         
#.   1 forward 6 	r2: 1#1#11##
#.   2 forward 3              
#.   3 add_hash 1             
#.   4 backward 4             
#.   5 add_one 1              
#.   6 backward 6             
## run(move_r2_r1, make_regs('', '1#1#11##'))
#. {1: '1#1#11##', 2: ''}


from itertools import izip_longest
import re

def parse(program):
    assert re.match(r'(1+#{1,5})*$', program)
    tokens = re.findall(r'1+#{1,5}', program)
    return tuple(map(parse_insn, tokens))

def parse_insn(token):
    return insn_table[token.count('#')], token.count('1')

def make_regs(*strings):
    return dict((i+1, s) for i, s in enumerate(strings))

def run(insns, regs, verbose=False):
    pc = 0
    while pc < len(insns):
        if verbose:
            show(insns, pc, regs)
            print
        fn, n = insns[pc]
        pc += fn(n, regs)
    if verbose:
        show(insns, pc, regs)
    return regs

def do_add_one(n, regs):
    regs[n] += '1'
    return 1

def do_add_hash(n, regs):
    regs[n] += '#'
    return 1

def do_forward(n, regs):
    return n

def do_backward(n, regs):
    return -n

def do_case(n, regs):
    reg = regs[n]
    if not reg:   return 1
    ch, regs[n] = reg[0], reg[1:]
    if ch == '1': return 2
    if ch == '#': return 3
    assert False

insn_table = {1: do_add_one, 2: do_add_hash,
              3: do_forward, 4: do_backward,
              5: do_case}

def show(insns, pc=0, regs={}):
    left = ['%3s %s %d' % (abs(pc - addr) or '',
                           fn.__name__[3:],
                           n)
            for addr, (fn, n) in enumerate(insns)]
    right = ['\tr%d: %s' % item for item in sorted(regs.items())]
    print '\n'.join(abut(left, right))

## print '|\n'.join(abut('abc de ghi'.split(), 'XY TUV'.split())) + '|',
#. abcXY |
#. de TUV|
#. ghi   |

def abut(lines1, lines2):
    return flip(flip(lines1) + flip(lines2))

## flip(['abc', 'xy'])
#. ['ax', 'by', 'c ']

def flip(strings):
    return map(''.join, izip_longest(*strings, fillvalue=' '))
