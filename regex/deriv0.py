"""
Regular expression matching using Brzozowski derivatives.
"""

def match(re, s):
    for c in s:
        re = re.deriv(c)
    return re.nullable

class Fail:
    nullable = False
    def deriv(self, c):
        return self
fail = Fail()

class Empty:
    nullable = True
    def deriv(self, c):
        return fail
empty = Empty()

class Lit:
    nullable = False
    def __init__(self, c):
        assert len(c) == 1
        self.c = c
    def deriv(self, c):
        return empty if c == self.c else fail

class Alt:
    def __init__(self, re1, re2):
        self.nullable = re1.nullable or re2.nullable
        self.re1 = re1
        self.re2 = re2
    def deriv(self, c):
        return Alt(self.re1.deriv(c), self.re2.deriv(c))

class Seq:
    def __init__(self, re1, re2):
        self.nullable = re1.nullable and re2.nullable
        self.re1 = re1
        self.re2 = re2
    def deriv(self, c):
        blocking = Seq(self.re1.deriv(c), self.re2)
        if self.re1.nullable: return Alt(blocking, self.re2.deriv(c))
        else: return blocking

class Many:
    nullable = True
    def __init__(self, re):
        self.re = re
    def deriv(self, c):
        return Seq(self.re.deriv(c), self)


## match(fail, '')
#. False
## match(empty, '')
#. True
## match(empty, 'A')
#. False
## match(Lit('x'), '')
#. False
## match(Lit('x'), 'y')
#. False
## match(Lit('x'), 'x')
#. True
## match(Lit('x'), 'xx')
#. False
### match(Lit('abc'), 'abc')
## match(Seq(Lit('a'), Lit('b')), '')
#. False
## match(Seq(Lit('a'), Lit('b')), 'ab')
#. True
## match(Alt(Lit('a'), Lit('b')), 'b')
#. True
## match(Alt(Lit('a'), Lit('b')), 'a')
#. True
## match(Alt(Lit('a'), Lit('b')), 'x')
#. False
## match(Many(Lit('a')), '')
#. True
## match(Many(Lit('a')), 'a')
#. True
## match(Many(Lit('a')), 'x')
#. False
## match(Many(Lit('a')), 'aa')
#. True

## complicated = Seq(Many(Alt(Seq(Lit('a'), Lit('b')), Seq(Lit('a'), Seq(Lit('x'), Lit('y'))))), Lit('z'))
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
