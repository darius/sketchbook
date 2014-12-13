#!/bin/sh
set -e

./meta.py $1 $2 >foo
./meta.py foo $2 >bar
diff -u foo bar
