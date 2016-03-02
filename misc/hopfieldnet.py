"""
Hopfield network.
https://en.wikipedia.org/wiki/Hopfield_network is pretty bad;
what's a better source?

Code is obviously not working.
"""

import random

class Net(object):
    def __init__(self, N):
        self.N = N
        self.s = [1] * N                     # acivations
        self.w = [[0] * N for _ in range(N)] # weights

    def batch_learn(self, vectors):
        for i in range(self.N):
            for j in range(self.N):
                if i == j:
                    self.w[i][j] = 0
                else:
                    self.w[i][j] = sum(v[i]*v[j] for v in vectors) / float(len(vectors))
        for i in range(self.N):
            for j in range(self.N):
                assert self.w[i][j] == self.w[j][i]

    def fetch(self, vector):
        self.set(vector)
        self.run()
        return self.s

    def set(self, values):
        self.s = list(values)
        assert len(self.s) == self.N
    
    def run(self):
        while True:
            prev = list(self.s)
            self.step()
            if self.s == prev: break

    def step(self):
        units = list(range(self.N))
        random.shuffle(units)
        for i in units:
            # (assuming all thresholds are 0)
            p = sum(self.w[i][j] * self.s[j] for j in range(self.N))
            self.s[i] = 1 if 0 <= p else -1

    def energy(self):
        # (leaving out threshold term, assuming they're 0)
        return -0.5 * sum(self.w[i][j] * self.s[i] * self.s[j]
                          for i in range(self.N)
                          for j in range(self.N))
    

n = Net(20)
n.set((0,1,)* 10)
print(n.energy())
n.run()
print(n.s)
print(n.energy())

n.batch_learn([(0,)*20, (0,1,1,0,)*5])
print(n.fetch((0,)*20))
print(n.fetch((0,1,1,0,)*5))
print(n.energy())
#. -0.0
#. [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#. -0.0
#. [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#. [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
#. -22.5
