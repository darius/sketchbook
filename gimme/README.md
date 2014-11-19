# Notes for a post

The simplest way to rebuild things is with a build script you rerun
every time. This is fine for lots of things.

Issues:
  * It's centralized.
  * It can do way too much work after small changes.
  * It serializes the work.
  * (minor) You need "set -e" for reliability.

Decentralizing: Scripts call scripts.

Incrementalizing: Is there a nice solution within a serial build script?
Something like

    $ if-stale goal.o 'cc -c goal.c'

if-stale could use mtime or content hashes. Could just inspect the
argument, or use something like strace on a prior run of the same
command.

Parallelizing: By hand is a pain. Best automatic using dependencies.

Decentralized *and* incremental: gimme gimme. Redoing redo.
