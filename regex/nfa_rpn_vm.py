"""
The Thompson algorithm again but starting from a regex in RPN, as
Thompson did. In a more C-like style now, compiling to a virtual
machine. We differ from Thompson in parsing from right to left, and
thus needing fewer jump instructions and backpatching only for loops.
"""

def match(re, s):
    re = list(re)
    insns = []
    start = parse(insns, re, emit(insns, expect, EOF))
    assert not re, "Syntax error"
    return run(insns, start, s)

def show(insns, pc):
    for k, (operator, operand) in enumerate(insns):
        print '%2d %s %-6s %s' % (k,
                                  '*' if k == pc else ' ',
                                  operator.__name__,
                                  operand)

def parse(insns, re, k):
    if not re:
        return k
    else:
        c = re.pop()
        if c == '.':            # (Concatenation operator)
            rhs = parse(insns, re, k)
            return parse(insns, re, rhs)
        elif c == '|':
            rhs = parse(insns, re, k)
            return emit_alt(insns, parse(insns, re, k), rhs)
        elif c == '*':
            star = emit_loop(insns, k)
            patch(insns, star, parse(insns, re, star))
            return star
        else:
            return emit_expect(insns, c, k)

def emit_expect(insns, literal, k):
    emit_jump(insns, k)
    return emit(insns, expect, literal)

def emit_alt(insns, k1, k2):
    emit_jump(insns, k1)
    return emit(insns, alt, k2)

def emit_loop(insns, k):
    return emit_alt(insns, k, None)

def patch(insns, k, target):
    insns[k][1] = target

def emit_jump(insns, k):
    if len(insns) - 1 != k:
        emit(insns, jump, k)

def emit(insns, operation, operand):
    insns.append([operation, operand])
    return len(insns) - 1

def run(insns, start, s):
    states = set([start])
    for c in s:
        states = step(insns, states, c)
    return ACCEPTED in step(insns, states, EOF)

def step(insns, states, c):
    next = set()
    while states:
        pc = states.pop()
        while pc is not None:
            operator, operand = insns[pc]
            pc = operator(states, next, pc, c, operand)
    return next

def jump(states, next, pc, c, k):
    return k
def expect(states, next, pc, c, literal):
    if c == literal: next.add(pc - 1)
    return None
def alt(states, next, pc, c, k):
    states.add(k)
    return pc - 1

EOF, ACCEPTED = 'EOF', -1

## match('', '')
#. True
## match('', 'A')
#. False
## match('x', '')
#. False
## match('x', 'y')
#. False
## match('x', 'x')
#. True
## match('x', 'xx')
#. False
## match('xx.', 'xx')
#. True
## match('ab.', '')
#. False
## match('ab.', 'ab')
#. True
## match('ab|', '')
#. False
## match('ab|', 'a')
#. True
## match('ab|', 'b')
#. True
## match('ab|', 'x')
#. False
## match('a*', '')
#. True
## match('a*', 'a')
#. True
## match('a*', 'x')
#. False
## match('a*', 'aa')
#. True
## match('a*', 'ax')
#. False
## match('a*', 'aaa')
#. True

## complicated = 'ab.axy..|*z.'
## match(complicated, '')
#. False
## match(complicated, 'z')
#. True
## match(complicated, 'abz')
#. True
## match(complicated, 'ababaxyab')
#. False
## match(complicated, 'ababaxyabz')
#. True
## match(complicated, 'ababaxyaxz')
#. False

tests = """\
ab.c.d.e.f.g.   1 abcdefg
ab|*a.          0 ababababab
ab|*a.          1 aaaaaaaaba
ab|*a.          0 aaaaaabac
abc|*.d.        1 abccbcccd
abc|*.d.        0 abccbcccde
""".splitlines()
for line in tests:
    re, should_match, s = line.split()
    assert int(should_match) == match(re, s), 'match(%r, %r)' % (re, s)
