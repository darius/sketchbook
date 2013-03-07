"""
http://blog.lukego.com/blog/2013/02/04/cute-code/
Let's see what the Python looks like.
untested
"""

new, old = {}, {}

def get(k):
    return new[k] if k in new else put(k, old.get(k))

def put(k, v):
    if v is not None: new[k] = v
    return v

def age():
    global new, old
    new, old = {}, new


# Simpler

capacity = 1000

table = {}

get = table.get

def put(k, v):
    if len(table) == capacity and k not in table:
        table.clear()
    table[k] = v


# Fancier, but good only for small capacities:

class MRUDict(dict):
    "A dict with fixed capacity, keeping only the most recently used keys."
    def __init__(self, capacity=5):
        dict.__init__(self)
        self.capacity = capacity
        self._keys = []         # Most-recently-touched first.
    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._keys.remove(key)
    def __getitem__(self, key):
        self.touch(key)
        return dict.__getitem__(self, key)
    def __setitem__(self, key, value):
        self.touch(key)
        return dict.__setitem__(self, key, value)
    def get(self, key, default=None):
        if key in self: self.touch(key)
        return dict.get(self, key, default)
    def touch(self, key):
        if key in self: self._keys.remove(key)
        self._keys.insert(0, key)
        if self.capacity < len(self._keys):
            dict.__delitem__(self, self._keys.pop())

## d = MRUDict(2)
## d[1] = 'x'
## d[2] = 'y'
## d
#. {1: 'x', 2: 'y'}
## d[3] = 'z'
## d
#. {2: 'y', 3: 'z'}
## d[2]
#. 'y'
## d
#. {2: 'y', 3: 'z'}
## d[1] = 'x'
## d
#. {1: 'x', 2: 'y'}


# Fancier still

P, S, K, V = range(4) # Fields in a cache entry: predecessor, successor, key, value

class MRUCache(object):
    def __init__(self, capacity=5):
        self.capacity = capacity
        self.map = {}
        self.head = [None, None, None, None]
        self.head[P] = self.head[S] = self.head  # For a circular list
        self.self_check()
    def _entries(self):
        entry = self.head[S]
        while entry is not self.head:
            yield entry
            entry = entry[S]
    def __repr__(self):
        return repr([(entry[K], entry[V]) for entry in self._entries()])
    def self_check(self):
        assert len(self.map) <= self.capacity
        assert len(self.map) == sum(1 for _ in self._entries())
        for key in self.map:
            assert any(entry[K] == key for entry in self._entries())
        for entry in self._entries():
            assert entry[P] is not entry
            assert entry[S] is not entry
            assert entry[P][S] is entry
            assert entry[S][P] is entry
            assert entry[K] in self.map
    def __contains__(self, key):
        return key in self.map
    def get(self, key, default=None):
        return self.touch(key, self.map[key][V]) if key in self.map else default
    def __setitem__(self, key, value):
        self.touch(key, value)
    def touch(self, key, value):
        self.self_check()
        if key in self.map:
            self._remove(self.map[key])
        pred, succ = self.head, self.head[S]
        self.map[key] = pred[S] = succ[P] = [pred, succ, key, value]
        if self.capacity < len(self.map):
            self._remove(self.head[P])
        self.self_check()
        return value
    def _remove(self, entry):
        del self.map[entry[K]]
        entry[P][S], entry[S][P] = entry[S], entry[P]
    def touch(self, key, value):
        # Like previous touch() but with fewer map lookups and trickier code.
        self.self_check()
        try:
            entry = self.map[key]
        except KeyError:
            (pred, succ) = (self.head, self.head[S])
            pred[S] = succ[P] = self.map[key] = [pred, succ, key, value]
        else:
            (entry[S][P], entry[P][S]) = (entry[P], entry[S])
            (entry[P], entry[S]) = (pred, succ) = (self.head, self.head[S])
            pred[S] = succ[P] = entry
        if self.capacity < len(self.map):
            oldest = self.head[P]
            (oldest[S][P], oldest[P][S]) = (oldest[P], oldest[S])
            del self.map[oldest[K]]
        self.self_check()
        return value

## d = MRUCache(2)
## d[1] = 'x'
## d[2] = 'y'
## d
#. [(2, 'y'), (1, 'x')]
## d[3] = 'z'
## d
#. [(3, 'z'), (2, 'y')]
## d.get(2)
#. 'y'
## d
#. [(2, 'y'), (3, 'z')]
## d[1] = 'x'
## d
#. [(1, 'x'), (2, 'y')]
