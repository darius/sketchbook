"""
For convenience, I'm going to assume all data is comparable (<,=,>).
"""

from parson import Grammar

class Nuts(object):
    def __cmp__(self, other):
        return 0 if isinstance(other, Nuts) else 1
    def __repr__(self):
        return 'nuts'
    def call(self, argument):
        raise KeyError("Unknown key", argument) # XXX I guess?

nuts = Nuts()

## nuts < nuts
#. False
## nuts <= nuts
#. True
## nuts < 1
#. False
## 1 < nuts
#. True

def aggregate_all(xs):
    return reduce(mk_alt, xs, null)

def mk_alt(x, y):
    if isinstance(x, Nuts): return x
    if isinstance(y, Nuts): return y
    zs = merge(as_tuple(x), as_tuple(y))
    return zs[0] if 1 == len(zs) else Aggregate(zs)

def as_tuple(x):
    return x.xs if isinstance(x, Aggregate) else (x,)

def merge(xs, ys):
    zs = []
    j = 0
    for x in xs:
        while j < len(ys) and ys[j] < x:
            zs.append(ys[j])
            j += 1
        if j < len(ys) and ys[j] == x:
            j += 1
        zs.append(x)
    while j < len(ys):
        zs.append(ys[j])
        j += 1
    return tuple(zs)

class Aggregate(object):
    def __init__(self, xs):
        self.xs = xs
    def __cmp__(self, other):
        # TODO: "maps inherit ordering from their ranges
        #        m <=n iff  Ax. m.x <= n.x"
        # XXX this is actually a problem: it means maps only support a partial order,
        # not a total one. But my aggregates are represented by sorted lists, requiring
        # a total order. This is not immediately fatal, since the *elements* of an
        # aggregate can't be aggregates, but I don't feel like I'm on firm ground here,
        # since the elements could certainly be e.g. sets.
        #
        # I guess the way forward then would be for my aggregates to
        # be sorted on an *internal, implementation-defined*
        # comparison. And the <= operator (etc.) in the language is
        # separately implemented.
        if isinstance(other, Nuts):
            return -cmp(other, self)
        elif isinstance(other, Aggregate):
            return lex_cmp(self.xs, other.xs)
        else:
            # N.B. this assumes distributivity is expanded out elsewhere
            return lex_cmp(self.xs, (other,))
    def call(self, argument):
        return aggregate_all([Call(xi, argument) for xi in self.xs])
    def __repr__(self):
        return '(%s)' % ' | '.join(map(repr, self.xs))

def Null(): return null
null = Aggregate(())

## null < null
#. False
## null <= null
#. True
## null < 1
#. True
## 1 < null
#. False

class Set(object):
    def __init__(self, x):
        self.x = x
    def __repr__(self):
        return '{%r}' % (self.x,)

def lex_cmp(xs, ys):
    return cmp(xs, ys)

def Nil(): return nil

class Sequence(object):
    def __init__(self, xs):
        self.xs = xs
    def __cmp__(self, other):
        if isinstance(other, Sequence):
            return lex_cmp(self.xs, other.xs)
        else:
            # N.B. this assumes distributivity is expanded out elsewhere
            return lex_cmp(self.xs, (other,))
    def call(self, argument):
        # (m , n).x == m.(n.x)
        for x in reversed(self.xs):
            argument = Call(x, argument)
        return argument
    def __repr__(self):
        if len(self.xs) == 1:
            return repr(self.xs[0])
        return '(%s)' % ', '.join(map(repr, self.xs))

nil = Sequence(())

# TODO: define a List class instead?
# Then at least we could change how it's displayed.
def mk_list(x):
    if isinstance(x, Sequence): return x.xs
    else:                       return (x,)

def append(x, y):
    assert not isinstance(x, Nuts)
    assert not isinstance(y, Nuts)

    # x , (y | z) == x,y | x,z
    # (x | y) , z == x,z | y,z
    if isinstance(x, Aggregate):
        return aggregate_all([append(xi, y) for xi in x.xs])
    if isinstance(y, Aggregate):
        return aggregate_all([append(x, yi) for yi in y.xs])

    xs = x.xs if isinstance(x, Sequence) else (x,)
    ys = y.xs if isinstance(y, Sequence) else (y,)
    zs = xs + ys
    return zs[0] if len(zs) == 1 else Sequence(zs)

class Map(object):
    def __init__(self, key, val):
        self.key = key
        self.val = val
    def __cmp__(self, other):
        # I'm making up this behavior here...
        if isinstance(other, Map):
            return cmp((self.key, self.val), 
                       (other.key, other.val))
        else:
            return -cmp(other, (Map, self.key, self.val))
    def call(self, argument):
        return self.val if argument == self.key else null
    def __repr__(self):
        return '(%r := %r)' % (self.key, self.val)

def Call(x, y):
    assert not isinstance(y, Nuts)  # XXX I'm not sure what to do
    if isinstance(y, Aggregate):
        return aggregate_all([Call(x, yi) for yi in y.xs])
    else:
        return x.call(y)

import operator
Le, Lt, Ge, Gt, Eq, Ne = [getattr(operator, name) for name in 'le lt ge gt eq ne'.split()]

grammar_text = r"""
program :  FNORD e :end.

e       :  e1 ('|' e1 :mk_alt)*.
e1      :  e2 (',' e2 :append)*.
e2      :  e3 (':=' e3 :Map)?.
e3      :  e4 ('<=' e4 :Le
              |'<'  e4 :Lt
              |'>=' e4 :Ge
              |'>'  e4 :Gt
              |'==' e4 :Eq
              |'!=' e4 :Ne)?.
e4      :  eN ('.' eN :Call)?.    # N.B. nonassociative for now

eN      :  name
        |  number
        |  '(' e ')'
        |  '[' e ']' :mk_list
        |  '{' e '}' :Set.

FNORD  ~:  /\s*/.
name   ~:  /Null\b/ FNORD  :Null
        |  /Nuts\b/ FNORD  :Nuts
        |  /Nil\b/ FNORD   :Nil.
number ~:  /([0-9]+)/ FNORD :int.
"""

parser = Grammar(grammar_text)(**globals())
parse_program = parser.program.expecting_one_result()

## parse_program('1 | 3 | (2 | Null)')
#. (1 | 2 | 3)
## parse_program('1, 3 , (2 , Nil)')
#. (1, 3, 2)
## parse_program('1 , 3 | (2 , Nil)')
#. ((1, 3) | 2)
## parse_program('(1 | 2) , (3 | 4)')
#. ((1, 3) | (1, 4) | (2, 3) | (2, 4))
## parse_program('{1 | 2 | 4}')
#. {(1 | 2 | 4)}
## parse_program('[1 , 2 , 4]')
#. (1, 2, 4)
## parse_program('1 := 2')
#. (1 := 2)
## parse_program('(1 := 2) . 1')
#. 2
## parse_program('(1 := 2 | 1 := 3) . 1')
#. (2 | 3)
## parse_program('(1 := 2 | 2 := 3) . 1')
#. 2
## parse_program('1 <= (2 | 1)')
#. True
## parse_program('(1 := 2) . (1 | 2)')
#. 2
## parse_program('(1 := 2 | 2 := 4 | 4 := 8) . (1 | 2)')
#. (2 | 4)
## parse_program('((2 := 4), (1 := 2)) . 1')
#. 4
