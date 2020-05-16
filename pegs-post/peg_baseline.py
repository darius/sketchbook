"""
sketch of minimal PEG demo
"""

from parson import Grammar

def parse(g, start, s):
    for _, vals in g[start](g, s, (0, ())):
        return vals
    return None

def Either(p, q):
    def either(g, s, st):
        return p(g, s, st) or q(g, s, st)
    return either

def Chain(p, q):
    def chain(g, s, st1):
        return [st3 for st2 in p(g, s, st1) for st3 in q(g, s, st2)]
    return chain

def Literal(string):
    def literal(g, s, (i, vals)):
        return ([(i+len(string), vals+(string,))] if s.startswith(string, i)
                else [])
    return literal

def Call(name):
    def call(g, s, st):
        return [(i, (((name,)+vals),)) for i, vals in g[name](g, s, st)]
    return call

pegging = Grammar(r"""rule* :end.

rule: name '<-' pe :hug.
pe: e1 ('/' pe :Either)?.
e1: e2 (e1 :Chain)?.
e2: name :Call
  | literal :Literal.

name:    /([A-Za-z_][A-Za-z_0-9]*)/.
literal: /'([^']*)'/.
FNORD:   /\s+/?.
""")(**globals())

## 'b'.startswith('b', 0)
#. True
eg1 = dict(pegging(" a <- 'b' / 'c' "))
## parse(eg1, 'a', 'b')
#. ('b',)
## parse(eg1, 'a', 'd')
