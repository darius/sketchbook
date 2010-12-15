"""
Collect state-counts for DFAs of a bunch of regular expressions;
and test that different implementations work the same.
"""

import dfa_deriv2 as m1
import dfa_nfa as m2

import dfa_minimize
import enum_res
import parse

max_size = 6

def write_counts(module):
    out = open(module.__name__ + '.counts', 'w')
    for re in a_bunch(module.Maker()):
        dfa = module.make_dfa(re)
        print >>out, len(dfa)
    out.close()

def a_bunch(maker):             # TODO use flatmap
    acc = []
    for size in range(max_size + 1):
        acc.extend(enum_res.gen_res(maker, '01', size))
    return acc

testing = False

def test(module1, module2):
    "Look for inconsistency between module1 and module2's re implementations."
    if testing: test_strings = collect_test_strings()
    maxdiff = 1
    maxmindiff = 0
    for re1, re2, re_string in zip(a_bunch(module1.Maker()),
                                   a_bunch(module2.Maker()),
                                   a_bunch(parse.TreeMaker())):
        dfa1 = module1.make_dfa(re1)
        dfa2 = module2.make_dfa(re2)
        if testing:
          for s in test_strings:
            match1 = matches(dfa1, s)
            match2 = matches(dfa2, s)
            if match1 != match2:
                print '*** CONFLICT:', re_string
                print module1.__name__, match1
                print module2.__name__, match2
                print
        if len(dfa1) < len(dfa2):
            print '*** m1 IS SMALLER FOR', re_string
            print module1.__name__ + ':'
            dump(dfa1)
            print
            print module2.__name__ + ':'
            dump(dfa2)
            print
        else:
            diff = len(dfa1) - len(dfa2)
            if maxdiff < diff:
                maxdiff = diff
                print 'new maxdiff for', re_string
                print module1.__name__ + ':'
                dump(dfa1)
                print
                print module2.__name__ + ':'
                dump(dfa2)
                print
        min_count = dfa_minimize.minimal_state_count(dfa2)
        if min_count < min(len(dfa1), len(dfa2)):
            diff = min(len(dfa1), len(dfa2)) - min_count
            if maxmindiff < diff:
                maxmindiff = diff
                print 'DFA MINIMIZATION WINS for', re_string
                print 'minimum state count:', min_count
                print module1.__name__ + ':'
                dump(dfa1)
                print
                print module2.__name__ + ':'
                dump(dfa2)
                print


def dump(dfa):
    for i, (accepting, moves) in enumerate(dfa):
        print i, ' *'[accepting], moves

def matches(dfa, s):
    state = 0
    accepting = dfa[0][0]
    for c in s:
        accepting, moves = dfa[state]
        state = moves.get(c)
        if state is None:
            return False
    return accepting

def collect_test_strings(alphabet='01', max_length=max_size+5):
    return flatmap(lambda length: gen_strings(length, alphabet),
                   range(max_length + 1))

def gen_strings(length, alphabet):
    if length == 0:
        return ['']
    else:
        return flatmap(lambda s: map(lambda c: s + c, alphabet),
                       gen_strings(length - 1, alphabet))

## collect_test_strings('01', 2)
#. ['', '0', '1', '00', '01', '10', '11']
## gen_strings(3, '01')
#. ['000', '001', '010', '011', '100', '101', '110', '111']

def flatmap(f, xs):
    acc = []
    for x in xs:
        acc.extend(f(x))
    return acc

if __name__ == '__main__':
    if True:
        test(m1, m2)
    else:
        write_counts(m1)
        write_counts(m2)
