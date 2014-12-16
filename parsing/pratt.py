"""
Pratt parser for infix expressions
http://eli.thegreenplace.net/2010/01/02/top-down-operator-precedence-parsing/
# TODO: see if any ideas from precedence_climbing.py can improve this
#       or vice-versa
"""

import re

## parse('1+2*3+4')
#. 11

def parse(s):
    next = tokenize(s).next
    def my(): pass # A hack to express a nonlocal mutable variable in Python 2.
    my.token = next()
    def parse_expression(rbp):
        nud, my.token = my.token.nud, next()
        left = nud(parse_expression)
        while rbp < my.token.lbp:
            led, my.token = my.token.led, next()
            left = led(left, parse_expression)
        return left
    return parse_expression(0)

def tokenize(s):
    for number, operator in re.findall(r'\s*(?:(\d+)|(.))', s):
        if number:
            yield Token(number, nud=lambda pe, value=int(number): value)
        elif operator == '+':
            yield Token('+', lbp=10,
                        led=lambda left, pe: left + pe(10))
        elif operator == '*':
            yield Token('*', lbp=20,
                        led=lambda left, pe: left * pe(20))
        else:
            raise SyntaxError('unknown operator: %s', operator)
    yield Token('<eof>')
            
class Token:
    def __init__(self, datum, lbp=0, led=None, nud=None):
        self.datum = datum
        self.lbp = lbp
        self.led = led
        self.nud = nud
    def __repr__(self):
        return repr(self.datum)
