# A tree is either () or (left, val, right).

T = (((),'a',()),  'b',  ( ((),'c',()), 'd', ()))


# A zipper is a 'point' in the tree.
# zipper = (context, tree)
# context = ('top', _, _, _)
#         | ('left', context, val, right) meaning a hole (*, val, right)
#         | ('right', context, left, val) meaning a hole (left, val, *)

def make_zipper(tree):
    return ('top', None, None, None), tree

def at_top(((tag, _1, _2, _3), tree)): return tag == 'top'
def get_tree((_, tree)): return tree
def replace_tree((context, _), tree): return context, tree

def left((context, (left, val, right))):  return ('left', context, val, right), left
def right((context, (left, val, right))): return ('right', context, left, val), right

def up(((tag, context, x, y), tree)):
    if tag == 'left':
        val, right = x, y
        return context, (tree, val, right)
    elif tag == 'right':
        left, val = x, y
        return context, (left, val, tree)
    else:
        assert False

z = make_zipper(T)
## z
#. (('top', None, None, None), (((), 'a', ()), 'b', (((), 'c', ()), 'd', ())))
## at_top(z)
#. True
## at_top(right(z))
#. False
## at_top(up(right(z)))
#. True

## get_tree(z)
#. (((), 'a', ()), 'b', (((), 'c', ()), 'd', ()))
## get_tree(right(z))
#. (((), 'c', ()), 'd', ())
## get_tree(left(right(z)))
#. ((), 'c', ())

## get_tree(replace_tree(left(right(z)), ()))
#. ()
## get_tree(up(up(replace_tree(left(right(z)), ()))))
#. (((), 'a', ()), 'b', ((), 'd', ()))
