"""
Memoization decorator.
"""

def memoize(f):
    memos = {}
    def memoized(*args):
        if args not in memos: memos[args] = f(*args)
        return memos[args]
    return memoized
