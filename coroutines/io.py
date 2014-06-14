"""
Two new types of lull, readable(fd) and writable(fd). This is
incomplete because we'll need a 'choose' lull, which takes multiple
channels (ideally) or fds (if we're just trying to get a real
networking app running) and waits for one of them to be ready and
tells you which one.
"""

import select

import multitask

rfds, wfds = {}, {}

def readable(fd): return blocking(rfds, fd)
def writable(fd): return blocking(wfds, fd)

def blocking(fd_dict, fd):
    if not (rfds or wfds):
        multitask.spawn(polling())
    assert fd not in fd_dict  # Or return the existing get-facet?
    put, get = multitask.make_channel()
    fd_dict[fd] = put
    return get

def polling():
    while rfds or wfds:
        yield multitask.ready
        timeout = 0 if multitask.events else None
        r, w, e = select.select(rfds, wfds, [], timeout)
        for fd in r: rfds.pop(fd)(fd)
        for fd in w: wfds.pop(fd)(fd)
        # TODO: do something with e
