def concat(insns):
    return insns[0](insns[1:]) if insns else ''

def capitalize(insns):
    return concat(insns).capitalize()

def lit(s):
    def insn(insns):
        rest = concat(insns)
        sep = '' if insns[0:1] == [concat] else space(rest)
        return s + sep + rest
    return insn

def a_an(insns):
    s = concat(insns)
    return ("an" if s[0:1] in 'aeiouy' else "a") + space(s) + s

def space(s): return ' ' if s else ''

## concat([capitalize, a_an, lit('hell'), concat, lit(','), lit('world')])
#. 'A hell, world'

## concat([a_an, lit('ohell'), concat, lit(','), lit('world')])
#. 'an ohell, world'
