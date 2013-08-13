#!/bin/sh
# The world's crudest chat program.

# Make my pty world-writable:
chmod a+w `who am i | awk '{print $2}'`

# Send stdin to $1's pty:
cat >`who | awk '$1 == "'$1'" { print $2; exit(0) }'`
