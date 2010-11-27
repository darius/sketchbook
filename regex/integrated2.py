"""
Integrate the right-to-left top-down operator-precedence parser with
the simplest terminating NFA code. Almost C-level code now.
"""

def match(re, s): return run(prepare(re), s)

def run((insns, start), s):
    agenda = set()
    spread(insns, start, agenda, set())
    for c in s:
        agenda = step(insns, agenda, c)
        if not agenda: break    # Redundant test, can speed it
    return 0 in agenda          # 0 for the accepting state

def spread(insns, pc, agenda, visited):
    while True:
        op, arg = insns[pc]
        if op == 'expect':
            agenda.add(pc)
            return
        elif op == 'jump':
            pc = arg
        elif op == 'split':
            if pc in visited:
                return
            visited.add(pc)
            spread(insns, arg, agenda, visited)
            pc -= 1

def step(insns, agenda, c):
    visited, next = set(), set()
    for pc in agenda:
        op, arg = insns[pc]
        assert op == 'expect'
        if arg == c: spread(insns, pc-1, next, visited)
    return next
    
def emit_fork(insns, k): return emit(insns, 'split', None, k)
def patch(insns, k, target): insns[k][1] = target

def emit(insns, op, arg, k):
    if len(insns) - 1 != k:
        insns.append(['jump', k])
    insns.append([op, arg])
    return len(insns) - 1

def prepare(re):
    ts = list(re)
    insns = []

    def parse_expr(precedence, k):
        rhs = parse_factor(ts, k)
        while ts:
            if ts[-1] == '(': break
            prec = 2 if ts[-1] == '|' else 4
            if prec < precedence: break
            if chomp('|'):
                rhs = emit(insns, 'split', rhs, parse_expr(prec+1, k))
            else:
                rhs = parse_expr(prec+1, rhs)
        return rhs

    def parse_factor(ts, k):
        if not ts or ts[-1] in '|(':
            return k
        elif chomp(')'):
            e = parse_expr(0, k)
            assert chomp('(')
            return e
        elif chomp('*'):
            fork = emit_fork(insns, k)
            patch(insns, fork, parse_expr(6, fork))
            return fork
        else:
            return emit(insns, 'expect', ts.pop(), k)

    def chomp(token):
        matches = (ts and ts[-1] == token)
        if matches: ts.pop()
        return matches

    start = parse_expr(0, emit(insns, 'expect', None, -1))
    assert not ts
    return insns, start


def show(insns, pc):
    for k, (op, arg) in enumerate(insns):
        print '%2d %s %-6s %s' % (k, '*' if k == pc else ' ', op, arg)

## match('', '')
#. True
## match('', 'a')
#. False
## match('a', '')
#. False
## match('a', 'a')
#. True
## match('a', 'aa')
#. False
## match('ab', '')
#. False
## match('ab', 'ab')
#. True
## match('abc', 'ab')
#. False
## match('abc', 'abc')
#. True
## match('abc', 'abcd')
#. False
## match('a|b|c', '')
#. False
## match('a|b|c', 'a')
#. True
## match('a|b|c', 'b')
#. True
## match('a|b|c', 'c')
#. True
## match('a|b|c', 'd')
#. False
## match('ab||c', '')
#. True
## match('ab||c', 'a')
#. False
## match('ab||c', 'b')
#. False
## match('ab||c', 'c')
#. True
## match('ab||c', 'ab')
#. True
## match('a*', '')
#. True
## match('a*', 'a')
#. True
## match('a*', 'aa')
#. True
## match('a*', 'aab')
#. False
## match('ab*c', '')
#. False
## match('ab*c', 'ab')
#. False
## match('ab*c', 'ac')
#. True
## match('ab*c', 'abc')
#. True
## match('ab*c', 'abbbbc')
#. True
## match('ab*c', 'abbbbd')
#. False
## match('a(bc|d|)*e', '')
#. False
## match('a(bc|d|)*e', 'a')
#. False
## match('a(bc|d|)*e', 'ae')
#. True
## match('a(bc|d|)*e', 'abe')
#. False
## match('a(bc|d|)*e', 'ade')
#. True
## match('a(bc|d|)*e', 'abce')
#. True
## match('a(bc|d|)*e', 'abcde')
#. True
## match('(ab*c)', '')
#. False
## match('(ab*c)', 'abbbbc')
#. True
## match('()', '')
#. True
## match('()', 'a')
#. False
## match('()', 'a')
#. False
## match('()*', 'a')
#. False
## match('()*', '')
#. True
## match('a**', 'aaa')
#. True
## match('a**', 'b')
#. False
