# http://en.wikipedia.org/wiki/List_of_poker_hands
# http://www.reddit.com/comments/6u4pn/what_successful_software_projects_are_oneman/

# TODO: test
# TODO: polish some more

import collections

## go()
#. (2, 14, 10, 9, 5, 4) Ad 0d 9s 5c 4c
#. (2, 14, 10, 9, 5, 4) 9s 5c Ad 4c 0d
#. (2, 13, 12, 11, 8, 7) Jc Qd 8h 7h Kc
#. 

## hand_rank('Ad 0d 9s 5c 4c'.split())
#. (2, 14, 10, 9, 5, 4)
## hand_rank('9s 5c Ad 4c 0d'.split())
#. (2, 14, 10, 9, 5, 4)
## hand_rank('Jc Qd 8h 7h Kc'.split())
#. (2, 13, 12, 11, 8, 7)
## hand_rank('Jc 0d 8h 7h 9c'.split())
#. (6, 11)

def go():
    check('Ad 0d 9s 5c 4c')
    check('9s 5c Ad 4c 0d')
    check('Jc Qd 8h 7h Kc')
    return
    check('')
    check('')
    check('')

def check(s):
    hand = s.split()
    print hand_rank(hand), s

def best_hand(hands):
    return max(hands, key=hand_rank)

def hand_rank(hand):
    kinds = descending(map(card_kind, hand))
    suits = map(card_suit, hand)
    def rank(r, opt_subrank):
        return opt_subrank and tuple(map(kind_rank, r + opt_subrank))
    return (   rank('0', flush(kinds, suits) and straight(kinds))
            or rank('9', n_of_a_kind(4, kinds))
            or rank('8', full_house(kinds))
            or rank('7', flush(kinds, suits))
            or rank('6', straight(kinds))
            or rank('5', n_of_a_kind(3, kinds))
            or rank('4', n_pairs(2, kinds))
            or rank('3', n_pairs(1, kinds))
            or rank('2', kinds))


# Hands. In all cases kinds must be sorted descending by rank.

def n_of_a_kind(n, kinds):
    g = find(groups(n, kinds))
    return g and g + descending(k for k in kinds if k != g)

def full_house(kinds):
    return n_of_a_kind(2, kinds) and n_of_a_kind(3, kinds)

def flush(kinds, suits):
    return 1 == len(set(suits)) and kinds

def straight(kinds):
    return (consecutive(kinds)                       # Try aces high
            or consecutive(kinds.replace('A', '1'))) # and aces low

def n_pairs(n, kinds):
    paired = groups(2, kinds)
    return (n == len(paired)
            and descending(paired) + descending(groups(1, kinds)))

def consecutive(kinds):
    "Return the high rank if a straight, else None."
    return (len(kinds) == len(set(kinds))
                       == kind_rank(kinds[0]) - kind_rank(kinds[-1]) + 1
            and kinds[0])

def descending(kinds):
    return ''.join(sorted(kinds, key=kind_rank, reverse=True))

def groups(n, kinds):
    "Return those kinds that appear in groups of n."
    d = collections.defaultdict(int)
    for kind in kinds:
        d[kind] += 1
    return [kind for kind, count in d.items() if count == n]


# Cards:
# kind + suit
# 'As' ace of spades
# '0c' ten of clubs
# Kinds: A, K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1 (1 for a low ace)
# Suits: h s c d: heart spade club diamond

def card_kind(card): return card[0]
def card_suit(card): return card[1]

def kind_rank(kind):
    "Return a numeric rank, aces high."
    return 1 + '1234567890JQKA'.index(kind)


# Helpers

def find(it):
    "Return the first non-None value, else None."
    for x in it:
        if x:
            return x
    return None


if __name__ == '__main__':
    go()
