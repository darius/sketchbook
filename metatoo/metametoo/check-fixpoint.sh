#!/bin/sh
set -eu; IFS=$'\n\t'  # 'strict mode': e=errexit, u=nounset

./meta.py $1 $2 >foo
./meta.py foo $2 >bar
diff -u foo bar
