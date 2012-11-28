"""
Like http://www.eblong.com/zarf/mutagen/mutagen.js
(More or less; assume 'less', for now.)
The C version of Elite would be another thing-of-this-sort to study.

TODO:
  - clean up 'fixed' mess
  - better naming
  - documentation
  - fix quadratic-time formatting
  - compare to original and learn from the difference
"""

from itertools import count, izip
import random

def mutagen(gen, seed=None):
    return render(RNG(seed).call(gen))


# Generator state

class RNG:
    def __init__(self, seed=None):
        self.random = random.Random(seed)
        self.fixed_table = {}
        self.choice_table = {}
        self.weighted_choice_table = {}
    def call(self, gen):
        return desugar(gen)(self)
    def choice(self, values):
        return self.random.choice(values)
    def weighted_choice(self, weights):
        return weighted_choose(self.random.randint, weights)
    def fixed(self, tag, chooser, values):
        if tag not in self.fixed_table:
            eep = chooser(*map(lambda i: lambda rng: i,
                               range(len(values))))
            index = eep(self)
            self.fixed_table[tag] = index
        return values[self.fixed_table[tag]]

def weighted_choose(randint, weights):
    k = randint(0, sum(weights) - 1)
    for weight, i in izip(weights, count()):
        if k < weight:
            return i
        k -= weight
    assert False, "Unreachable"


# Generators

def literal(s):      return lambda rng: [lit_insn(s)]
def choice(*gens):   return lambda rng: rng.call(rng.choice(gens))
def sequence(*gens): return lambda rng: flatmap(rng.call, gens)

def flatmap(f, xs):
    return sum(map(f, xs), [])

def weighted_choice(*weights):
    return lambda *gens: lambda rng: \
        rng.call(gens[rng.weighted_choice(weights)])

def fixed(chooser):
    tag = next(counter)
    return lambda *gens: lambda rng: \
        rng.call(rng.fixed(tag, chooser, gens))

counter = count()

def empty(rng):      return []
def abut(rng):       return [abut_insn]
def capitalize(rng): return [capitalize_insn]
def a_an(rng):       return [a_an_insn]

comma  = sequence(abut, literal(","))
period = sequence(abut, literal("."), capitalize)


# Sugar

def desugar(x):
    if isinstance(x, (unicode, str)):
        return literal(x)
    if isinstance(x, (list, tuple)):
        return sequence(*x)
    return x


# Formatting

def render(insns):
    return insns[0](insns[1:]) if insns else ''

def capitalize_insn(insns):
    return render(insns).capitalize()

def lit_insn(s):
    def insn(insns):
        rest = render(insns)
        sep = '' if insns[0:1] == [abut_insn] else space(rest)
        return s + sep + rest
    return insn

abut_insn = render

def a_an_insn(insns):
    s = render(insns)
    return ("an" if s[0:1] in 'aeiouy' else "a") + space(s) + s

def space(s):
    return ' ' if s else ''


# Tests

def eg(gen): return mutagen(gen, 142)

## eg("hello")
#. 'hello'

## eg(["hello", empty, "world"])
#. 'hello world'

## eg(choice("hello", "world"))
#. 'world'

## eg(choice("hello", comma, "cruel", "world"))
#. 'cruel'

## eg(["hello", comma, "cruel", "world", period, "yo"])
#. 'hello, cruel world. Yo'

## L = fixed(choice)
## def yn(s): return L(*s.split())
## eg([yn('0 1'), yn('N Y'), yn('F T')])
#. '1 Y T'

wchoice = weighted_choice

by_gender = fixed(choice)

FemaleName = choice("Emmalissa", "Chloe", "Tiffani", "Eunice", "Zoe",
    "Jennifer", "Imelda", "Yvette", "Melantha")
MaleName = choice("Bernard", "Joseph", "Emmett", "Ogden", "Eugene",
    "Xerxes", "Joshua", "Lemuel", "Etienne")

Name = by_gender(MaleName, FemaleName)
HeShe = by_gender("he", "she")

PersonAdjective = choice("precocious", "unflappable", "energetic",
    "forceful", "inimitable", "daring", "mild", "intense", "jaded")

Intensifier = choice("great", "some", "considerable", "not inconsiderable",
    "distinct", "impressive", "unique", "notable")

NeutralDescriptor = choice("toddler", "aesthete", "writer", "artist")
MaleDescriptor = choice("stalwart", "gentleman", "boy", "youth")
FemaleDescriptor = choice("young miss", "girl", "maiden", "flapper")
Descriptor = wchoice(1, 1)(NeutralDescriptor,
                           by_gender(MaleDescriptor, FemaleDescriptor))

DescriptorModifier = ["of", Intensifier,
                      choice("perspicacity", "fortitude", "passion", "wit", 
                             "perception", "presence of mind")]

CommaDescriptionPhrase = [comma, a_an, 
                          wchoice(1, 1)(PersonAdjective, empty),
                          Descriptor,
                          wchoice(1, 2)(DescriptorModifier, empty),
                          comma]

PersonDescription = [Name, 
                     wchoice(2, 1)(CommaDescriptionPhrase, empty)]

## eg(PersonDescription)
#. 'Imelda, a forceful girl of some wit,'
