from doomer import curse, a_coinflip

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
    assert is_balanced(tree)
#. a_tree: (None, ((((((None, (None, (None, None))), None), None), None), None), None))
