"""
Deriving an efficient renderer from a straightforward one,
with some flailing along the way.
"""

# Rendering
# insn: [insn] -> (string, string)

def render_top(insns):
    return render(insns)[1]

def render(insns):
    return insns[0](insns[1:]) if insns else ('', '')

def abut_insn(insns):
    _, rest = render(insns)
    return '', rest

def capitalize_insn(insns):
    space, rest = render(insns)
    return space, rest.capitalize()

def lit_insn(s):
    def insn(insns):
        space, rest = render(insns)
        return ' ', s + space + rest
    return insn

def a_an_insn(insns):
    space, rest = render(insns)
    return ' ', ("an" if rest[0:1] in 'aeiouy' else "a") + space + rest


# Rendering
# insn: string, [insn] -> string

def render(space, insns):
    return insns[0](space, insns[1:]) if insns else ''

def abut_insn(space, insns):
    return render('', insns)

def capitalize_insn(space, insns):
    rest = render(space, insns)
    return re.sub(r'\w+', lambda m: m.group(0).capitalize(), rest, 1)

def lit_insn(s):
    return lambda space, insns: space + s + render(' ', insns)

def a_an_insn(space, insns):
    rest = render(' ', insns)
    return space + ("an" if rest.lstrip().startswith(vowels) else "a") + rest

vowels = tuple('aeiouyAEIOUY')


# Rendering
# insn: string, bool, [insn] -> string

def render_top(insns):
    return render('', False, insns)

def render(space, cap, insns):
    return insns[0](space, cap, insns[1:]) if insns else ''

def abut_insn(space, cap, insns):
    return render('', cap, insns)

def capitalize_insn(space, cap, insns):
    return render(space, True, insns)

def lit_insn(s):
    def insn(space, cap, insns):
        rest = render(' ', False, insns)
        return space + (s.capitalize() if cap else s) + rest
    return insn

def a_an_insn(space, cap, insns):
    rest = render(' ', False, insns)
    s = ("an" if rest[0:1].lower() in 'aeiouy' else "a")
    return space + (s.capitalize() if cap else s) + rest


# Rendering
# insn: string, [insn] -> string

def render_top(insns):
    return render('', insns)

def render(space, insns):
    return insns[0](space, insns[1:]) if insns else ''

def abut_insn(space, insns):
    return render('', insns)

def capitalize_insn(space, insns):
    return render(space, insns).capitalize()

def lit_insn(s):
    return lambda space, insns: space + s + render(' ', insns)

def a_an_insn(space, insns):
    rest = render(' ', insns)
    return space + ("an" if rest[0:1].lower() in 'aeiouy' else "a") + rest


# Rendering
# insn: (string->string), string, (string->string), [insn] -> string

def render(aan, space, cap, insns):
    return insns[0](aan, space, cap, insns[1:]) if insns else ''

def lit_insn(s):
    return lambda aan, space, cap, insns: aan(s) + space + cap(s) + render(nil, ' ', no_op, insns)

def abut_insn(aan, space, cap, insns):
    return render(aan, '', cap, insns)

def capitalize_insn(aan, space, cap, insns):
    return render(aan, space, string.capitalize, insns)

def a_an_insn(aan, space, cap, insns):
    def new_aan(s):
        return cap('an' if s.startswith(vowels) else 'a')
    return aan('a') + space + render(new_aan, ' ', no_op, insns)

vowels = tuple('aeiouAEIOU')

no_op = lambda s: s
nil = lambda s: ''


# Rendering
# insn: (string->string), string, (string->string), [insn] -> string

def render(insns):
    aan, space, cap = nil, '', no_op
    buf = []
    for insn in insns:
        s, aan, space, cap = insn(aan, space, cap)
        buf.append(s)
    return ''.join(buf)

def lit_insn(s):
    return lambda aan, space, cap: (aan(s) + space + cap(s), nil, ' ', no_op)

def abut_insn(aan, space, cap):
    return '', aan, '', cap

def capitalize_insn(aan, space, cap):
    return '', aan, space, string.capitalize

def a_an_insn(aan, space, cap):
    def new_aan(s):
        return cap('an' if s.startswith(vowels) else 'a')
    return aan('a') + space, new_aan, ' ', no_op

vowels = tuple('aeiouAEIOU')

no_op = lambda s: s
nil = lambda s: ''


# Rendering
# (Presumably) efficient version

def render(insns):
    aan, space, cap = '', '', no_op
    buf = []
    for insn in insns:
        s, aan, space, cap = insn(aan, space, cap)
        buf.append(s)
    return ''.join(buf)

def lit_insn(s):
    return lambda aan, space, cap: (
        apply_aan(aan, s) + space + cap(s), '', ' ', no_op)

def abut_insn(aan, space, cap):
    return '', aan, '', cap

def capitalize_insn(aan, space, cap):
    return '', aan, space, string.capitalize

def a_an_insn(aan, space, cap):
    return apply_aan(aan, 'a') + space, cap('a'), ' ', no_op

def apply_aan(aan, s):
    return aan and aan + ('n' if s.startswith(vowels) else '')

vowels = tuple('aeiouAEIOU')

no_op = lambda s: s
