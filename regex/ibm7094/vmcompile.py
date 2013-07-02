"""
The first compiler from Thompson 1968, "Regular expression search
algorithm", ported from Algol and IBM 7094. Support code in runtime.vm.s.
"""

def toplevel(postfix):
    print '        jump ,,init'
    print 'code'
    for line in nfa_from_postfix(postfix):
        print '        ' + line
    print
    for line in open('runtime.vm.s'):
        print line.rstrip('\n')

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
            code.append(instruction("jump ,,code+%d", pc+1))
            code.append(instruction("ifne r1,'%c',fail", char))
            code.append(instruction("jump r4,,nnode"))
            stack.append(pc)
        elif char == '.':
            stack.pop()
        elif char == '*':
            code.append(instruction("jump r4,,cnode"))
            code.append(code[stack[-1]])
            code[stack[-1]] = instruction("jump ,,code+%d", pc)
        elif char == '|':
            code.append(instruction("jump ,,code+%d", pc+4))
            code.append(instruction("jump r4,,cnode"))
            code.append(code[stack[-1]])
            code.append(code[stack[-2]])
            code[stack[-2]] = instruction("jump ,,code+%d", pc+1)
            code[stack[-1]] = instruction("jump ,,code+%d", pc+4)
            stack.pop()
        else:
            assert False
    code.append(instruction("jump ,,found"))
    return code

def instruction(template, *args):
    return template % args

## comp('ab.')
#. code
#.  0	jump ,,code+1
#.  1	ifne r1,'a',fail
#.  2	jump r4,,nnode
#.  3	jump ,,code+4
#.  4	ifne r1,'b',fail
#.  5	jump r4,,nnode
#.  6	jump ,,found
#. 

## comp('ab|')
#. code
#.  0	jump ,,code+7
#.  1	ifne r1,'a',fail
#.  2	jump r4,,nnode
#.  3	jump ,,code+10
#.  4	ifne r1,'b',fail
#.  5	jump r4,,nnode
#.  6	jump ,,code+10
#.  7	jump r4,,cnode
#.  8	jump ,,code+4
#.  9	jump ,,code+1
#. 10	jump ,,found
#. 

## comp('abc|*.d.')
#. code
#.  0	jump ,,code+1
#.  1	ifne r1,'a',fail
#.  2	jump r4,,nnode
#.  3	jump ,,code+13
#.  4	ifne r1,'b',fail
#.  5	jump r4,,nnode
#.  6	jump ,,code+13
#.  7	ifne r1,'c',fail
#.  8	jump r4,,nnode
#.  9	jump ,,code+13
#. 10	jump r4,,cnode
#. 11	jump ,,code+7
#. 12	jump ,,code+4
#. 13	jump r4,,cnode
#. 14	jump ,,code+10
#. 15	jump ,,code+16
#. 16	ifne r1,'d',fail
#. 17	jump r4,,nnode
#. 18	jump ,,found
#. 

if __name__ == '__main__':
    import sys
    toplevel(sys.argv[1])
