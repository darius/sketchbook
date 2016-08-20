""""
https://en.wikipedia.org/wiki/Two_envelopes_problem
Not that there's any doubt what the program below will answer;
but I've written it out so we can ask "Just how does the specious
argument misdescribe the program?"
"""
from __future__ import division

# There are two equally-probable worlds, each with two money-stuffed envelopes.
setups = ((1,2),  # In one world you get the envelope holding $1, and not the $2 one.
          (2,1))  # In the other, it's the other way around.
# We could add more envelopes in pairs, like (2,4),(4,2), but I won't bother.

# The expectation value of opening the first envelope, the one you were given.
stay   = sum(envelope[0] for envelope in setups) / len(setups)

# The expectation value of switching to the other envelope.
switch = sum(envelope[1] for envelope in setups) / len(setups)

## stay, switch
#. (1.5, 1.5)

"""From Wikipedia:

I denote by A the amount in my selected envelope.

The probability that A is the smaller amount is 1/2, and that it is
the larger amount is also 1/2.

The other envelope may contain either 2A or A/2.

If A is the smaller amount, then the other envelope contains 2A.

If A is the larger amount, then the other envelope contains A/2.

Thus the other envelope contains 2A with probability 1/2 and A/2 with
probability 1/2.

So the expected value of the money in the other envelope is

   (1/2)(2A) + (1/2)(A/2) = (5/4)A

This is greater than A, so I gain on average by swapping.
"""

"""
My response: if we interpret A as a random variable -- that is, a
function of the setup:

def A(envelopes): return envelopes[0]

-- then the above is all right until "the expected value of the money
in the other envelope". It combines two different worlds where A takes
different values, erroneously treating A as constant across worlds. It
seems we need to be careful talking in terms of random variables,
where we treat the sample space as implicit context and pretend we're
talking about simple values instead of functions on the sample space.
Since the expectation value sums over the space, that implicit context
varies for each term. We can correct the formula while retaining its
form, by making the context explicit again:
"""
def A(envelopes): return envelopes[0]
corrected = (1/2)*(2*A(setups[0])) + (1/2)*(A(setups[1])/2)
## corrected
#. 1.5

"""
OK, https://en.wikipedia.org/wiki/Two_envelopes_problem#Simple_resolutions
says something similar, except it takes A to mean the expectation value of
the given envelope, which never occurred to me, and to me seems artificial.

Wow, deep waters in the rest of that page.
"""
