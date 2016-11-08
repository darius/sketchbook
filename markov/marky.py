"""
generate text by markov chain of words
"""

import random, re

def words(text):
    return (m.group(0)
#            for m in re.finditer(r'''[A-Za-z]+(?'[a-z])?''', text))
            for m in re.finditer(r'[A-Za-z]+', text))

model = {}                      # (word,) -> {word2: count}

## get_word(model['three',])
#. 'rings'

text = list(words(open('the-fellowship-of-the-ring.txt').read().lower()))
## text[:10]
#. ['three', 'rings', 'for', 'the', 'elven', 'kings', 'under', 'the', 'sky', 'seven']

example_dict = {'Elven': 1, 'sky': 2}

def get_word(d):
    probs = 0
    max_probs = {}
    for k, v in d.items():
      probs += v
      max_probs[probs] = k
    n = random.randint(0, probs-1)
    for p, word in sorted(max_probs.items()):
      if n < p:
            return word

## get_word(example_dict)
#. 'Elven'

for i in range(len(text)-1):
    next_word = text[i+1]
    submodel = model.setdefault((text[i],), {})
    submodel[next_word] = submodel.get(next_word, 0) + 1

context = ('three',)
for word in context:
    print word,
for _ in xrange(100):
    word = get_word(model[context])
    print word,
    context = context[:-1] + (word,)

#. three of soft voices they love peace of slipping away answering horns blowing and leaning squat or twice they can hear me also to fetch the landing since the fire and stone he will explain your accident has gone and yestereve a lot of those of belfalas to move or two higher shoulders her maidens stood before we cannot be seen them save you but it would follow as my heart tell them was still be welcome to the currents of time is their minds from some of watchman he said pippin was broad white flashes and to know sam that
