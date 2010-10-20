def lit(s):
    def insn(rest):
        if not rest:
            return s
        elif rest[0] == concat:
            return s + format(rest)
        else:
            return s + ' ' + format(rest)
    return insn

def concat(rest):
    return format(rest)

def a_an(rest):
    s = format(rest)
    if is_vowel(first_letter(s)):
        return "an " + s
    else:
        return "a " + s

def first_letter(s):
    return s[0]                 # XXX

def is_vowel(c):
    return c in 'aeiouy'

def capitalize(rest):
    return format(rest).capitalize()

comma = (concat, lit(","))

def format(insns):
    if not insns:
        return ''
    return insns[0](insns[1:])

## format([capitalize, a_an, lit('hell'), concat, lit(','), lit('world')])
#. 'A hell, world'

## format([a_an, lit('ohell'), concat, lit(','), lit('world')])
#. 'an ohell, world'
