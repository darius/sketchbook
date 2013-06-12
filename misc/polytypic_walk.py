"""
Polytypic traversals -- postorder and preorder.
"""

def visit(node, visitor):
    return node.accept(lambda x: x, visitor)

def walk_postorder(node, visitor):
    def walk(node): return node.accept(walk, visitor)
    return walk(node)

def walk_preorder(node, visitor):
    # The logical symmetry with walk_postorder here is obscured 
    # because fmap and visit are generic functions, while accept
    # is a method.
    def walk(node): return fmap(visit(node, visitor), walk)
    return walk(node)

# The name 'fmap' is the usual one in Haskell.
def fmap(node, f):
    return node.accept(f, identity_visitor)


# An example type and traversal

class Literal:
    def __init__(self, value):
        self.value = value
    def accept(self, f, visitor):
        return visitor.visit_literal(self, self.value)

class BinaryApp:
    def __init__(self, operator, left, right):
        self.operator = operator
        self.left = left
        self.right = right
    def accept(self, f, visitor):
        return visitor.visit_binary_app(self, 
                                        self.operator,
                                        f(self.left),
                                        f(self.right))

def evaluate(node):
    return walk_postorder(node, EvalVisitor())

class EvalVisitor:
    def visit_literal(self, node, value):
        return value
    def visit_binary_app(self, node, operator, left, right):
        assert operator == '+'
        return left + right

## evaluate(BinaryApp('+', BinaryApp('+', Literal(4), Literal(2)), Literal(3)))
#. 9
