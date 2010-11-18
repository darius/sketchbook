"""
The Thompson algorithm again but starting from a regex in RPN, as
Thompson did. In a more C-like style now except for the representation
of NFA states.
"""

def match(re, s):
    re = list(re)
    nfa = parse(re, accept)
    assert not re, "Syntax error"
    return run(nfa, s)

def parse(re, k):
    if not re:
        return k
    else:
        c = re.pop()
        if c == '.':            # (Concatenation operator)
            rhs = parse(re, k)
            return parse(re, rhs)
        elif c == '|':
            rhs = parse(re, k)
            return alt(parse(re, k), rhs)
        elif c == '*':
            star = loop(k)
            star.target = parse(re, star)
            return star
        else:
            return expect(c, k)

def expect(literal, k):
    return lambda c: set([k]) if c == literal else set()

def alt(k1, k2):
    return lambda c: k1(c) | k2(c)

def loop(k):
    def star(c): return k(c) | star.target(c)
    return star

def run(nfa, s):
    states = set([nfa])
    for c in s:
        states = set.union(*[state(c) for state in states])
    return any(ACCEPTED in state(EOF) for state in states)

ACCEPTED, EOF = object(), object()
accept = expect(EOF, ACCEPTED)

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
