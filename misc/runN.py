#!/usr/bin/env python

# Serially for-each over arguments

import sys

args = sys.argv[1:]
i = args.index('--')
constant = args[:i]
varying  = args[i+1:]

for v in varying:
    command = constant + [v]
    print ' '.join(command)     # XXX execute it instead

# XXX have an alternative version to go in parallel
