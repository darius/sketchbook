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
    new, old = {}, new
