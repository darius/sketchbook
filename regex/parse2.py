"""
Right-to-left top-down operator-precedence parser for regular expressions.
(Crude grammar.)
"""

def parse(string, maker):
    ts = list(string)

    def parse_expr(precedence):
        rhs = parse_factor(ts)
        while ts:
            if ts[-1] == '(': break
            op, prec = (maker.alt, 2) if ts[-1] == '|' else (maker.seq, 4)
            if prec < precedence: break
            chomp('|')
            rhs = op(parse_expr(prec + 1), rhs)
        return rhs

    def parse_factor(ts):
        if not ts or ts[-1] in '|(':
            return maker.empty
        elif chomp(')'):
            e = parse_expr(0)
            assert chomp('(')
            return e
        elif chomp('*'):
            return maker.many(parse_expr(6))
        else:
            return maker.lit(ts.pop())

    def chomp(token):
        matches = (ts and ts[-1] == token)
        if matches: ts.pop()
        return matches

    re = parse_expr(0)
    assert not ts
    return re

class TreeMaker:
    empty = 'empty'
    def lit(self, s): return repr(s)
    def alt(self, t1, t2): return 'Alt(%s, %s)' % (t1, t2)
    def seq(self, t1, t2): return 'Seq(%s, %s)' % (t1, t2)
    def many(self, t): return 'Many(%s)' % t

maker = TreeMaker()

def p(s): return parse(s, maker)

## p('')
#. 'empty'
## p('a')
#. "'a'"
## p('ab')
#. "Seq('a', 'b')"
## p('abc')
#. "Seq('a', Seq('b', 'c'))"
## p('a|b|c')
#. "Alt('a', Alt('b', 'c'))"
## p('ab||c')
#. "Alt(Seq('a', 'b'), Alt(empty, 'c'))"
## p('a*')
#. "Many('a')"
## p('ab*c')
#. "Seq('a', Seq(Many('b'), 'c'))"
## p('a(bc|d|)*e')
#. "Seq('a', Seq(Many(Alt(Seq('b', 'c'), Alt('d', empty))), 'e'))"
## p('(ab*c)')
#. "Seq('a', Seq(Many('b'), 'c'))"
## p('()')
#. 'empty'
