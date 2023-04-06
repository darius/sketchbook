from random import Random

def curse(seed=None):
    "A decorator for a property-test function, to exercise it."
    def accept(test):
        """Exercise test(doom) on a number of dooms, trying to find an assertion failure.
        On finding one, print the choices. Call me for effect only."""
        result = exercise(Random(seed), test)
        if result is not None:
            print_result(result)
    return accept

def print_result(trail):
    for (chooser, choice) in trail:
        print('%s: %r' % (chooser.__name__, choice))

def exercise(rng, test_fn):
    for trial in range(100):
        doom = RecordingDoom(rng)
        try:
            test_fn(doom)
        except AssertionError:
            return doom.trail
    return None

class RecordingDoom(object):
    def __init__(self, rng):
        self.cd = ChoosingDoom(rng)
        self.trail = []
    def draw(self, chooser):
        choice = chooser(self.cd)
        self.trail.append((chooser, choice))
        return choice

class ChoosingDoom(object):
    def __init__(self, rng):
        self.rng = rng
    def draw(self, chooser):
        return chooser(self)
    def draw_a_nat(self, n):
        return self.rng.randint(0, n)

def a_small_nat(doom):
    return doom.draw_a_nat(10)

def a_coinflip(percent=50):
    return lambda doom: doom.draw_a_nat(100) < percent
