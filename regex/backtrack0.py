"""
Matching derived by transformation from generate.py.
"""

def match(re, s): return re(s)

def lit(char):
    return lambda s: char == s

def alt(re1, re2):
    return lambda s: re1(s) or re2(s)

def empty(s): return s == ''

def seq(re1, re2):
    def me(s):
        return any(re1(s[:i]) and re2(s[i:])
                   for i in range(len(s) + 1))
    return me

def many(re):
    def me(s):
        if s == '': return True
        return any(re(s[:i]) and me(s[i:])
                   for i in range(1, len(s) + 1))
    return me

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
## match(many(lit('a')), 'ax')
#. False

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

## match(many(many(lit('x'))), 'xxxx')
#. True

# Had a bug: empty forced a match regardless of the continuation.
## match(seq(empty, lit('x')), '')
#. False
## match(seq(empty, lit('x')), 'x')
#. True
