# Now with really basic shrinking

from random import Random

# now the top-level dooms are always Recording; they use a choice of either rng- or replay-based subdooms.

# TODO terminology for trail, trial

def curse(seed=None):
    "A decorator for a property-test function, to exercise it."
    def accept(test_fn):
        """Exercise test(doom) on a number of dooms, trying to find an assertion failure.
        On finding one, try to shrink it; then print the choices. Call me for effect only."""
        print("\nExercising %s" % test_fn.__name__)
        opt_doom = exercise(Random(seed), test_fn)
        if opt_doom:
            print("Found a doom")
            doom = shrink(opt_doom, test_fn)
            doom.print_choices()
    return accept

def exercise(rng, test_fn):
    for trial in range(100):
        doom = RecordingDoom(ChoosingDoom(rng))
        if do_trial(doom, test_fn):
            return doom
    return None

def do_trial(doom, test_fn):
    try:
        test_fn(doom)
    except AssertionError, e:
#        print("assertion error: lose")
        return True
    except Overrun:
#        print("overrun")
        return False     # TODO assert this can't happen in the exercise() phase
    else:
#        print("win")
        return False

def shrink(losing_doom, test_fn):
    best = losing_doom.make_replay()
    best.trail = losing_doom.trail   # TODO ugh this code man
    
    while True:
        progress = False
        print 'shrink loop iteration', best.cd.nats
        for new_doom in best.gen_mutants():
            if do_trial(new_doom, test_fn):
                best = new_doom
                progress = True
                break
        if not progress:
            break

    return best

class Doom(object):
    def draw(self, chooser):
        return chooser(self)
    def draw_a_nat(self, n):
        raise Exception("Use a doom.draw(a_nat) instead")

class RecordingDoom(Doom):
    def __init__(self, subdoom):
        self.cd = subdoom
        self.trail = []
        
    def draw(self, chooser):
        choice = chooser(self.cd)
        self.trail.append((chooser, choice))
        return choice

    def make_replay(self):
        return RecordingDoom(ReplayDoom(tuple(self.cd.nats)))    # TODO reaching into innards, assumes .cd is a ChoosingDoom?

    def gen_mutants(self):
        # TODO this assumes the subdoom is a replaydoom
        nats = self.cd.nats
        for i in range(len(nats)-1, max(0, len(nats)-8), -1):

            # Try to delete a nat at i
            new_nats = nats[:i-1] + nats[i+1:]
            yield RecordingDoom(ReplayDoom(new_nats))

            # Try to zero a nat at i
            last_nat = nats[i]
            if 0 < last_nat:
                new_nats = nats[:i-1] + (0,) + nats[i+1:]
                yield ReplayDoom(new_nats)

            # Try to decrement a nat at i
            while 1 < last_nat:
                last_nat -= 1
                new_nats = nats[:i-1] + (last_nat,) + nats[i+1:]
                yield ReplayDoom(new_nats)

    def print_choices(self):
        for (chooser, choice) in self.trail:
            print('%s: %r' % (chooser.__name__, choice))
        if not self.trail:
            print("No choices")

class ChoosingDoom(Doom):
    def __init__(self, rng):
        self.rng = rng
        self.nats = []
    def draw_a_nat(self, n):
        self.nats.append(self.rng.randint(0, n))
        return self.nats[-1]

class ReplayDoom(Doom):
    def __init__(self, trail):
        self.nats = tuple(trail)
        self.fate = list(trail)
        self.fate.reverse()   # for efficient pop()
    def draw_a_nat(self, n):
        if not self.fate: raise Overrun()
        nat = self.fate.pop()
        if n <= nat:
            # XXX different exception, or rename. Doesn't matter because it wouldn't really come up in the fancier impl
            raise Overrun()
        return nat

class Overrun(Exception): pass

def a_small_nat(doom):
    return doom.draw_a_nat(10)

def a_coinflip(percent=50):
    return lambda doom: doom.draw_a_nat(100) < percent
