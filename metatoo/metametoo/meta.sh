#!/bin/sh
set -eu; IFS=$'\n\t'  # 'strict mode': e=errexit, u=nounset

python meta.py meta.asm "$1"
