"""
longest_subpalindrome problem from Udacity CS212.
Genesis: https://forums.udacity.com/questions/100051766/using-a-heap-to-avoid-trying-starting-positions-that-cant-possibly-give-the-best-answer#cs212
"""

def find_longest_palindrome(s):
    "Return (i,j) such that s[i:j] is a longest palindrome in s."
    i, j = 0, 0
    for max_width in range(len(s), 0, -1):
        if max_width <= j - i:
            break
        # Check the candidate centers that on growing to max_width
        # would reach either the left or the right edge of s.
        for m in set([max_width, 2*len(s) - max_width]):
            i1, j1 = grow(s, m // 2, (m + 1) // 2)
            if j - i < j1 - i1:
                i, j = i1, j1
    return i, j

def grow(s, i, j):
    "Return the slice-indices of the longest palindromic extension of palindrome s[i:j]."
    while 0 < i and j < len(s) and s[i-1].lower() == s[j].lower():
        i -= 1; j += 1
    return i, j

## find_longest_palindrome('')
#. (0, 0)
## find_longest_palindrome('x')
#. (0, 1)
## find_longest_palindrome('xy')
#. (0, 1)
## find_longest_palindrome('xx')
#. (0, 2)
## find_longest_palindrome('xyx')
#. (0, 3)
## find_longest_palindrome('xyy')
#. (1, 3)
## find_longest_palindrome('abracadabra')
#. (3, 6)
## find_longest_palindrome('abracarbra')
#. (1, 8)

def test_suite(n=10):
    for L in range(n+1):
        for i in range(2**L):
            s = bin(i)[2:]
            s = '0' * (n - len(s)) + s
            test_finder(find_longest_palindrome, s)

def test_finder(finder, string):
    i, j = finder(string)
    assert 0 <= i <= j <= len(string)
    assert string[i:j] == string[i:j][::-1]  # assuming string doesn't mix cases
    for lo in range(len(string)+1):
        for hi in range(lo+j-i+1, len(string)+1):
            assert string[lo:hi] != string[lo:hi][::-1]

## test_suite()
