#!/bin/sh
./metaii.sh metaii.metaii >foo &&
diff -u metaii.asm foo &&
rm foo
