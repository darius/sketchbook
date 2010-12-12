"""
The first compiler from Thompson 1968, "Regular expression search
algorithm", ported from Algol. Support code in thompson.s.
"""

def comp(postfix):
    print 'code'
    for i, line in enumerate(nfa_from_postfix(postfix)):
        print '%2d\t%s' % (i, line)

def nfa_from_postfix(postfix):
    code = []
    stack = []
    for char in postfix:
        pc = len(code)
        if char not in '.*|':
            code.append(instruction("tra code+%d", pc+1))
            code.append(instruction("txl fail, 1, -'%c'-1", char))
            code.append(instruction("txh fail, 1, -'%c'", char))
            code.append(instruction("tsx nnode, 4"))
            stack.append(pc)
        elif char == '.':
            stack.pop()
        elif char == '*':
            code.append(instruction("tsx cnode, 4"))
            code.append(code[stack[-1]])
            code[stack[-1]] = instruction("tra code+%d", pc)
        elif char == '|':
            code.append(instruction("tra code+%d", pc+4))
            code.append(instruction("tsx cnode, 4"))
            code.append(code[stack[-1]])
            code.append(code[stack[-2]])
            code[stack[-2]] = instruction("tra code+%d", pc+1)
            code[stack[-1]] = instruction("tra code+%d", pc+4)
            stack.pop()
        else:
            assert False
    code.append(instruction("tra found"))
    return code

def instruction(template, *args):
    return template % args

## comp('ab.')
#. code
#.  0	tra code+1
#.  1	txl fail, 1, -'a'-1
#.  2	txh fail, 1, -'a'
#.  3	tsx nnode, 4
#.  4	tra code+5
#.  5	txl fail, 1, -'b'-1
#.  6	txh fail, 1, -'b'
#.  7	tsx nnode, 4
#.  8	tra found
#. 

## comp('abc|*.d.')
#. code
#.  0	tra code+1
#.  1	txl fail, 1, -'a'-1
#.  2	txh fail, 1, -'a'
#.  3	tsx nnode, 4
#.  4	tra code+16
#.  5	txl fail, 1, -'b'-1
#.  6	txh fail, 1, -'b'
#.  7	tsx nnode, 4
#.  8	tra code+16
#.  9	txl fail, 1, -'c'-1
#. 10	txh fail, 1, -'c'
#. 11	tsx nnode, 4
#. 12	tra code+16
#. 13	tsx cnode, 4
#. 14	tra code+9
#. 15	tra code+5
#. 16	tsx cnode, 4
#. 17	tra code+13
#. 18	tra code+19
#. 19	txl fail, 1, -'d'-1
#. 20	txh fail, 1, -'d'
#. 21	tsx nnode, 4
#. 22	tra found
#. 
