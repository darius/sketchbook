# Bayes nets

Here's a basic implementation of [Bayesian
networks](https://en.wikipedia.org/wiki/Bayesian_network). For
simplicity, it supports only binary (i.e. True/False-valued)
variables.

[bayes_prior.py](../bayes_nets/bayes_prior.py) introduces the
mechanics of representing a Bayes net in Python code, and, as an
example of computing with it, samples from the full joint
distribution.

[bayes_gibbs.py](../bayes_nets/bayes_gibbs.py) performs
inference: it estimates the conditional probability of a variable,
given that some of the other variables have some set values.

(These modules are independent of each other -- I've duplicated code
so you can read each in isolation.)

There's a diagram of the example network in figure 14.2 (page 139) of
[this collection of
figures](http://aima.cs.berkeley.edu/all-figures.pdf) from
[AIMA](http://aima.cs.berkeley.edu/index.html). (If you can view .eps
files, the figure by itself is [this
one](http://aima.cs.berkeley.edu/3e-figures/burglary2.eps).)

[probability.py](https://github.com/aimacode/aima-python/blob/master/probability.py)
in [aima-python](https://github.com/aimacode/aima-python) extends this
to exact inference by variable elimination.
