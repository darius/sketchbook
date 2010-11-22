"""
Like deriv0.py but with less-verbose code:
represent an RE by a deriv procedure with a nullable field attached.
"""

def match(re, s):
    for c in s:
        re = re(c)
    return re.nullable

def mark(nullable, deriv):
    deriv.nullable = nullable
    return deriv

fail = mark(False, lambda c: fail)
empty = mark(True, lambda c: fail)

def lit(literal):
    return mark(False, lambda c: empty if c == literal else fail)

def alt(re1, re2):
    return mark(re1.nullable or re2.nullable,
                lambda c: alt(re1(c), re2(c)))

def seq(re1, re2):
    if re1.nullable:
        def sequence(c): return alt(seq(re1(c), re2), re2(c))
    else:
        def sequence(c): return seq(re1(c), re2)
    return mark(re1.nullable and re2.nullable, sequence)

def many(re):
    def loop(c): return seq(re(c), loop)
    return mark(True, loop)

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
### match(lit('abc'), 'abc')
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
## match(many(many(lit('x'))), 'xxxxy')
#. False

## match(seq(empty, lit('x')), '')
#. False
## match(seq(empty, lit('x')), 'x')
#. True
