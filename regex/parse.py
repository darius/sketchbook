"""
Parse regular expressions into regex structures.
"""

def make_parser(maker):
    return lambda s: parse(s, maker)

class Struct: pass

def parse(string, maker):
    input = iter(string)
    t = Struct()

    def eat():
        try: t._ = input.next()
        except StopIteration: t._ = None

    def chomp(c):
        if t._ == c:
            eat()
            return True
        return False

    def expect(c):
        if not chomp(c): raise SyntaxError

    """ Oversimplified grammar to start:
parse   = expr $.
expr    = term '|' expr
        / term.
term    = factor ![)|] term
        / factor.
factor  = prim stars.
stars   = '*' stars
        / .
prim    = '(' expr ')'                  
        / '\\' any
        / ![*+?|()\\] any.
        / ."""

    def parse_expr():
        term = parse_term()
        if chomp('|'): return maker.alt(term, parse_expr())
        else: return term

    def parse_term():
        factor = parse_factor()
        if t._ in (')', '|', None): return factor
        return maker.seq(factor, parse_term())
        
    def parse_factor():
        factor = parse_prim()
        while chomp('*'):
            factor = maker.many(factor)
        return factor

    def parse_prim():
        if chomp('('):
            prim = parse_expr()
            expect(')')
            return prim
        if chomp('\\'):
            if t._ is None: raise SyntaxError
            c = t._
            eat()
            return maker.lit(c)
        if t._ is None or t._ in '*()\\':
            return maker.empty
        c = t._
        eat()
        return maker.lit(c)

    eat()
    expr = parse_expr()
    if t._ is not None:
        raise SyntaxError
    return expr

class TreeMaker:
    empty = 'empty'
    def lit(self, s): return repr(s)
    def alt(self, t1, t2): return 'Alt(%s, %s)' % (t1, t2)
    def seq(self, t1, t2): return 'Seq(%s, %s)' % (t1, t2)
    def many(self, t): return 'Many(%s)' % t

p = make_parser(TreeMaker())

## p(r'')
#. 'empty'
## p(r'hello')
#. "Seq('h', Seq('e', Seq('l', Seq('l', 'o'))))"
## p(r'hello|goodbye')
#. "Alt(Seq('h', Seq('e', Seq('l', Seq('l', 'o')))), Seq('g', Seq('o', Seq('o', Seq('d', Seq('b', Seq('y', 'e')))))))"
## p(r'hello*')
#. "Seq('h', Seq('e', Seq('l', Seq('l', Many('o')))))"
## p(r'()')
#. 'empty'
## p(r'(hey)you')
#. "Seq(Seq('h', Seq('e', 'y')), Seq('y', Seq('o', 'u')))"
## p(r'hey*you')
#. "Seq('h', Seq('e', Seq(Many('y'), Seq('y', Seq('o', 'u')))))"
## p(r'h(ey)*you')
#. "Seq('h', Seq(Many(Seq('e', 'y')), Seq('y', Seq('o', 'u'))))"
## p(r'a\*b')
#. "Seq('a', Seq('*', 'b'))"
