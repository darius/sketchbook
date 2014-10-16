"""
Addressing a peeve: repetitive __init__ definitions.
namedtuple is one solution, but with baggage that sometimes
adds problems. So here's a more minimal one. It's not the
most minimal: this does leave room for custom __init__ 
actions. Most minimal would work like

class Chain:
    __init__ = initter_v0('left right')
    def get_length(self):
        return self.left.get_length() + self.right.get_length()
"""

def initter(field_names):
    names = field_names.split()
    def decorator(fn):
        def __init__(self, *args):
            assert len(args) == len(names), "Wrong # of arguments"
            self.__dict__.update(zip(names, args))
            fn(self)
        return __init__
    return decorator


# Example use:

class Chain:
    @initter('left right')
    def __init__(self):
        self.length = self.left.length + self.right.length
class Unit:
    length = 1
## c = Chain(Unit(), Unit())
## c.length
#. 2
## c.left.length
#. 1
