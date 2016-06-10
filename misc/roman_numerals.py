"""
Convert from Roman numeral to int. Two versions.
"""

def int_from_roman1(string):
    def convert((i, c)):
        return -values[c] if string[i:i+2] in almost else values[c]
    return sum(map(convert, enumerate(string)))

values = {'M': 1000, 'D': 500, 'C': 100, 'L': 50, 'X': 10, 'V': 5, 'I': 1}
almost = 'CM CD XC XL IX IV'.split()

# After a more elegant answer in Java: http://stackoverflow.com/a/25411754/27024
def int_from_roman2(string):
    acc = prev = 0
    for c in reversed(string):
        v = values[c]
        if prev < v: acc += v
        else:        acc -= v
        prev = v
    return acc

## int_from_roman1('MCMLXXIX')
#. 1979
## int_from_roman2('MCMLXXIX')
#. 1959

"""
And the converse. Disappointing to use different tables.
"""

def roman_from_int(n):
    tens, ones = divmod(n, 10)
    return (times_X(roman_from_int(tens)) if tens else '') + digits[ones]

def times_X(numeral):
    return ''.join(places[c] for c in numeral)

digits = ' I II III IV V VI VII VIII IX'.split(' ')
places = dict(zip('IVXLC',
                  'XLCDM'))

## roman_from_int(1979)
#. 'MCMLXXIX'
