import random, re

# N.B. the words can be arbitrary text.
dictionary = {word: expansion.strip()
              for line in open('menu.text')
              for word, expansion in [line.split(':', 1)]}

def expand_word(word, probability=.99):
    """Given a dictionary word, replace it with its definition or not,
    randomly. Further expand the definition (but less probably, to
    make it eventually stop growing)."""
    if random.random() < probability:
        return expand_text(dictionary[word], probability * .8)
    else:
        return word

def expand_text(text, probability):
    "Find substrings like [blah], and expand them."
    return re.sub(r'\[([^]]*)\]',
                  lambda match: expand_word(match.group(1), probability),
                  text)

if __name__ == '__main__':
    import sys
    print expand_word(sys.argv[1])
