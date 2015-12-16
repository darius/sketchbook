"""
Let's see if I can reconstruct B+ trees from this draft post by Ezekiel:
https://github.com/tehgeekmeister/dadabass/blob/b_plus_tree/notes/b_plus_tree.md
I've now departed from that outline in a couple respects to do with the root:
it can be a leaf, or as a branch it's not specially tagged as the root.

A B+ tree represents a map from keys to values. It's built of two node types,
each represented by a 3-tuple:

  'branch', keys, kids    (Called either 'root' or 'internal node' in the post.)
  'leaf', keys, values
"""

from math import ceil

def what_I_represent(bpt):
    "Return a dict that represents the same mapping as the given B+ tree does."
    result = {}
    def walk(node):
        tag, keys, xs = node
        if tag == 'branch':
            kids = xs
            for kid in kids:
                walk(kid)
        elif tag == 'leaf':
            values = xs
            result.update(zip(keys, values))
    walk(bpt)
    return result

capacity = 4 # Our node-size constant; pretty arbitrary. Here's a rather
      # small value to make testing easier. (We should test with
      # larger values as well, since capacity=4 happens to make the root
      # and branch kinds more similar than in general, as Ezekiel
      # pointed out.)
assert capacity % 2 == 0  # TODO come back and see what if this is false

def check_bpt(bpt):
    """
    Check the representation invariant for our B+ tree type. Return
    the tree if it's OK, else raise an error. Since there's a lot to
    this invariant, here it is in parts:

    For what_I_represent() to be meaningful:
    * We have a tree of the two node types, as explained above.
    * For leaves, len(keys) == len(values)
    * The keys from all of the leaves together are all distinct.

    So that fetch() can find a key, and store() can leave it where
    fetch() will find it:
    * For both kinds of nodes, keys are sorted ascending.
    * Branches' keys partition their descendants by key:
      for i in range(len(keys)):
          all of kids[i] and descendants' keys < keys[i] <= all of kids[i+1] and descendants' keys
    * For branches, len(keys)+1 == len(kids)
      This is needed for the above partitioning invariant to be meaningful.
      (It also implies at least one kid, so you eventually reach a leaf.)

    To bound the size of nodes, for efficiency:
    * For both node kinds, len(keys) < capacity

    To ensure a balanced tree, for efficiency:
    * The leaves are all at the same depth.
    * If the root is a branch, it has at least two kids.
    * For branches below the root, ceil(capacity//2) <= len(kids)
    * For leaves below the root,   ceil(capacity//2) <= len(values)
      (This one does not affect asymptotics, but without it the
      constant factor would suck.)
    """
    tag, _, xs = bpt
    assert tag == 'leaf' or xs

    # First compute the depth.
    depth = 0
    while tag == 'branch':
        tag, _, xs = xs[0]
        depth += 1

    def checking(node, d, lo, hi):
        """Check node (which is at depth d) and its descendants. Besides the
        noncontextual invariants, check that keys are in range between
        lo[0] and hi[0] (except for lo or hi being (), meaning
        unbounded). The lo bound is inclusive, the hi exclusive."""
        tag, keys, xs = node
        assert len(keys) < capacity, "Overflowed node capacity"
        for i in range(len(keys)-1):
            assert keys[i] < keys[i+1], "Disordered or duplicate key"
        assert lo is () or lo[0] <= keys[0]
        assert hi is () or keys[-1] < hi[0]
        if tag == 'branch':
            kids = xs
            if d == 0:
                assert 2 <= len(kids), "Underpopulated root"
            else:
                assert ceil(capacity//2) <= len(kids), "Underpopulated branch"
            assert len(keys) == len(kids)-1, "keys and kids don't correspond"
            for i, kid_i in enumerate(kids):
                checking(kid_i, d+1,
                         lo if i == 0 else (keys[i-1],),
                         hi if i == len(keys) else (keys[i],))
        elif tag == 'leaf':
            assert d == depth, "Leaves at different depths"
            values = xs
            assert len(keys) == len(values), "keys and values don't correspond"
            if 0 < d:
                assert ceil(capacity//2) <= len(values), "Underpopulated leaf"
        else:
            assert False, "Bad tag"

    checking(bpt, 0, (), ())
    return bpt

def fetch(bpt, needle_key, default=None):
    "Return bpt's value for needle_key, or default if absent."
    tag, keys, xs = bpt
    while tag == 'branch':
        for i, key_i in enumerate(keys):
            if needle_key < key_i:
                break
        else:
            i = len(keys)
        tag, keys, xs = xs[i]
    for i, key_i in enumerate(keys):
        if needle_key == key_i:
            return xs[i]
        elif needle_key < key_i:
            break # (just to finish quicker; not needed for correctness)
    return default

def make_empty_bpt():
    return check_bpt(('leaf', [], []))

def store(bpt, new_key, value):
    return check_bpt(really_store(bpt, new_key, value))

def really_store(bpt, new_key, value):
    """Mutate bpt to add (new_key,value) (replacing any current value for
    new_key), and return the new root node."""

    tag, keys, xs = bpt

    # Find the leaf node for new_key, and the path down to it.
    path = []
    while tag == 'branch':
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
    if len(keys) < capacity:
        return bpt

    # Otherwise split the now-overpacked leaf...
    mid = capacity//2
    tween = keys[mid]
    left  = 'leaf', keys[:mid], xs[:mid]
    right = 'leaf', keys[mid:], xs[mid:]

    # ...and propagate the split back up the path.
    while path:
        tag, keys, kids, i = path.pop()
        keys.insert(i, tween)
        kids[i:i+1] = [left, right]
        if len(keys) < capacity:
            return bpt
        # Example (capacity=4, mid=2):
        #   [key0,key1,key2,key3]         [key0]    key1   [key2,key3]
        # [kid0,kid1,kid2,kid3,kid4] => [kid0,kid1]      [kid2,kid3,kid4]
        #                                 (left)   (tween)  (right)
        tween = keys[mid-1]
        left  = 'branch', keys[:mid-1], kids[:mid]
        right = 'branch', keys[mid:], kids[mid:]

    # If we got here, we need a new root.
    return 'branch', [tween], [left, right]


# Testing

import random

def random_tests(ntrials=10000):
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEF'
    for trial in range(ntrials):
        exercise_bpt((random.choice(alphabet),
                      'fetch' if random.random() < 0.3 else value)
                     for value in range(50))

def exercise_bpt(pairs):
    """Check that a sequence of stores and fetches produces the same
    results for a dict and a bpt."""
    default = ['missing']
    d = {}
    t = make_empty_bpt()
    for key, value in pairs:
        if value == 'fetch':
            assert d.get(key, default) == fetch(t, key, default), "Wrong fetch result"
        else:
            d[key] = value
            t = store(t, key, value)
            wir = what_I_represent(t)
            assert d == wir, ("different", d, wir, t)

### random_tests()


# Smoke test

## t = make_empty_bpt()
## t
#. ('leaf', [], [])
## t = store(t, 'm', 5)
## t
#. ('leaf', ['m'], [5])
## t = store(t, 'm', 42)
## t
#. ('leaf', ['m'], [42])
## t = store(t, 'n', 1)
## t
#. ('leaf', ['m', 'n'], [42, 1])
## fetch(t, 'm')
#. 42
## fetch(t, 'n')
#. 1
## t = store(t, 'a', 8)
## t
#. ('leaf', ['a', 'm', 'n'], [8, 42, 1])
## fetch(t, ''), fetch(t, 'a'), fetch(t, 'b'), fetch(t, 'm'), fetch(t, 'n'), fetch(t, 'z')
#. (None, 8, None, 42, 1, None)

## what_I_represent(t)
#. {'a': 8, 'm': 42, 'n': 1}

## t = store(t, 'o', 10)
## t
#. ('branch', ['n'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10])])
## t = store(t, 'p', 11)
## t
#. ('branch', ['n'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o', 'p'], [1, 10, 11])])
## t = store(t, 'q', 12)
## t
#. ('branch', ['n', 'p'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10]), ('leaf', ['p', 'q'], [11, 12])])
## t = store(t, 'r', 13)
## t
#. ('branch', ['n', 'p'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10]), ('leaf', ['p', 'q', 'r'], [11, 12, 13])])
## t = store(t, 's', 14)
## t
#. ('branch', ['n', 'p', 'r'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10]), ('leaf', ['p', 'q'], [11, 12]), ('leaf', ['r', 's'], [13, 14])])
## t = store(t, 't', 15)
## t
#. ('branch', ['n', 'p', 'r'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10]), ('leaf', ['p', 'q'], [11, 12]), ('leaf', ['r', 's', 't'], [13, 14, 15])])
## t = store(t, 'u', 16)
## t
#. ('branch', ['p'], [('branch', ['n'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10])]), ('branch', ['r', 't'], [('leaf', ['p', 'q'], [11, 12]), ('leaf', ['r', 's'], [13, 14]), ('leaf', ['t', 'u'], [15, 16])])])
## t = store(t, 'v', 17)
## t
#. ('branch', ['p'], [('branch', ['n'], [('leaf', ['a', 'm'], [8, 42]), ('leaf', ['n', 'o'], [1, 10])]), ('branch', ['r', 't'], [('leaf', ['p', 'q'], [11, 12]), ('leaf', ['r', 's'], [13, 14]), ('leaf', ['t', 'u', 'v'], [15, 16, 17])])])

## sorted(what_I_represent(t).items())
#. [('a', 8), ('m', 42), ('n', 1), ('o', 10), ('p', 11), ('q', 12), ('r', 13), ('s', 14), ('t', 15), ('u', 16), ('v', 17)]

## for k in '-abcdefghijklmnopqrstuvw': print k, fetch(t, k)
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
