"""
Text Register Machine interpreter
http://www.indiana.edu/~iulg/trm/
Glossary:
  pc    program counter
  insn  instruction
  n     argument part of instruction
  reg   register
(regs is 0-indexed in Python, 1-indexed in the TRM model)
"""


# Smoke test

## show(parse('1#111##'))
#.     add_one 1 
#.   1 add_hash 3
#. 

## run(parse('1#111##'), ('', '', ''), verbose=True)
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
#. 
#. ['1', '', '#']


# 4.1 Program to move register contents

## move_r2_r1 = parse('11#####111111###111###1##1111####1#111111####')
## show(move_r2_r1, 0, ('', '1#1#11##'))
#.     case 2    	r1:         
#.   1 forward 6 	r2: 1#1#11##
#.   2 forward 3              
#.   3 add_hash 1             
#.   4 backward 4             
#.   5 add_one 1              
#.   6 backward 6             
#. 
## run(move_r2_r1, ('', '1#1#11##'))
#. ['1#1#11##', '']


from itertools import izip_longest
import re

def parse(program):
    assert re.match(r'(1+#{1,5})*$', program)
    tokens = re.findall(r'1+#{1,5}', program)
    return tuple(map(parse_insn, tokens))

def parse_insn(token):
    return insn_table[token.count('#')], token.count('1')
            
def run(insns, regs, verbose=False):
    pc = 0
    regs = list(regs)
    while pc < len(insns):
        if verbose:
            show(insns, pc, regs)
            print
        fn, n = insns[pc]
        pc = fn(n, pc, regs)
    if verbose:
        show(insns, pc, regs)
    return regs

def do_add_one(n, pc, regs):
    regs[n-1] += '1'
    return pc + 1

def do_add_hash(n, pc, regs):
    regs[n-1] += '#'
    return pc + 1

def do_forward(n, pc, regs):
    return pc + n

def do_backward(n, pc, regs):
    return pc - n

def do_case(n, pc, regs):
    reg = regs[n-1]
    if not reg:   return pc + 1
    ch, regs[n-1] = reg[0], reg[1:]
    if ch == '1': return pc + 2
    if ch == '#': return pc + 3
    assert False

insn_table = {1: do_add_one, 2: do_add_hash,
              3: do_forward, 4: do_backward,
              5: do_case}

def show(insns, pc=0, regs=()):
    left = ['%3s %s %d' % (('' if addr == pc else abs(pc - addr)),
                           fn.__name__[3:],
                           n)
            for addr, (fn, n) in enumerate(insns)]
    right = ['\tr%d: %s' % (r+1, reg)
             for r, reg in enumerate(regs)]
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
