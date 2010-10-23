"""
An implementation of LZ78
(without any entropy coder or codebook size limit)
"""

## printit(encode('much wood would a woodchuck chuck if a woodchuck would'))
#. (0, 'm')
#. (0, 'u')
#. (0, 'c')
#. (0, 'h')
#. (0, ' ')
#. (0, 'w')
#. (0, 'o')
#. (7, 'd')
#. (5, 'w')
#. (7, 'u')
#. (0, 'l')
#. (0, 'd')
#. (5, 'a')
#. (9, 'o')
#. (8, 'c')
#. (4, 'u')
#. (3, 'k')
#. (5, 'c')
#. (16, 'c')
#. (0, 'k')
#. (5, 'i')
#. (0, 'f')
#. (13, ' ')
#. (6, 'o')
#. (15, 'h')
#. (2, 'c')
#. (20, ' ')
#. (24, 'u')
#. (11, 'd')
#. 
## '.'.join(decode(encode('much wood would a woodchuck chuck if a woodchuck would')))
#. 'm.u.c.h. .w.o.od. w.ou.l.d. a. wo.odc.hu.ck. c.huc.k. i.f. a .wo.odch.uc.k .wou.ld'

def encode(s):
    "Generate the LZ78 codes for string or iterable s."
    codes = {'': 0}
    chunk = ''
    for c in s:
        chunk += c
        if chunk not in codes:
            yield codes[chunk[:-1]], c
            codes[chunk] = len(codes)
            chunk = ''
    if chunk:
        yield codes[chunk[:-1]], chunk[-1]

def decode(pairs):
    """Given an LZ78-code iterable, generate string chunks that,
    concatenated, form the original plaintext."""
    buffer = ''
    chunks = ['']
    for code, c in pairs:
        chunk = chunks[code] + c
        yield chunk
        chunks.append(chunk)

def printit(iterable):
    for x in iterable: print x

## test_reversible('xxxxxxxxxyyyyyyyyyyyyyyxxxxxxxxx')
## test_reversible('when in the course of human events to be or not to be')

def test_reversible(s):
    assert s == ''.join(decode(encode(s))), s

def rle_test():
    for L in range(100):
        test_reversible('x' * L)

def exhaustive_binary_test():
    for L in range(10):
        for input in range(2**L):
            binary = bin(input)[2:]
            test_reversible(binary)

## rle_test()
## exhaustive_binary_test()

## mil = list(encode('a' * 1000))
## len(mil), max(mil)
#. (45, (43, 'a'))
