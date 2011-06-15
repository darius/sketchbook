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

def main():
    # Problem from http://toughsat.appspot.com/
    nvariables, problem = dimacs.load('problems/factoring6.dimacs')
    os.system('stty raw')
    try:
        play(Game(problem))
    finally:
        os.system('stty sane')
        print

def play(game):
    sys.stdout.write(ansi.clear_screen)
    while True:
        game.refresh()
        if game.is_solved():
            print 'You win!'
            break
        cmd = sys.stdin.read(1)
        v = game.variable_of_name(cmd)
        if v is not None:
            game.flip(v)
        else:
            print 'You quit!'
            break

class Game(object):

    def __init__(self, problem):
        self.problem = problem
        variables = sat.problem_variables(problem)
        self.env = dict((v, False) for v in variables)
        self.labels = ('1234567890' + string.ascii_uppercase)[:len(variables)]

    def refresh(self):
        sys.stdout.write(ansi.home)
        self.show(coloring=True)

    def show(self, coloring=False):
        "Display the board."

        def write(color, s):
            if coloring: sys.stdout.write(color)
            sys.stdout.write(s)

        def present(v, clause):
            if v in clause or -v in clause:
                true = (self.env[v] if v in clause else not self.env[v])
                return '*' if true else 'O'
            else:
                return '.'

        for v in sat.problem_variables(self.problem):
            write(other, self.name_of_variable(v))
            for clause in self.problem:
                color = (satisfied if self.clause_is_satisfied(clause)
                         else unsatisfied)
                write(color, ' ' + present(v, clause))
            write(other, ' ' + self.name_of_variable(v))
            write(chr(13), '\n')
        write(other, '')

    def name_of_variable(self, v):
        return self.labels[v-1]

    def variable_of_name(self, label):
        try:
            return self.labels.index(label.upper()) + 1
        except ValueError:
            return None

    def is_solved(self):
        return sat.is_satisfied(self.problem, self.env)

    def clause_is_satisfied(self, clause):
        return any(self.env.get(abs(literal)) == (0 < literal)
                   for literal in clause)

    def flip(self, v):
        self.env[v] = not self.env[v]


bg = ansi.set_background(ansi.black)

other       = (bg + ansi.set_foreground(ansi.white))
satisfied   = (bg + ansi.set_foreground(ansi.blue))
unsatisfied = (bg + ansi.set_foreground(ansi.yellow))


if __name__ == '__main__':
    main()
