"""
Hi I'm MacRoe and I'll be your macro evaluator today.
I'm pretty simpleminded, so you know.

TODO:
  user-defined macros
  conditionals
  some way to quote metacharacters
  more primitives
"""

import sys

def main(argv):
    if argv[1:]:
        for filename in argv[1:]:
            with open(filename) as f:
                macroe(f)
    else:
        macroe(sys.stdin)

def macroe(infile):
    for ch in expand(file_chars(infile)):
        sys.stdout.write(ch)

def file_chars(infile):
    while True:
        ch = infile.read(1)
        if not ch: break
        yield ch

def expand(chars):
    for ch in chars:
        if ch == '{':
            for x in expand(call(collect_call(chars))):
                yield x
        else:
            yield ch

def collect_call(chars):
    parts, part = [], ''
    for ch in chars:
        if ch == ',':
            parts.append(part)
            part = ''
        elif ch == '}':
            if part: parts.append(part)
            return parts
        else:
            part += ch
    raise Exception("Missing '}'", parts, part)

def call(parts):
    if not parts: raise Exception("Missing operator", parts)
    rator, rands = parts[0], parts[1:]
    try:             expander = expanders[rator]
    except KeyError: raise Exception("Bad call", rator, rands)
    else:            return expander(rands)

def length(args):
    if len(args) != 1: raise Exception("length: expected 1 argument", args)
    return iter(str(len(args[0])))

expanders = dict(length=length)


if __name__ == '__main__':
    main(sys.argv)
