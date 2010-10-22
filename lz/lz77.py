"""
LZ77 from http://en.wikipedia.org/wiki/LZ77_and_LZ78
with an unlimited 'window'.
"""

## printit(encode('much wood would a woodchuck chuck if a woodchuck would'))
#. (0, 0, 'm')
#. (0, 0, 'u')
#. (0, 0, 'c')
#. (0, 0, 'h')
#. (0, 0, ' ')
#. (0, 0, 'w')
#. (0, 0, 'o')
#. (1, 1, 'd')
#. (3, 5, 'u')
#. (0, 0, 'l')
#. (2, 6, 'a')
#. (5, 13, 'c')
#. (1, 20, 'u')
#. (1, 3, 'k')
#. (1, 10, 'c')
#. (5, 6, 'i')
#. (0, 0, 'f')
#. (13, 21, 'w')
#. (3, 39, 'd')
#. 

def encode(s):
    """Generate LZ77 triples encoding s. The triple (n, k, c) means
    that each of the next n characters is equal to the character k
    places behind it; then the next character after them is c."""
    buffer = ''                 # The input so far
    p = 0                       # Position in buffer of the current chunk
    def triple():
        n = len(buffer) - 1 - p
        k = p - buffer.rindex(buffer[p:-1], 0, -2) if n else 0
        return n, k, buffer[-1]
    for c in s:
        buffer += c
        if buffer[p:] not in buffer[:-1]:
            yield triple()
            p = len(buffer)
    if p < len(buffer):
        yield triple()

def decode(triples):
    """Given an LZ77-code iterable, generate string chunks that,
    concatenated, form the original plaintext."""
    buffer = ''
    for n, k, c in triples:
        for i in range(n):
            buffer += buffer[-k]
        buffer += c
        yield buffer[-n-1:]

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

## list(encode('a' * 1000))
#. [(0, 0, 'a'), (998, 1, 'a')]
