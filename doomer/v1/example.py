from doomer import curse, a_coinflip, a_small_nat

# Example
# datatype tree = None | (tree, tree)

def a_tree(doom):
    if doom.draw(a_coinflip(60)):
        return None
    else:
        return (doom.draw(a_tree), doom.draw(a_tree))

def is_balanced(tree):
    # TODO one-pass algorithm
    # Checking correctness of the one-pass version would also be a good property to test
    if tree is None: return True
    if not all(map(is_balanced, tree)): return False
    return abs(height(tree[0]) - height(tree[1])) <= 1

def height(tree):
    if tree is None: return 0
    return 1 + max(height(tree[0]), height(tree[1]))

@curse(seed=239)
def tree_should_balance(doom):
    tree = doom.draw(a_tree)
    # print 'trying', tree
    assert is_balanced(tree)
#    raise doom.deem(is_balanced(tree))
#    raise doom.claim(is_balanced(tree))
#    raise doom.surely(is_balanced(tree))
#    raise doom.daresay(is_balanced(tree))
#    raise doom.venture(is_balanced(tree))

def a_list_of(chooser):
    def a_list(doom):
        result = []
        while doom.draw(a_coinflip(80)):
            result.append(doom.draw(chooser))
        return result
    return a_list

def a_nonempty_list_of(chooser):
    def a_list(doom):
        result = []
        while True:
            result.append(doom.draw(chooser))
            if not doom.draw(a_coinflip(80)):
                break
        return result
    return a_list

def my_max(ns):
    return ns[0]

@curse(seed=239428937)
def max_should_be_last_sorted(doom):
    ns = doom.draw(a_nonempty_list_of(a_small_nat))
    assert my_max(ns) == sorted(ns)[-1]

@curse(seed=245398)
def append_should_be_monotonic(doom):
    ns = doom.draw(a_nonempty_list_of(a_small_nat))
    m = doom.draw(a_small_nat)
    maxn = my_max(ns)
    mns = [m] + ns
    maxmn = my_max(mns)
    assert maxmn == max(m, maxn)
#. 
#. Exercising tree_should_balance
#. Found a doom
#. shrink loop iteration (84, 48, 61, 99, 97, 76, 76, 75, 48, 99, 9, 96, 56, 43, 21, 23, 32, 7, 59)
#. shrink loop iteration (84, 48, 61, 99, 97, 76, 76, 75, 48, 99, 9, 43, 21, 23, 32, 7, 59)
#. shrink loop iteration (84, 48, 61, 99, 97, 76, 76, 75, 48, 43, 21, 23, 32, 7, 59)
#. shrink loop iteration (84, 48, 61, 99, 97, 76, 76, 43, 21, 23, 32, 7, 59)
#. shrink loop iteration (84, 48, 61, 99, 97, 76, 21, 23, 32, 7, 59)
#. shrink loop iteration (84, 48, 61, 99, 97, 23, 32, 7, 59)
#. shrink loop iteration (84, 48, 61, 99, 32, 7, 59)
#. a_tree: (None, ((None, None), None))
#. 
#. Exercising max_should_be_last_sorted
#. Found a doom
#. shrink loop iteration (3, 25, 9, 77, 0, 15, 10, 56, 8, 91)
#. shrink loop iteration (3, 25, 9, 77, 0, 15, 8, 91)
#. shrink loop iteration (3, 25, 9, 77, 0, 91)
#. shrink loop iteration (3, 25, 9, 91)
#. a_list: [3, 9]
#. 
#. Exercising append_should_be_monotonic
#. Found a doom
#. shrink loop iteration (8, 62, 3, 25, 10, 77, 5, 30, 3, 55, 7, 66, 10, 89, 6)
#. a_list: [8, 3, 10, 5, 3, 7, 10]
#. a_small_nat: 6
