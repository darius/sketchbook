"""
Regular expression matching by backtracking. Simple but can take up to
infinite time.
"""

def match(re, s):
    return any(s1 == '' for s1 in re(s))

## match(fail, '')
#. False
## match(empty, '')
#. True
## match(empty, 'A')
#. False
## match(lit('x'), '')
#. False
## match(lit('x'), 'y')
#. False
## match(lit('x'), 'x')
#. True
## match(lit('x'), 'xx')
#. False
## match(lit('abc'), 'abc')
#. True
## match(seq(lit('a'), lit('b')), '')
#. False
## match(seq(lit('a'), lit('b')), 'ab')
#. True
## match(alt(lit('a'), lit('b')), 'b')
#. True
## match(alt(lit('a'), lit('b')), 'a')
#. True
## match(alt(lit('a'), lit('b')), 'x')
#. False
## match(many(lit('a')), '')
#. True
## match(many(lit('a')), 'a')
#. True
## match(many(lit('a')), 'x')
#. False
## match(many(lit('a')), 'aa')
#. True

fail = lambda s: []

empty = lambda s: [s]

def lit(c):
    return lambda s: [s[len(c):]] if s.startswith(c) else []

def seq(re1, re2):
    return lambda s: [s2 for s1 in re1(s) for s2 in re2(s1)]

def alt(re1, re2):
    return lambda s: re1(s) + re2(s)

def many(re):
    def star(s):
        acc = [s]
        for s1 in re(s):
            acc.extend(star(s1))
        return acc
    return star

## complicated = seq(many(alt(seq(lit('a'), lit('b')), seq(lit('a'), seq(lit('x'), lit('y'))))), lit('z'))
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
