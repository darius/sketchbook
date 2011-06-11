"""
A crude human interface for SAT solving -- I want to see if it can
make a fun puzzle game.

To play, run this file, and it shows a board with rows denoting
variables and columns denoting clauses. Unsatisfied clauses appear in
red. Each row is labeled at the left edge. To move, type a label and
hit enter, which flips the chosen variable.

Exit with control-C if you get sick of it.
"""

import string

import ansi
import dimacs
import sat

# Problem from http://toughsat.appspot.com/
nvariables, problem = dimacs.load('factoring.dimacs')

# Make sure it's solvable, and visible in a terminal window:
## import indexedsat as solver
## solver.solve(problem) is not None
#. True
## nvariables <= 25
#. True
## len(problem) < 39
#. True

env = dict((v, False) for v in sat.problem_variables(problem))

def is_solved():
    return sat.is_satisfied(problem, env)

def flip(v):
    env[v] = not env[v]

labels = ('1234567890' + string.ascii_uppercase)[:nvariables]

def which(c):
    "Return the variable labeled by c, or None."
    c = c[0].upper()
    try:
        return labels.index(c) + 1
    except ValueError:
        return None

normal     = ansi.set_foreground(ansi.black)
look_at_me = ansi.set_foreground(ansi.red)

def show(coloring=False):
    "Display the board."
    for v in sat.problem_variables(problem):
        print labels[v-1] + ':',
        x = env[v]
        for clause in problem:
            color = (normal if clause_is_satisfied(clause) else look_at_me)
            c = '.'
            if v in clause or -v in clause:
                true = (x if v in clause else not x)
                c = '*' if true else 'O'
            if coloring: print color + c,
            else: print c,
        print

def clause_is_satisfied(clause):
    return any(env.get(abs(literal)) == (0 < literal)
               for literal in clause)

### show()
### flip(which('1')); show()

def play():
    print(ansi.clear_screen)
    show(coloring=True)
    while not is_solved():
        c = raw_input()
        v = which(c)
        if v is not None:
            flip(v)
        print(ansi.home)
        show(coloring=True)
    print 'You win!'

if __name__ == '__main__':
    play()
