"""
An exceedingly unpythonic trick to get multiline anonymous lambdas.
Sort of. 'Inspired' by, but simpler than,
http://news.ycombinator.com/item?id=777564
"""

def flip(f, *args, **kwargs):
    "'flip' from Haskell's standard library, generalized to multiple args."
    return lambda y: f(y, *args, **kwargs)

# For example. We want code like 
#   result = map(lambda x: BLAH, [1, 2, 3])
# But BLAH isn't just an expression. So:

@flip(map, [1, 2, 3])
def result(x):
    print 'twice %d is %d' % (x, 2*x)
    return 2 * x
## result
#. [2, 4, 6]
#. twice 1 is 2
#. twice 2 is 4
#. twice 3 is 6
#. 
