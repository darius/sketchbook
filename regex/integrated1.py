"""
Integrate the right-to-left top-down operator-precedence parser with
the simplest terminating NFA code.
"""

def match(re, s): return run(prepare(re), s)

def run(states, s):
    for c in s:
        states = set.union(*[state(c) for state in states])
    return accepting_state in states

def accepting_state(c): return set()
def expecting_state(char, k): return lambda c: k(set()) if c == char else set()

def state_node(state): return lambda seen: set([state])
def alt_node(k1, k2):  return lambda seen: k1(seen) | k2(seen)
def loop_node(k, make_k):
    def loop(seen):
        if loop in seen: return set()
        seen.add(loop)
        return k(seen) | looping(seen)
    looping = make_k(loop)
    return loop

def prepare(re):
    ts = list(re)

    def parse_expr(precedence, k):
        rhs = parse_factor(ts, k)
        while ts:
            if ts[-1] == '(': break
            prec = 2 if ts[-1] == '|' else 4
            if prec < precedence: break
            if chomp('|'):
                rhs = alt_node(parse_expr(prec + 1, k), rhs)
            else:
                rhs = parse_expr(prec + 1, rhs)
        return rhs

    def parse_factor(ts, k):
        if not ts or ts[-1] in '|(':
            return k
        elif chomp(')'):
            e = parse_expr(0, k)
            assert chomp('(')
            return e
        elif chomp('*'):
            return loop_node(k, lambda loop: parse_expr(6, loop))
        else:
            return state_node(expecting_state(ts.pop(), k))

    def chomp(token):
        matches = (ts and ts[-1] == token)
        if matches: ts.pop()
        return matches

    k = parse_expr(0, state_node(accepting_state))
    assert not ts
    return k(set())

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
