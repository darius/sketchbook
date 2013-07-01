"""
To simplest.py we add channels and subtask calls.
"""

from collections import deque

events = deque()
def schedule(task, value): events.append((task, value))

def ready(task): schedule(task, None)
spawn = ready

def run():
    while events:
        task, value = events.popleft()
        try:
            lull = task.send(value)
        except StopIteration:
            continue
        lull(task)

def make_channel():
    tasks, values = deque(), deque()
    def put(value):
        if tasks:  schedule(tasks.popleft(), value)
        else:      values.append(value)
    def get(task):
        if values: schedule(task, values.popleft())
        else:      tasks.append(task)
    return put, get

def call(task_maker, *args, **kwargs):
    put, get = make_channel()
    spawn(task_maker(put, *args, **kwargs))
    return get
