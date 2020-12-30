"""
Varieties of semantics
"""

def DictSemantics(*dicts):
    result = {}
    for d in dicts: result.update(d)
    return result

base_semantics = DictSemantics(__builtins__)  # TODO Parson conveniences like `hug`

def ModuleSemantics(module):
    # TODO keep up with any updates to the module instead of just copying the dict
    return DictSemantics(module.__dict__)

class ASTSemantics(object):
    def __getitem__(self, name):
        return lambda *args: (name,) + args
    def get(self, name, default=None):
        return self[name]

ast_semantics = ASTSemantics()

class ComboSemantics(object): # TODO is there a dictlike class that already does this?
    def __init__(self, *semanticses):
        self.sems = list(semanticses)
        self.sems.reverse()
    def __getitem__(self, name):
        value = self.get(name)
        if value is None: raise KeyError(name)
        return value
    def get(self, name, default=None):
        for sem in self.sems:
            value = sem.get(name)
            if value is not None:
                return value
        return default
