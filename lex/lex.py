#import dfa_nfa as dfa_module
import dfa_deriv2 as dfa_module
import dfa_statecount
from parse import make_parser

maker = dfa_module.Maker()
parse = make_parser(maker)

whitespace = parse('( |\t)*')
re_strings = open('c-lex0').read().splitlines()
res = map(parse, re_strings)
alts = maker.make_scanner(whitespace, res)
dfa = dfa_module.make_dfa(alts)
## len(dfa)
#. 48
from dfa_minimize import minimal_state_count
## minimal_state_count(dfa)
#. 48

def scan(s):
    while True:
        token, rest = scan1(s)
        if token is None: break
        print repr(token)
        s = rest
    if s: print 'left over: %r' % s

def scan1(s):
    state = 0
    assert not dfa[state][0], "We're not designed to accept 0-length tokens"
    accepted = None
    for i, c in enumerate(s):
        moves = dfa[state][1]
        if c not in moves: break
        state = moves[c]
        if dfa[state][0]: accepted = i+1
    return accepted and s[:accepted], s[accepted:]

## scan('  if for long defined   int world')
#. '  if'
#. ' for'
#. ' long'
#. ' defined'
#. '   int'
#. left over: ' world'
#. 

## dfa_statecount.dump(dfa)
#. 0   {' ': 0, 'c': 6, 'b': 1, 'e': 25, 'd': 16, 'f': 27, '\t': 0, 'l': 31, 'i': 30, 's': 34, 'u': 42, 'w': 46}
#. 1   {'r': 2}
#. 2   {'e': 3}
#. 3   {'a': 4}
#. 4   {'k': 5}
#. 5 * {}
#. 6   {'h': 7, 'o': 9}
#. 7   {'a': 8}
#. 8   {'r': 5}
#. 9   {'n': 10}
#. 10   {'s': 11, 't': 12}
#. 11   {'t': 5}
#. 12   {'i': 13}
#. 13   {'n': 14}
#. 14   {'u': 15}
#. 15   {'e': 5}
#. 16   {'e': 17, 'o': 22}
#. 17   {'f': 18}
#. 18   {'i': 19}
#. 19   {'n': 20}
#. 20   {'e': 21}
#. 21   {'d': 5}
#. 22 * {'u': 23}
#. 23   {'b': 24}
#. 24   {'l': 15}
#. 25   {'l': 26}
#. 26   {'s': 15}
#. 27   {'l': 28, 'o': 8}
#. 28   {'o': 29}
#. 29   {'a': 11}
#. 30   {'n': 11, 'f': 5}
#. 31   {'o': 32}
#. 32   {'n': 33}
#. 33   {'g': 5}
#. 34   {'t': 35, 'w': 38}
#. 35   {'r': 36}
#. 36   {'u': 37}
#. 37   {'c': 11}
#. 38   {'i': 39}
#. 39   {'t': 40}
#. 40   {'c': 41}
#. 41   {'h': 5}
#. 42   {'n': 43}
#. 43   {'s': 44}
#. 44   {'i': 45}
#. 45   {'g': 19}
#. 46   {'h': 47}
#. 47   {'i': 24}
#. 
