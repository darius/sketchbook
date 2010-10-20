def encode(s):
    input = iter(s)
    window = ''
    try:
        while True:
            chunk = ''
            while chunk in window:  # TODO extend window with chunk[:-1]
                c = input.next()
                chunk += c
            i = window.rindex(chunk[:-1])
            yield len(window) - i, len(chunk)-1, c
            window += chunk
    except StopIteration:
        if chunk:
            i = window.rindex(chunk[:-1])
            yield len(window) - i, len(chunk)-1, c

## for x in encode('hello world'): print x
#. (0, 0, 'h')
#. (0, 0, 'e')
#. (0, 0, 'l')
#. (1, 1, 'o')
#. (0, 0, ' ')
#. (0, 0, 'w')
#. (3, 1, 'r')
#. (6, 1, 'd')
#. 

## for x in encode('AAAAAAAAAAAAAAAAAA'): print x
#. (0, 0, 'A')
#. (1, 1, 'A')
#. (3, 3, 'A')
#. (7, 7, 'A')
#. (2, 2, 'A')
#. 
