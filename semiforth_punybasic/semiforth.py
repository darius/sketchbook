r'''
Semideterministic Forth. (Call it Eighth?)

A variant of peglet.py (for documentation look there) with these changes:

  * There's no seclusion: when parsing a rule, it passes in the
    current values stack instead of creating a fresh new empty
    one.
  * There's no memoization, since we'd have to memoize on the
    contents of the passed-in stack as well as the position in
    the input.

This bears a relation to Icon too, since there's an implicit subject
for string matching. The difference is there's semideterminism but not
more general nondeterminism.
'''

import operator, re, sys

_identifier = r'[A-Za-z_]\w*'

def Parser(grammar, **actions):
    r"""Make a parsing function from a peglet grammar, defining the
    grammar's semantic actions with keyword arguments.

    The parsing function maps a string to a results tuple or raises
    Unparsable. (It can optionally take a rule name to start from, by
    default the first in the grammar.) It doesn't necessarily match
    the whole input, just a prefix.

    >>> nums = Parser(r"nums = num ,\s* nums | num   num = (\d+) int", int=int)
    >>> nums('42, 137, and 0 are magic numbers')
    (42, 137)
    >>> nums('The magic numbers are 42, 137, and 0')
    Traceback (most recent call last):
    Unparsable: ('nums', '', 'The magic numbers are 42, 137, and 0')
    """
    parts = re.split(' ('+_identifier+') += ',
                     ' '+re.sub(r'\s', ' ', grammar))
    if len(parts) == 1 or parts[0].strip():
        raise BadGrammar("Missing left hand side", parts[0])
    if len(set(parts[1::2])) != len(parts[1::2]):
        raise BadGrammar("Multiply-defined rule(s)", grammar)
    rules = dict((lhs, [alt.split() for alt in (' '+rhs+' ').split(' | ')])
                 for lhs, rhs in zip(parts[1::2], parts[2::2]))
    return lambda text, rule=parts[1]: _parse(rules, actions, rule, text)

class BadGrammar(Exception):
    "A peglet grammar was ill-formed."

class Unparsable(Exception):
    "An attempted parse failed because the input did not match the grammar."

def _parse(rules, actions, rule, text):
    # Each function takes a position pos and a values tuple vals, and
    # returns either (far, pos1, vals1) on success or (far, None,
    # garbage) on failure (where far is the rightmost position reached
    # in the attempt).

    def parse_rule(name, pos, vals):
        farthest = pos
        for alternative in rules[name]:
            pos1, vals1 = pos, vals
            for token in alternative:
                far, pos1, vals1 = parse_token(token, pos1, vals1)
                farthest = max(farthest, far)
                if pos1 is None: break
            else: return farthest, pos1, vals1
        return farthest, None, ()

    def parse_token(token, pos, vals):
        if re.match(r'!.', token):
            _, pos1, _ = parse_token(token[1:], pos, vals)
            return pos, pos if pos1 is None else None, vals
        elif token in rules:
            return parse_rule(token, pos, vals)
        elif token in actions:
            f = actions[token]
            if hasattr(f, 'semiforth_prim'): return f(text, pos, vals) 
            else: return pos, pos, f(*vals)
        elif token.isdigit():
            return pos, pos, vals + (int(token),)
        else:
            if re.match(_identifier+'$', token):
                raise BadGrammar("Missing rule", token)
            if re.match(r'/.+/$', token): token = token[1:-1]
            m = re.match(token, text[pos:])
            if m: return pos + m.end(), pos + m.end(), vals + m.groups()
            else: return pos, None, ()

    far, pos, vals = parse_rule(rule, 0, ())
    if pos is None: raise Unparsable(rule, text[:far], text[far:])
    else: return vals

# Conveniences

def attempt(parser, *args, **kwargs):
    "Call a parser, but return None on failure instead of raising Unparsable."
    try: return parser(*args, **kwargs)
    except Unparsable: return None

def OneResult(parser):
    "Parse like parser, but return exactly one result, not a tuple."
    def parse(text):
        results = parser(text)
        assert len(results) == 1, "Expected one result but got %r" % (results,)
        return results[0]
    return parse

# Some often-used actions:

def hug(*xs):
    "Return a tuple of all the arguments."
    return xs

def join(*strs):
    "Return all the arguments (strings) concatenated into one string."
    return ''.join(strs)

def position(text, pos, vals):
    "A peglet action: always succeed, producing the current position."
    return pos, pos, vals + (pos,)
position.semiforth_prim = True


# Forth

def mkprim(n, fn):
    return lambda *vals: vals[:-n] + (fn(*vals[-n:]),)

def mkaction(fn):
    return lambda *vals: null(fn())

def null(x): return ()

def mkstacker(n, fn):
    return lambda *vals: vals[:-n] + fn(*vals[-n:])

def mkpred(n, fn):
    def pred(text, pos, vals):
        if fn(*vals[-n:]):
            return pos, pos, vals[:-n]
        else:
            return pos, None, ()
    pred.semiforth_prim = True
    return pred

primitives = {
    'drop':   mkstacker(1, lambda x: ()),
    'dup':    mkstacker(1, lambda x: (x, x)),
    'swap':   mkstacker(2, lambda x, y: (y, x)),
    'over':   mkstacker(2, lambda x, y: (x, y, x)),
    'rot':    mkstacker(3, lambda x, y, z: (y, z, x)),

    '+':      mkprim(2, operator.add),
    '-':      mkprim(2, operator.sub),
    '*':      mkprim(2, operator.mul),
    '/':      mkprim(2, operator.truediv),
    '//':     mkprim(2, operator.idiv),
    '%':      mkprim(2, operator.imod),
    '**':     mkprim(2, operator.pow),
    'negate': mkprim(1, operator.neg),
    'int':    mkprim(1, int),

    'write':  mkstacker(1, lambda x: null(sys.stdout.write(str(x)))),
    'space':  mkaction(lambda: sys.stdout.write(' ')),
    'newline': mkaction(lambda: sys.stdout.write('\n')),

    '<':      mkpred(2, operator.lt),
    '<=':     mkpred(2, operator.le),
    '=':      mkpred(2, operator.eq),
    '!=':     mkpred(2, operator.ne),
    '>=':     mkpred(2, operator.ge),
    '>':      mkpred(2, operator.gt),

    'position': position,
}


# Smoke test

def eighth(program, input_text):
    return Parser(program, **primitives)(input_text)

eg = r"""
main  = wc fib

fib   = dup 2 <  drop 1
      | dup 1 - fib  swap 2 - fib +

wc    = 0 _ words
words = 1 + word words
      | 
word  = \w+ _
_     = \s*
"""

## eighth(eg, 'hi there  yo dude yay')
#. (8,)
