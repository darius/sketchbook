"""
Parse infix expressions by precedence climbing. N.B. Not quite identical to 
http://en.wikipedia.org/wiki/Operator-precedence_parser#Precedence_climbing_method
so maybe I should rename this. I learned this method from Dave Gillespie.
"""

import operator

default_infix_ops = {
  # lprec means left-precedence, rprec means right
  # token  lprec rprec     op
    '+':    (10,   11,   operator.add), # left-associative
    '-':    (10,   11,   operator.sub),
    '*':    (20,   21,   operator.mul),
    '/':    (20,   21,   operator.div), 
    '^':    (30,   30,   pow),          # right-associative
}

default_prefix_ops = {
  # token  pprec    op
    '-':    (20,  lambda n: -n),
}

def make_parse_primary(parse_literal=int, prefix_ops=default_prefix_ops):
    """The infix parser calls on a 'primary' parser for its noninfix
    subexpressions. You can give it an arbitrary primary parser, but
    here's one for the simple common case of prefix operators,
    parentheses, and literals."""
    def parse_primary(scan, parse_expr, infix_ops):
        if scan.token in default_prefix_ops:
            pprec, op = prefix_ops[scan.token]
            scan()
            return op(parse_expr(pprec))
        elif scan.token == '(':
            scan()
            result = parse_expr(0)
            assert scan.token == ')', "Missing ')'"
            scan()
            return result
        elif scan.token not in infix_ops:
            result = parse_literal(scan.token)
            scan()
            return result
        else:
            assert False, "Unexpected operator: %r" % scan.token
    return parse_primary

def make_parse_expr(scan, infix_ops, parse_primary):
    def parse_expr(min_precedence):
        """Parse a head of the scanner's stream as an infix expression whose
        operators (unless in parentheses) all have lprec >= min_precedence."""
        operand = parse_primary(scan, parse_expr, infix_ops)
        while True:
            lprec, rprec, op = infix_ops.get(scan.token, (-1, -1, None))
            if lprec < min_precedence: return operand
            scan()
            operand = op(operand, parse_expr(rprec))
    return parse_expr

def parse_infix(tokens,
                infix_ops=default_infix_ops,
                parse_primary=make_parse_primary()):
    "Parse the whole tokens input as an infix expression."

    def scan(): scan.token = next(tokens, None)
    tokens = iter(tokens)
    scan()

    parse_expr = make_parse_expr(scan, infix_ops, parse_primary)
    result = parse_expr(0)
    assert scan.token is None, "Input not fully consumed"
    return result


def demo(s): return parse_infix(s.replace(' ', ''))

## demo('5')
#. 5
## demo('(((9)))')
#. 9
## demo('-8')
#. -8
## demo('2*3')
#. 6
## demo('5 + 2 * 3')
#. 11
## demo('5-1-2')
#. 2
## demo('4^3^2')
#. 262144
## demo('4^(3^2)')
#. 262144
## demo('(4^3)^2')
#. 4096
## demo('5-(1-2)')
#. 6

## demo('1+-2*3+4')
#. -1
