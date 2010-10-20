"""
Predicate dispatch.
"""

def make_generic_function_trivially():  # Trivial version
    pairs = []
    def store(predicates, handler):
        """Add a method to this generic function."""
        pairs.insert(0, (predicates, handler))
    def generic_function(*args):
        """Call the method matching these arguments."""
        for predicates, handler in pairs:
            for predicate, arg in zip(predicates, args):
                if not predicate(arg):
                    break
            else:
                return handler(args)
        raise 'No applicable method'
    return store, generic_function


def make_generic_function(arity):       # Fancier trie-based dispatch, with more error checks
    pt = PredicateTrie()
    def store(predicates, handler):
        assert len(predicates) == arity
        pt.insert(predicates, handler)
    def generic_function(*args):
        assert len(args) == arity
        handler = pt.get(args)
        if handler is not None:
            return handler(args)
        raise 'No applicable method'
    return store, generic_function

class PredicateTrie:

    def __init__(self):
        self.handler = None
        self.pairs = []
        
    def get(self, values):
        if 0 == len(values):
            return self.handler
        for predicate, pt in self.pairs:
            if predicate(values[0]):
                handler = pt.get(values[1:])
                if handler is not None:
                    return handler
        return None

    def insert(self, predicates, handler):
        if 0 == len(predicates):
            if self.handler is not None:
                print 'Warning: replacing a handler'
            self.handler = handler
        else:
            for predicate, pt in self.pairs:
                if predicate == predicates[0]:       # XXX implication tests might be cool
                    pt.insert(predicates[1:], handler)
                    return
            pt = PredicateTrie()
            self.pairs.append((predicates[0], pt))
            pt.insert(predicates[1:], handler)

# TODO:
#   Features:
#     treat types as predicates?
#     useful higher-order predicates (e.g. curried equality)
#     use a decorator to add a method?
#     order overrides by subsumption instead of by order of definitions?
#     other syntactic sugar?
#     would there be any point in something like a MOP?
#   Efficiency:
#     some kind of caching for faster lookup?
#     special-case common kinds of predicates?
#     special-case the smallest arities?
#     read the Kiczales paper on efficient dispatching
#     profile and bum the code
#   Examples and tests:
#     generic list functions (problem set 2)
#     examples from the predicate dispatch paper
