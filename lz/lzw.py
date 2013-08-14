"""
An implementation of
http://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Welch
(without any entropy coder or codebook size limit)
"""

## message = 'TOBEORNOTTOBEORTOBEORNOT'
## encoded = list(encode(message))
## output = ''.join(decode(encoded))
## message == output
#. True
## list(show_lzw(message))
#. ['T', 'O', 'B', 'E', 'O', 'R', 'N', 'O', 'T', 256, 258, 260, 265, 259, 261, 263]
## list(chunked_decode(iter(encoded)))
#. ['T', 'O', 'B', 'E', 'O', 'R', 'N', 'O', 'T', 'TO', 'BE', 'OR', 'TOB', 'EO', 'RN', 'OT']

default_codebook = map(chr, range(256))

def show_lzw(s):
    return (chr(code) if code <= 255 else code for code in encode(s))

def encode(s, codebook=default_codebook):
    "Generate the LZW codes for string or iterable s."
    # Pre: each character in s has an entry in codebook.
    codes = dict((chunk, i) for i, chunk in enumerate(codebook))
    chunk = ''
    for c in s:
        chunk += c
        if chunk not in codes:
            yield codes[chunk[:-1]]
            codes[chunk] = len(codes)
            chunk = chunk[-1]
    if chunk:
        yield codes[chunk]

def decode(codes, codebook=default_codebook):
    """Given an LZW code sequence as an iterable, generate the
    plaintext character sequence it came from."""
    # Pre: codebook is the same as the encoder's.
    for chunk in chunked_decode(iter(codes), codebook):
        for c in chunk:
            yield c

def chunked_decode(codes_iter, codebook=default_codebook):
    chunks = list(codebook)
    chunk = chunks[codes_iter.next()]
    while True:
        yield chunk
        chunks.append(chunk)        # Pending: last char of chunk
        code = codes_iter.next()
        chunks[-1] += chunks[code][0]
        chunk = chunks[code]

## m = 'XXXXXXXXXXXX'
## list(show_lzw(m))
#. ['X', 256, 257, 258, 256]
## x = list(encode(m))
## list(chunked_decode(iter(x)))
#. ['X', 'XX', 'XXX', 'XXXX', 'XX']
## m == ''.join(chunked_decode(iter(x)))
#. True

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
#. (45, 298)
