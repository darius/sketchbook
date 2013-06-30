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
            assert False, "No go, Mo"
        except AssertionError:
            retry()

import time

def retrying(trials):
    def retry():
        retry.done = False
    for trial in trials:
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
#.     for retry in retrying(timeout(2, range(3))):
#.   File "retrying.py", line 27, in retrying
#.     raise RetryError
#. RetryError

def fancy_retrying(trials):
    def retry(exc=None):
        retry.done = False
        retry.exc = exc
    retry.exc = None
    trial = None
    for trial in trials:
        retry.done = True
        yield retry
        if retry.done: 
            return
    # All the trials failed; complain.
    info = "on trial {0}".format(trial)
    if retry.exc:
        retry.exc.args += (info,)
        raise retry.exc
    else:
        raise RetryError(info)
