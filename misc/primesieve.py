# Let's try rendering the outline from
# http://en.literateprograms.org/Sieve_of_Eratosthenes_(Haskell)#Putting_it_together
# But I had to peek at their code for merge_all().
# (Could we make diff/merge shorter using Kragen's post on merging?)
# (Or how about defining diff in terms of merge and complement?)

def diff(xs, ys):
    x, y = next(xs), next(ys)
    while True:
        if x < y: yield x
        if x <= y: x = next(xs)
        else:      y = next(ys)

def merge(xs, ys):
    x, y = next(xs), next(ys)
    while True:
        d = x - y
        yield x if d <= 0 else y
        if d <= 0: x = next(xs)
        if 0 <= d: y = next(ys)

from itertools import count
from streams import LazyList

def gen_primes():
    yield 2; yield 3; yield 5
    multiples = merge_all(count(p*p, 2*p) for p in primes.tail())
    for p in diff(count(7, 2), multiples): yield p

def merge_all(iters):
    "Merge a stream of sorted streams, given map(next, iters) would be strictly increasing."
    xs = next(iters)
    yield next(xs)
    for x in merge(xs, merge_all(iters)): yield x

primes = LazyList(gen_primes())

for p in primes: print(p)
