"""
Building and running a RETE network. Not including the compiler to
translate a production system to a RETE network.

This sketch may be a dead end because there's a cyclic reference
which the approach handles poorly. See smoke test.
"""

from collections import deque

def run(root, initial_facts):
    agenda = deque()
    for fact in initial_facts:
        root(agenda, fact)
    while agenda:
        fact = agenda.popleft()
        yield fact
        root(agenda, fact)

empty_join_store = [[]]

def Store(eaters):
    store = []
    def eat(agenda, thing):
        store.append(thing)
        feed(eaters, agenda, thing)
    return eat, store

def feed(eaters, agenda, thing):
    for eater in eaters:
        eater(agenda, thing)

def dropper(agenda, fact):
    pass

def LengthMatcher(length, match_eater, nonmatch_eater):
    def eat(agenda, fact):
        (match_eater if len(fact) == length else nonmatch_eater)(agenda, fact)
    return eat

def Matcher(position, atom, match_eater, nonmatch_eater):
    def eat(agenda, fact):
        if position < len(fact) and atom == fact[position]: # XXX I think the length test is redundant here
            match_eater(agenda, fact)
        else:
            nonmatch_eater(agenda, fact)
    return eat

def Joiner(keys, facts, joins, eaters):
    def eat_match(agenda, fact):
        for join in joins:
            check(agenda, fact, join)
    def eat_join(agenda, join):
        for fact in facts:
            check(agenda, fact, join)
    def check(agenda, fact, join):
        if all(fact[f_slot] == join[j][j_slot] for f_slot, j, j_slot in keys):
            feed(eaters, agenda, join + [fact])
    return eat_match, eat_join

def Firer(fillers):
    # XXX what about fresh vars?
    def eat(agenda, join):
        for filler in fillers:
            agenda.append([adder(join) for adder in filler])
    return eat

def AtomAdder(atom):
    return lambda join: atom

def VariableAdder(fact_num, slot_num):
    return lambda join: join[fact_num][slot_num]


# Smoke test: sample_rules from production.py

on_mom_add, mom_facts = Store([]) # XXX not needed, right? ditto for joiner.
mom_fire = Firer([[AtomAdder('parent'),
                   VariableAdder(0, 1),
                   VariableAdder(0, 2)]])
on_mom, on_mom_join = Joiner([], mom_facts, empty_join_store, [mom_fire])

on_dad_add, dad_facts = Store([])
dad_fire = mom_fire
on_dad, on_dad_join = Joiner([], dad_facts, empty_join_store, [dad_fire])
# N.B. on_dad == on_mom except for the separate store

on_parent_add, parent_facts = Store([])
parent_fire = Firer([[AtomAdder('grandparent'),
                      VariableAdder(0, 1), # XXX
                      VariableAdder(0, 2)]])
on_parent, on_parent_join = Joiner([(1, 0, 2)],
                                   parent_facts, empty_join_store, [parent_fire])

on_parent = dropper             # XXX

root = LengthMatcher(3, Matcher(0, 'mom', on_mom,
                                Matcher(0, 'dad', on_dad,
                                        Matcher(0, 'parent', on_parent,
                                                dropper))),
                     dropper)

## for fact in run(root, [['dad', 'tywin', 'cersei'], ['mom', 'cersei', 'myrcella']]): print fact
#. ['parent', 'tywin', 'cersei']
#. ['parent', 'cersei', 'myrcella']
