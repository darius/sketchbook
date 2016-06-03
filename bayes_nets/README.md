# Bayes nets

Here's a basic implementation of [Bayesian
networks](https://en.wikipedia.org/wiki/Bayesian_network). For
simplicity, it supports only binary (i.e. True/False-valued)
variables.

[bayes_prior.py](../bayes_nets/bayes_prior.py) introduces the
mechanics of representing a Bayes net in Python code, and, as an
example of computing with it, samples from the full joint
distribution.

[bayes_gibbs.py](../bayes_nets/bayes_gibbs.py) does inference: it
estimates the conditional probability of a variable, given that some
of the other variables have some set values.

(These modules are independent of each other -- I've duplicated code
so you can read each in isolation.)

There's a diagram of the example network in figure 14.2 (page 139) of
[this collection of
figures](http://aima.cs.berkeley.edu/all-figures.pdf) from
[AIMA](http://aima.cs.berkeley.edu/index.html). (If you can view .eps
files, the figure by itself is [this
one](http://aima.cs.berkeley.edu/3e-figures/burglary2.eps).)

## To learn more

[probability.py](https://github.com/aimacode/aima-python/blob/master/probability.py)
in [aima-python](https://github.com/aimacode/aima-python) extends this
to exact inference by variable elimination. (Also it adds a `BayesNet`
class so you're not limited to just one network, and covers some other
topics from the same chapter of AIMA.)

Generalizing to n-way discrete variables is straightforward. I haven't
dealt with continuous variables so far; see Gwern below for an example
of that.

There's a Coursera course on [probabilistic graphical
models](https://www.coursera.org/course/pgm) and the course textbook
is in the RC library. (At the moment I have it checked out.)

Here's an example of [Gwern analyzing some real
data](https://www.gwern.net/Statistical%20notes#bayes-nets) with Bayes
nets.
