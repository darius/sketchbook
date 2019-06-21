# http://qandwhat.apps.runkite.com/i-failed-a-twitter-interview/
# (Going to assume nonnegative heights.)

def pour_volume(heights):
    return sum(max(0, min(hl, hr) - h)
               for h, hl, hr in zip(heights, 
                                    climb(heights),
                                    reversed(list(climb(list(reversed(heights)))))))

def climb(heights):
    level = 0
    for h, h1 in zip(heights, heights[1:]+[0]):
        if h1 < h: level = max(level, h)
        yield level

heights = [2, 5, 1, 2, 3, 4, 7, 7, 6]
## heights
#. [2, 5, 1, 2, 3, 4, 7, 7, 6]
## pour_volume(heights)
#. 10
