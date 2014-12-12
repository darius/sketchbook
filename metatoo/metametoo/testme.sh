#!/bin/sh
set -e

./meta.sh meta.meta >foo
diff -u meta.asm foo
rm foo

./meta.sh infix.meta >infix.asm
echo '(a+b)*c+d*d to c' | python meta.py infix.asm - >foo
echo ' a @ b @ + c @ * d @ d @ * + c !' >bar
diff -u foo bar
rm foo bar
