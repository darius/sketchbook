"""
Primitive procedures for metatoo; they all operate on a stack,
like Forth. I believe we could get by without any of them, but it's
probably less pleasant to use that way. (Not that I've used metatoo
for anything but compiling itself, so far.)
"""

def nl(vals):    return vals + ('\n',)
def swap(vals):  return vals[:-2] + (vals[-1], vals[-2])
def quote(vals): return vals[:-1] + (repr(vals[-1]),)
def cat(vals):   return vals[:-2] + (vals[-2]+vals[-1],)
