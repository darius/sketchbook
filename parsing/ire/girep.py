"""
Like grep, but for pegs.
TODO:
- Some kind of multiline mode
- How to generalize grep to semantic actions?
  - Make it more like Perl? Like 'structural regular expressions'?
"""

import sys

import ire

def main(argv):
    pattern = argv[1]
    filenames = argv[2:] or ['/dev/stdin']
    pegex = ire.compile(pattern)
    if not filenames:
        errcode = girep(pegex, sys.stdin)
    else:
        errcode = 0
        for filename in filenames:
            with open(filename) as f:
                prefix = filename + ':' if 1 < len(filenames) else ''
                ec = girep(pegex, f, prefix)
                errcode = max(errcode, ec)
    return errcode

def girep(pegex, f, prefix=''):
    matched = 0
    for line in f:
        line = line.rstrip('\n') # I guess
        m = pegex.match(line)
        if m:
            print prefix + line
            matched = 1
    return matched

if __name__ == '__main__':
    sys.exit(main(sys.argv))
