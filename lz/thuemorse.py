"""
http://en.wikipedia.org/wiki/Thue%E2%80%93Morse_sequence
I'm curious how well LZ compressors can parse this sequence.
"""

def thue_morse(power):
    s = '0'
    yield s
    for i in range(power):
        inv = s.replace('0', 'x').replace('1', '0').replace('x', '1')
        yield inv
        s += inv

## for p in range(7): print ' '.join(thue_morse(p))
#. 0
#. 0 1
#. 0 1 10
#. 0 1 10 1001
#. 0 1 10 1001 10010110
#. 0 1 10 1001 10010110 1001011001101001
#. 0 1 10 1001 10010110 1001011001101001 10010110011010010110100110010110
#. 

def try_compressing():
    from lz78 import encode
    #from lz77 import encode
    #from lzw import encode
    for power in range(12):
        tm = ''.join(thue_morse(power))
        print '%2d %5d %5d' % (power, len(list(encode(tm))), len(tm))

try_compressing()
