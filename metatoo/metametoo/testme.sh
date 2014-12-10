#!/bin/sh
python metaii.py oldsyntax-metaii.asm oldsyntax-metaii.oldsyntax-metaii >foo &&
diff -u oldsyntax-metaii.asm foo &&
rm foo
