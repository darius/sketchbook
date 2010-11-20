"""
The Thompson algorithm again but starting from a regex in RPN, as
Thompson did. In a more C-like style now, compiling to a virtual
machine. We differ from Thompson in parsing from right to left, and
thus needing fewer jump instructions and backpatching only for loops.
Also in detecting loops at match-time -- we should always terminate,
if this is correct.
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
            fork = emit_fork(insns, k)
            patch(insns, fork, parse(insns, re, fork))
            return fork
        elif c == '?':
            return emit_alt(insns, parse(insns, re, k), k)
        elif c == '+':
            fork = emit_fork(insns, k)
            plus = parse(insns, re, fork)
            patch(insns, fork, plus)
            return plus
        else:
            return emit_expect(insns, c, k)

def emit_expect(insns, literal, k):
    emit_jump(insns, k)
    return emit(insns, expect, literal)

def emit_alt(insns, k1, k2):
    emit_jump(insns, k1)
    return emit(insns, alt, k2)

def emit_fork(insns, k):
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
    agenda = set([start])
    for c in s:
        agenda = step(insns, agenda, c)
        if not agenda: break    # Redundant test, can speed it
    return ACCEPTED in step(insns, agenda, EOF)

def step(insns, agenda, c):
    done, next = set(), set()
    while agenda:
        pc = agenda.pop()
        while pc is not None:
            done.add(pc) # TODO: we could get away with only adding loop headers
            operator, operand = insns[pc]
            pc = operator(done, agenda, next, pc, c, operand)
    return next

def jump(done, agenda, next, pc, c, k):
    return (k not in done) and k
def expect(done, agenda, next, pc, c, literal):
    if c == literal: next.add(pc - 1)
    return None
def alt(done, agenda, next, pc, c, k):
    if k not in done: agenda.add(k)
    return pc-1

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
ab?.c.          0 abbc
ab?.c.          1 abc
ab?.c.          1 ac
ab.+c.          0 c
ab.+c.          1 abc
ab.+c.          1 ababc
a**x.           1 aaax
""".splitlines()
for line in tests:
    re, should_match, s = line.split()
    assert int(should_match) == match(re, s), 'match(%r, %r)' % (re, s)
