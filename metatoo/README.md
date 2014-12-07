This is meant to be approximately a reconstruction of META II in
Python, but might turn out different: I'm only going to check against
the original after I'm done.

I bootstrapped it using Peglet (`pip install peglet` and then `python
bootstrap.py >metatoo.py`) but you can just use the
already-bootstrapped `metatoo.py` checked in here if you prefer.

To rebuild after editing `metatoo.metatoo`: run `build.sh`, test that
`newmetatoo.py` works as desired, then `mv newmetatoo.py metatoo.py`
to replace the old version.

This could surely be either simpler or more useful, and maybe
both. I'm just checking it in as soon as it can compile itself.
