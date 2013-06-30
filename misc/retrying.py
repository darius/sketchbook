"""
A redesign of
http://code.activestate.com/recipes/578527-retry-loop/?in=lang-python
"""

import time

def retrying(trials):
    def retry(): retry.done = False
    for _ in trials:
        retry.done = True
        yield retry
        if retry.done: 
            return
    raise RetryError

class RetryError(Exception): pass

def timeout(interval, trials):
    deadline = time.time() + interval
    for trial in trials:
        yield trial
        if deadline <= time.time(): break

def eg():
    for retry in retrying(timeout(30, range(3))):
        try:
            print 'something'
            assert False
        except AssertionError:
            retry()

"""
Example from above link is equivalent except this line:
for retry in retryloop(10, timeout=30):
"""

## eg()
#. something
#. something
#. something
#. 
#. Traceback (most recent call last):
#.   File "retryloop.py", line 26, in eg
#.     for retry in retrying(timeout(30, range(3))):
#.   File "retryloop.py", line 15, in retrying
#.     raise RetryError
#. RetryError
