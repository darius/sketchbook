This started as a faithful implementation of Schorre's VM, starting
with Simon Forman's code at
http://comments.gmane.org/gmane.comp.lang.smalltalk.fonc/3642

There were some minor bugs in that code: erroring on trying to match
tokens at the end-of-input.

There was a bug in the compiler/VM design. Consider this grammar:

    THING = FAILURE | .OUT('hey') | .OUT('should not happen') .,
    FAILURE = 'a rule I expect to fail' .,

Trying to match THING writes *both* 'hey' and 'should not happen'.

Schorre's compiler handles output expressions separately from other
primary expressions, because they always succeed and hence needn't be
followed by a test for failure. But there are a couple of other
expression types with the same property. The new compiler takes
advantage of these and also fixes the above bug, at the cost of making
the output instructions set the success flag (which Schorre's VM did
not bother doing).

(At first I tried to do this optimization without making the
instructions set the flag, and spent no-kidding hours chasing a
bug. This was when I added tracing, though actually it might've been
more helpful to have added an ASSERT-WIN instruction in appropriate
places (with identical behavior to WIN-OR-DIE, but meant to check that
the *assembly* is correct, whereas WIN-OR-DIE is for reporting syntax
errors in the input). Anyway, with context-free code generation it
just didn't work out as significantly smaller unless everything
touches the success flag.)

Various other aspects got modernized or streamlined along the way.
