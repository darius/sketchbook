"""
Hopfield network.
http://www.comp.leeds.ac.uk/ai23/reading/Hopfield.pdf
(https://en.wikipedia.org/wiki/Hopfield_network is pretty bad)
"""

import random

class Net(object):
    def __init__(self, N):
        self.N = N
        self.x = [1] * N                     # acivations
        self.w = [[0] * N for _ in range(N)] # weights

    def batch_learn(self, vectors):
        for i in range(self.N):
            for j in range(self.N):
                if i == j:
                    self.w[i][j] = 0
                else:
                    self.w[i][j] = sum(v[i]*v[j] for v in vectors) / float(self.N)
        for i in range(self.N):
            for j in range(self.N):
                assert self.w[i][j] == self.w[j][i]

    def fetch(self, vector):
        self.set(vector)
        self.run()
        return self.x

    def set(self, values):
        self.x = list(values)
        assert len(self.x) == self.N
    
    def run(self):
        while True:
            prev = list(self.x)
            self.step()
            if self.x == prev: break

    def step(self):
        units = list(range(self.N))
        random.shuffle(units)
        for i in units:
            p = sum(self.w[i][j] * self.x[j] for j in range(self.N))
            self.x[i] = 1 if 0 <= p else -1

    def energy(self):
        return -0.5 * sum(self.w[i][j] * self.x[i] * self.x[j]
                          for i in range(self.N)
                          for j in range(self.N))
    

## n = Net(20)
## n.set((0,1,)* 10)
## n.energy()
#. -0.0
## n.run()
## n.x
#. [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
## n.energy()
#. -0.0

## n.batch_learn([(0,)*20, (0,1,1,0,)*5])
## n.fetch((0,)*20)
#. [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
## n.fetch((0,1,1,0,)*5)
#. [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
## n.energy()
#. -2.249999999999996

## t = Net(2)
## t.w = [[0,-1],[-1,0]]
## t.x
#. [1, 1]
## t.run()
## t.x
#. [1, -1]

## u = Net(4)
## u.batch_learn([[1,-1,1,1]])
## u.fetch([-1,-1,-1,-1])
#. [-1, 1, -1, -1]
## u.fetch([1,1,1,1])
#. [1, -1, 1, 1]
