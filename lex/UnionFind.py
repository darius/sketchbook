# From http://code.google.com/p/python-automata/
"""Implements a Union-Find (or discrete-set) data-structure with the following performance profile:
-makeset O(1)
-find O(1)
-union O(n)
"""

class UnionFind():
    def __init__(self):
        self.sets = []
        self.lookup = {}
    def make_set(self, item):
        new_set = [item]
        self.sets.append(new_set)
        self.lookup[item] = new_set
    def find(self, item):
        return self.lookup[item]
    def union(self, set1, set2):
        """Merges set1 into set2"""
        assert(set1 in self.sets)
        assert(set2 in self.sets)
        for (item, value) in self.lookup.iteritems():
            if value == set1:
                self.lookup[item] = set2
        self.sets.remove(set1)
        set2.extend(set1)
    def as_lists(self):
        return self.sets
