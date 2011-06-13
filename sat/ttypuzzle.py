"""
A crude human interface for SAT solving -- I want to see if it can
make a fun puzzle game.

To play, run this file, and it shows a board with rows denoting
variables and columns denoting clauses. Unsatisfied clauses appear in
red. Each row is labeled at the left edge. To move, type a label,
which flips the chosen variable.

Hit any other key to exit.
"""

import os
import string
import sys

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

normal     = ansi.set_foreground(ansi.black) # Assuming a white background
look_at_me = ansi.set_foreground(ansi.red)

def show(coloring=False):
    "Display the board."

    def write(color, s):
        if coloring: sys.stdout.write(color)
        sys.stdout.write(s)

    def present(v, clause):
        if v in clause or -v in clause:
            true = (env[v] if v in clause else not env[v])
            return '*' if true else 'O'
        else:
            return '.'

    for v in sat.problem_variables(problem):
        write(normal, labels[v-1] + ': ')
        for clause in problem:
            write(normal if clause_is_satisfied(clause) else look_at_me,
                  present(v, clause) + ' ')
        write(chr(13), '\n')
    write(normal, '')

def clause_is_satisfied(clause):
    return any(env.get(abs(literal)) == (0 < literal)
               for literal in clause)

### show()
### flip(which('1')); show()

def refresh():
    sys.stdout.write(ansi.home)
    show(coloring=True)

def get_command():
    c = sys.stdin.read(1)
    return which(c)

def play():
    while True:
        refresh()
        if is_solved():
            print 'You win!'
            break
        v = get_command()
        if v is not None:
            flip(v)
        else:
            print 'You quit!'
            break

def game():
    os.system('stty raw')
    try:
        sys.stdout.write(ansi.clear_screen)
        play()
    finally:
        os.system('stty sane')
        print

if __name__ == '__main__':
    game()
