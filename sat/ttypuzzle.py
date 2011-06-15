"""
A crude human interface for SAT solving -- I want to see if it can
make a fun puzzle game.
"""

import os
import string
import sys

import ansi
import dimacs
import sat

filenames = ['problems/trivial.dimacs',
             'problems/factoring6.dimacs',
             'problems/factoring2.dimacs',
             'problems/subsetsum_random.dimacs',
             ]

def main():
    # Some problems from http://toughsat.appspot.com/
    games = [Game(problem) for nvariables, problem  in map(dimacs.load, filenames)]
    os.system('stty raw')
    try:
        play(games)
    finally:
        os.system('stty sane')
        print

def play(games):
    game_num = 0
    while True:
        game = games[game_num]
        sys.stdout.write(ansi.clear_screen)
        while True:
            game.refresh()
            cmd = sys.stdin.read(1)
            if cmd == ' ':
                return
            elif cmd == '\t':
                game_num = (game_num + 1) % len(games)
                break
            else:
                v = game.variable_of_name(cmd)
                if v is not None:
                    game.flip(v)
                else:
                    print 'Enter <space> to quit, <tab> to try the next game.'

class Game(object):

    def __init__(self, problem):
        self.problem = problem
        variables = sat.problem_variables(problem)
        self.env = dict((v, False) for v in variables)
        self.labels = ('1234567890' + string.ascii_uppercase)[:len(variables)]

    def refresh(self):
        sys.stdout.write(ansi.home)
        self.show(coloring=True)
        sys.stdout.write(helping)
        print chr(13)
        print ('You won!' if self.is_solved() else '        ') + chr(13)
        print chr(13)
        print 'To flip a row, type its label (given on the left and right edges).' + chr(13)
        print 'Win by making every column have a * in it.' + chr(13)
        print '(Columns with no *s appear in yellow.)' + chr(13)
        print chr(13)
        print 'Hit <tab> to switch to the next game (cyclically).' + chr(13)
        print 'Hit <space> to quit.' + chr(13)

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
            write(other, self.name_of_variable(v) + ' ')
            for clause in self.problem:
                color = (satisfied if self.clause_is_satisfied(clause)
                         else unsatisfied)
                write(color, present(v, clause))
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
unsatisfied = (bg + ansi.set_foreground(ansi.bright(ansi.yellow)))

helping = (ansi.set_background(ansi.bright(ansi.white))
           + ansi.set_foreground(ansi.black))


if __name__ == '__main__':
    main()
