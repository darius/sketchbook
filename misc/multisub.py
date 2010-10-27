"""
In the common idiom of doing multiple parallel string replacements by
repeated re.sub or string.replace, the replacements can interfere with
each other. This avoids the problem. It also works in one pass.
"""

import re

def multisub(subs, subject):
    "Simultaneously perform all substitutions on the subject string."
    pattern = '|'.join('(%s)' % re.escape(p) for p, s in subs)
    substs = [s for p, s in subs]
    replace = lambda m: substs[m.lastindex - 1]
    return re.sub(pattern, replace, subject)

## multisub([('hi', 'bye'), ('bye', 'hi')], 'hi and bye')
#. 'bye and hi'
