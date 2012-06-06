# http://www.cs.princeton.edu/courses/archive/spr09/cos333/beautiful.html

# regexp ::= '^'? (('.' | literal) '*'?)* '$'?
def match(re, text):
    if re.startswith('^'): return matchhere(re[1:], text) 
    else: return matchstar('.', re, text)

def matchhere(re, text):
    while re:
        if re == '$':      return text == '' 
        if re[1:2] == '*': return matchstar(re[0], re[2:], text)
        if text == '' or re[0] not in ('.', text[0]):
            return False
        re, text = re[1:], text[1:]
    return True

def matchstar(c, re, text):
    while not matchhere(re, text):
        if text == '' or c not in (text[0], '.'):
            return False
        text = text[1:]
    return True

# New version taking after https://gist.github.com/2789897
def matchstar(c, re, text):
    for i, ti in enumerate(text):
        if matchhere(re, text[i:]): return True
        if c not in (ti, '.'): return False
    return matchhere(re, '')

# Or how about this?
def matchhere_v0(re, text):
    return (re == '' or
            matchstar(re[0], re[2:], text) if re[1:2] == '*' else
            text == '' if re == '$' else
            text and re[:1] in ('.', text[0]) and matchhere(re[1:], text[1:]))

# TODO: actually test this
