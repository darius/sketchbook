"""
A redesign of
http://code.activestate.com/recipes/578527-retry-loop/?in=lang-python
Its example is like example() except for this line:
    for retry in retryloop(10, timeout=30):
"""

def example():
    for retry in retrying(timeout(2, range(3))):
        try:
            print 'something'
            # time.sleep(1)   # Uncomment to test timeout
            assert False
        except AssertionError:
            retry()

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

## example()
#. something
#. something
#. something
#. 
#. Traceback (most recent call last):
#.   File "retrying.py", line 9, in example
#.     for retry in retrying(timeout(5, range(3))):
#.   File "retrying.py", line 26, in retrying
#.     raise RetryError
#. RetryError
