# A list is either () or (head, list).
# list = () | (head, list)

def make_list(xs): return (xs[0], make_list(xs[1:])) if xs else ()

L = make_list('abcd')
## L
#. ('a', ('b', ('c', ('d', ()))))


# A zipper is a 'point' in the list.
# zip = ('root', list) | ((zip, head), list)

def make_zipper(list): return ('root', list)

def at_root((before, _)): return before == 'root'
def get_right((_, after)): return after

def replace_right((before, _), tail): return (before, tail)

def left(((before, head), after)):  return (before, (head, after))
def right((before, (head, after))): return ((before, head), after)

z = make_zipper(L)
## z
#. ('root', ('a', ('b', ('c', ('d', ())))))
## at_root(z)
#. True
## at_root(right(z))
#. False
## get_right(right(z))
#. ('b', ('c', ('d', ())))
## get_right(left(right(z)))
#. ('a', ('b', ('c', ('d', ()))))
