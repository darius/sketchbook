#!/bin/sh
python metaii.py oldsyntax-metaii.asm metaii.oldsyntax-metaii |
python metaii.py - metaii.metaii |
python metaii.py - metaii.metaii >metaii.asm &&

python metaii.py metaii.asm metaii.metaii >foo &&
diff -u metaii.asm foo &&
rm foo
