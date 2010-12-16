import dfa_nfa as dfa_module
#import dfa_deriv2 as dfa_module
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
#. 75
from dfa_minimize import minimal_state_count
## minimal_state_count(dfa)
#. 48

def scan(s):
    while True:
        label, token, rest = scan1(s)
        if label is None: break
        print '%2s' % (label or ''), repr(token)
        s = rest
    if s: print 'left over: %r' % s

def scan1(s):
    label, moves = dfa[0]
    accepted = None
    for i, c in enumerate(s):
        if c not in moves: break
        label, moves = dfa[moves[c]]
        if label is not None: accepted = (i+1, label)
    if accepted:
        j, label = accepted
        return label, s[:j], s[j:]
    else:
        return None, '', s

## scan('')
## scan('  if for long defined   int world')
#.    '  '
#. 10 'if'
#.    ' '
#. 13 'for'
#.    ' '
#.  4 'long'
#.    ' '
#.  1 'defined'
#.    '   '
#.  3 'int'
#.    ' '
#. left over: 'world'
#. 

## dfa_module.dump(dfa)
#. 0 <0> '\t':1 ' ':1 'b':2 'c':7 'd':20 'e':32 'f':36 'i':43 'l':47 's':51 'u':62 'w':70
#. 1 <0> '\t':1 ' ':1
#. 2     'r':3
#. 3     'e':4
#. 4     'a':5
#. 5     'k':6
#. 6 <16> 
#. 7     'h':8 'o':11
#. 8     'a':9
#. 9     'r':10
#. 10 <7> 
#. 11     'n':12
#. 12     's':13 't':15
#. 13     't':14
#. 14 <9> 
#. 15     'i':16
#. 16     'n':17
#. 17     'u':18
#. 18     'e':19
#. 19 <17> 
#. 20     'e':21 'o':27
#. 21     'f':22
#. 22     'i':23
#. 23     'n':24
#. 24     'e':25
#. 25     'd':26
#. 26 <1> 
#. 27 <14> 'u':28
#. 28     'b':29
#. 29     'l':30
#. 30     'e':31
#. 31 <6> 
#. 32     'l':33
#. 33     's':34
#. 34     'e':35
#. 35 <11> 
#. 36     'l':37 'o':41
#. 37     'o':38
#. 38     'a':39
#. 39     't':40
#. 40 <5> 
#. 41     'r':42
#. 42 <13> 
#. 43     'f':44 'n':45
#. 44 <10> 
#. 45     't':46
#. 46 <3> 
#. 47     'o':48
#. 48     'n':49
#. 49     'g':50
#. 50 <4> 
#. 51     't':52 'w':57
#. 52     'r':53
#. 53     'u':54
#. 54     'c':55
#. 55     't':56
#. 56 <8> 
#. 57     'i':58
#. 58     't':59
#. 59     'c':60
#. 60     'h':61
#. 61 <12> 
#. 62     'n':63
#. 63     's':64
#. 64     'i':65
#. 65     'g':66
#. 66     'n':67
#. 67     'e':68
#. 68     'd':69
#. 69 <2> 
#. 70     'h':71
#. 71     'i':72
#. 72     'l':73
#. 73     'e':74
#. 74 <15> 
#. 
