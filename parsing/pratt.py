"""
Pratt parser for infix expressions
http://eli.thegreenplace.net/2010/01/02/top-down-operator-precedence-parsing/
"""

import re

## parse('1+2*3+4')
#. 11

def parse(s):
    next = tokenize(s).next
    token = Struct(_=next())
    def parse_expression(rbp):
        nud, token._ = token._.nud, next()
        left = nud(parse_expression)
        while rbp < token._.lbp:
            led, token._ = token._.led, next()
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

class Struct:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
