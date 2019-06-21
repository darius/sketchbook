"""
Rapid Serial Visual Presentation
TODO:
  * Split input into sentences.
    A chunk shouldn't span a sentence boundary.
    There should be a slight delay after a sentence.
  * Try showing chunks above and below the current one.
  * Speed control.
  * A TeX-like optimization algorithm to pick chunk boundaries.

See https://github.com/pasky/speedread/blob/master/speedread
"""

from __future__ import division
import sys
import textwrap
import time

prefix = '\x1b['
home         = prefix + 'H'
clear_screen = prefix + '2J' + home

def main(filename, width, cpm):
    with open(filename) as f:
        text = f.read()
    paragraphs = text.split('\n\n')
    chunks = enchunk(paragraphs, width)
    print clear_screen
    rsvp(chunks, 60/cpm)

def rsvp(chunks, interval):
    for chunk in chunks:
        print '\r', chunk.center(76),
        sys.stdout.flush()
        time.sleep(interval)
    print

def enchunk(paragraphs, width):
    wrapper = textwrap.TextWrapper(width=width, break_long_words=False)
    for para in paragraphs:
        para = ' '.join(para.split())
        for chunk in wrapper.wrap(para):
            yield chunk
        yield ''

def enchunk_obsolete(paragraphs, width):
    for para in paragraphs:
        chunk = ''
        for word in para.split():
            more = chunk + ' ' + word if chunk else word
            if chunk and width < len(more):
                yield chunk
                chunk = word
            else:
                chunk = more
        if chunk: yield chunk
        yield ''


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
