# Bayes nets

Here's a basic implementation of [Bayesian
networks](https://en.wikipedia.org/wiki/Bayesian_network). To keep it
as simple as possible, we support only binary variables -- that is,
their domain is {True, False}.

bayes_prior.py introduces the mechanics of representing a Bayes net in
Python code, and as an example of computing with it, samples from the
full joint distribution.

bayes_gibbs.py performs inference: it estimates the conditional
probability of a variable, given that some of the other variables have
some set values.

(These modules are independent of each other -- I've duplicated code
so you can read each in isolation.)
