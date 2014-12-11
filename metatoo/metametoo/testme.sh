#!/bin/sh
set -e

./metaii.sh metaii.metaii >foo
diff -u metaii.asm foo
rm foo

./metaii.sh infix.metaii >infix.asm
echo '(a+b)*c+d*d to c' | python metaii.py infix.asm - >foo
echo ' a @ b @ + c @ * d @ d @ * + c !' >bar
diff -u foo bar
rm foo bar
