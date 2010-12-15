"""
"Strong star normal form"
From "The complexity of regular-(like)-expressions"
http://www.springerlink.com/content/978-3-642-14454-7/#section=754924&page=3&locus=34
"""

## Many(Seq(Optional(Lit('x')), Optional(Lit('y')))).black()
#. ((x|y))*

def normalize(re): return re.black()

class Lit:
    nullable = False
    def __init__(self, c):
        self.c = c
    def __repr__(self): return self.c
    def white(self): return self
    def black(self): return self

class Alt:
    def __init__(self, re1, re2):
        self.re1 = re1
        self.re2 = re2
        self.nullable = re1.nullable or re2.nullable
    def __repr__(self):
        return '(%r|%r)' % (self.re1, self.re2)
    def white(self):
        return Alt(self.re1.white(), self.re2.white())
    def black(self):
        return Alt(self.re1.black(), self.re2.black())

class Optional():
    nullable = True
    def __init__(self, re):
        self.re = re
    def __repr__(self):
        return '(%r)?' % (self.re)
    def white(self):
        return self.re.white()
    def black(self):
        return self.re.black() if self.re.nullable else Optional(self.re.black())

class Many:
    nullable = True
    def __init__(self, re):
        self.re = re
    def __repr__(self):
        return '(%r)*' % (self.re)
    def white(self):
        return self.re.white()
    def black(self):
        return Many(self.re.black().white())

class Seq:
    def __init__(self, re1, re2):
        self.re1 = re1
        self.re2 = re2
        self.nullable = re1.nullable and re2.nullable
    def __repr__(self):
        return '%r%r' % (self.re1, self.re2)
    def white(self):
        return Alt(self.re1.white(), self.re2.white()) if self.nullable else self
    def black(self):
        return Seq(self.re1.black(), self.re2.black())
