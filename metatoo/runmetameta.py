"""
Compile the metatoo grammar using the metatoo compiler; the result
is a new metatoo compiler on stdout.
"""

import metatoo, sys
with open('metatoo.metatoo') as f:
    sys.stdout.write(''.join(metatoo.meta(f.read())))
