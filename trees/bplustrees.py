"""
Let's see if I can reconstruct B+ trees from this draft post by Ezekiel:
https://github.com/tehgeekmeister/dadabass/blob/b_plus_tree/notes/b_plus_tree.md

A tree represents a map from keys to values. It's built of three node types,
each represented by a 3-tuple:

  'root', keys, kids
  'branch', keys, kids    (Called 'internal node' in the post.)
  'leaf', keys, values

(I think we could ditch the 'root' tag and just say that the branch we start with
is the root.)
"""

import math

def what_I_represent(bpt):
    "Abstraction function for our B+ tree type."
    result = {}
    def walk(node):
        tag, keys, xs = node
        if tag in ('root','branch'):
            kids = xs
            for kid in kids:
                walk(kid)
        elif tag == 'leaf':
            values = xs
            result.update(zip(keys, values))
    walk(bpt)
    return result

N = 4 # Our node-size constant; pretty arbitrary. Here's a rather
      # small value to make testing easier. (We should test with
      # larger values as well, since N=4 happens to make the root
      # and branch kinds more similar than in general, as Ezekiel
      # pointed out.)
assert N%2 == 0  # TODO come back and see what if this is false

def check_bpt(bpt):
    """
    Check the representation invariant for our B+ tree type:

    * There's exactly one root.
        XXX why can't the root be a leaf instead of a branch?
    * The leaves are all at the same depth.
    * For all node kinds, len(keys) < N
    * For root and branches, len(keys) == len(kids)-1
    * For leaves, len(keys) == len(values)
    * For branches, ceil(N//2) <= len(kids)
    *   XXX Shouldn't there be a similar invariant for leaves?
            Could we just have a common invariant on len(keys)?
    * For all kinds, keys are distinct and sorted ascending:
      for i in range(len(keys)-1):
          keys[i] < keys[i+1]
    * Root and branches have keys related to their kids':
      for i in range(len(keys)):
          all of kids[i] and descendants' keys < keys[i] <= all of kids[i+1] and descendants' keys
      Where the kid key is in a branch, the <= is strengthened to a <.
    """
    tag, _, kids = bpt
    assert tag == 'root'

    # First compute the depth.
    depth = 0
    while kids and tag != 'leaf':
        tag, _, kids = kids[0]
        depth += 1

    def checking(node, d, lo, hi):
        tag, keys, xs = node
        assert len(keys) < N, "Overflowed node capacity"
        for i in range(len(keys)-1):
            assert keys[i] < keys[i+1], "Disordered or duplicate key"
        if tag in ('branch', 'root'):
            if tag == 'root': assert d == 0, "More than one root"
            kids = xs
            assert not kids or len(keys) == len(kids)-1, "keys and kids don't correspond"
            if tag == 'branch': math.ceil(N//2) <= len(kids)
            assert lo is () or lo[0] < keys[0]
            assert hi is () or keys[-1] < hi[0]
            for i, kid_i in enumerate(kids):
                checking(kid_i, d+1,
                         lo if i == 0 else (keys[i-1],),
                         hi if i == len(keys) else (keys[i],))
        elif tag == 'leaf':
            assert d == depth, "Leaves at different depths"
            values = xs
            assert len(keys) == len(values), "keys and values don't correspond"
            assert lo is () or lo[0] == keys[0]
            assert hi is () or keys[-1] < hi[0]
        else:
            assert False, "Bad tag"

    checking(bpt, 0, (), ())

def search(bpt, needle_key, default=None):
    "Return bpt's value for needle_key, or default if absent."
    tag, keys, xs = bpt
    if not xs: return default
    while tag != 'leaf':
        for i, key_i in enumerate(keys):
            if needle_key < key_i:
                break
        else:
            i = len(keys)
        tag, keys, xs = xs[i]
    for i, key_i in enumerate(keys):
        if needle_key == key_i:
            return xs[i]
    return default

def make_empty_bpt():
    result = 'root', [], []
    check_bpt(result)
    return result

def insert(bpt, new_key, value):
    result = really_insert(bpt, new_key, value)
    check_bpt(result)
    return result

def really_insert(bpt, new_key, value):
    """Mutate bpt to add (new_key,value) (replacing any current value for
    new_key), and return the new root node."""

    tag, keys, xs = bpt
    if not xs:
        # The tree is completely empty; start populating it.
        leaf = 'leaf', [new_key], [value]
        return 'root', [], [leaf]

    # Find the leaf node for new_key, and the path down to it.
    path = []
    while tag != 'leaf':
        for i, key_i in enumerate(keys):
            if new_key < key_i:
                break
        else:
            i = len(keys)
        path.append((tag, keys, xs, i))
        tag, keys, xs = xs[i]

    # Find the index for new_key in the leaf node.
    for i, key_i in enumerate(keys):
        if new_key == key_i:
            # new_key isn't actually new, so the structure goes unchanged.
            xs[i] = value
            return bpt
        elif new_key < key_i:
            break
    else:
        i = len(keys)

    # We'll have to insert it in the leaf at i. If there's room, just do it:
    keys.insert(i, new_key)
    xs.insert(i, value)
    if len(keys) < N:
        return bpt

    # Else split the now-overpacked leaf...
    mid = N//2
    tween = keys[mid]
    left  = 'leaf', keys[:mid], xs[:mid]
    right = 'leaf', keys[mid:], xs[mid:]

    # ...and propagate the split back up the path.
    while path:
        tag, keys, xs, i = path.pop()
        keys.insert(i, tween)
        xs[i:i+1] = [left, right]
        if len(keys) < N:
            return bpt
        #    (x0 k0 x1 k1 x2 k2 x3)       as ([k0,k1,k2] [x0,x1,x2,x3])
        # => ([x0 k0 x1]) k1 ([x2 k2 x3]) as ([k0] [x0,x1]) k1 ([k2] [x2,x3])
        #       (left)   tween  (right)         (left)     tween   (right)
        tween = keys[mid-1]
        left  = 'branch', keys[:mid-1], xs[:mid]
        right = 'branch', keys[mid:], xs[mid:]

    # If we got here, we need a new root.
    return 'root', [tween], [left, right]


# Smoke test

t = make_empty_bpt()
## t
#. ('root', [], [])
## t = insert(t, 'm', 5)
## t
#. ('root', [], [('leaf', ['m'], [5])])
## t = insert(t, 'm', 42)
## t
#. ('root', [], [('leaf', ['m'], [42])])
## t = insert(t, 'n', 1)
## t
#. ('root', [], [('leaf', ['m', 'n'], [42, 1])])
## search(t, 'm')
#. 42
## search(t, 'n')
#. 1
## t = insert(t, 'a', 8)
## t
#. ('root', [], [('leaf', ['a', 'm', 'n'], [8, 42, 1])])
## search(t, ''), search(t, 'a'), search(t, 'b'), search(t, 'm'), search(t, 'n'), search(t, 'z')
#. (None, 8, None, 42, 1, None)

## what_I_represent(t)
#. {'a': 8, 'm': 42, 'n': 1}

## t = insert(t, 'o', 10)
## t
#. ('root', ['n'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10])])
## t = insert(t, 'p', 11)
## t
#. ('root', ['n'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o', 'p'], [1, 10, 11])])
## t = insert(t, 'q', 12)
## t
#. ('root', ['n', 'p'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10]), ('leaf', ['p', 'q'], [11, 12])])
## t = insert(t, 'r', 13)
## t
#. ('root', ['n', 'p'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10]), ('leaf', ['p', 'q', 'r'], [11, 12, 13])])
## t = insert(t, 's', 14)
## t
#. ('root', ['n', 'p', 'r'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10]), ('leaf', ['p', 'q'], [11, 12]), ('leaf', ['r', 's'], [13, 14])])
## t = insert(t, 't', 15)
## t
#. ('root', ['n', 'p', 'r'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10]), ('leaf', ['p', 'q'], [11, 12]), ('leaf', ['r', 's', 't'], [13, 14, 15])])
## t = insert(t, 'u', 16)
## t
#. ('root', ['p'], [('branch', ['n'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10])]), ('branch', ['r', 't'], [('leaf', ['p', 'q'], [11, 12]), ('leaf', ['r', 's'], [13, 14]), ('leaf', ['t', 'u'], [15, 16])])])
## t = insert(t, 'v', 17)
## t
#. ('root', ['p'], [('branch', ['n'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10])]), ('branch', ['r', 't'], [('leaf', ['p', 'q'], [11, 12]), ('leaf', ['r', 's'], [13, 14]), ('leaf', ['t', 'u', 'v'], [15, 16, 17])])])

## sorted(what_I_represent(t).items())
#. [('a', 8), ('m', 42), ('n', 1), ('o', 10), ('p', 11), ('q', 12), ('r', 13), ('s', 14), ('t', 15), ('u', 16), ('v', 17)]

## for k in '-abcdefghijklmnopqrstuvw': print k, search(t, k)
#. - None
#. a 8
#. b None
#. c None
#. d None
#. e None
#. f None
#. g None
#. h None
#. i None
#. j None
#. k None
#. l None
#. m 42
#. n 1
#. o 10
#. p 11
#. q 12
#. r 13
#. s 14
#. t 15
#. u 16
#. v 17
#. w None
