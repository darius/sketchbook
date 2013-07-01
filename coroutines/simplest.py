"""
The simplest possible multitasking kernel.
"""

from collections import deque

ready_queue = deque()
ready = ready_queue.append

def run():
    while ready_queue:
        task = ready_queue.popleft()
        try:
            task.next()
        except StopIteration:
            continue
        ready(task)


# Example

def echoing(line, n):
    for i in range(n):
        print line
        yield

ready(echoing('Hello', 10))
ready(echoing('Goodbye', 5))
run()
