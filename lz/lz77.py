"""
First cut at LZ77 from http://en.wikipedia.org/wiki/LZ77_and_LZ78
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
    input = iter(s)
    window = ''
    try:
        while True:
            chunk = ''
            while chunk in window: # TODO: be able to output n > k
                c = input.next()
                chunk += c
            i = window.rindex(chunk[:-1])
            yield len(chunk)-1, len(window) - i, c
            window += chunk
    except StopIteration:
        if chunk:
            i = window.rindex(chunk[:-1])
            yield len(chunk)-1, len(window) - i, c

def decode(triples):
    """Given an LZ77-code iterable, generate string chunks that,
    concatenated, form the original plaintext."""
    window = ''
    for length, offset, c in triples:
        chunk = window[-offset:(-offset+length or None)] if length else ''
        yield chunk + c
        window += chunk + c

def test_reversible(s):
    assert s == ''.join(decode(encode(s)))

def printit(iterable):
    for x in iterable: print x

## printit(decode(encode('AAAAAAAAAAAAAAAAAAAAAA')))
#. A
#. AA
#. AAAA
#. AAAAAAAA
#. AAAAAAA
#. 

## test_reversible('')
## test_reversible('x')
## test_reversible('xxxxxxxxxyyyyyyyyyyyyyyxxxxxxxxx')
## test_reversible('when in the course of human events to be or not to be')

def rle_test():
    for L in range(1000):
        test_reversible('x' * L)

def exhaustive_binary_test():
    for L in range(10):
        for input in range(2**L):
            binary = bin(input)[2:]
            test_reversible(binary)

## rle_test()
## exhaustive_binary_test()

## len(list(encode('a' * 1000)))
#. 10
