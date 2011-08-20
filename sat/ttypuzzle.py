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

# Some problems from http://toughsat.appspot.com/
filenames = ['problems/trivial.dimacs',
             'problems/factoring6.dimacs',
             'problems/factoring2.dimacs',
             'problems/subsetsum_random.dimacs',
             ]

def main():
    games = [Game(problem) for nvariables, problem in map(dimacs.load,
                                                          filenames)]
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
            print '\r'
            print 'Hit <tab> to cycle to the next game.\r'
            print 'Hit <space> to quit.\r'
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

class Game(object):

    def __init__(self, problem):
        self.problem = problem
        variables = sat.problem_variables(problem)
        self.env = dict((v, False) for v in variables)
        self.labels = ('1234567890' + string.ascii_uppercase)[:len(variables)]

    def refresh(self):
        sys.stdout.write(ansi.home)
        self.show(coloring=True)
        set_color(helping)
        print '\r'
        print ('You won!' if self.is_solved() else '        ') + '\r'
        print '\r'
        print 'To flip a row, type its label (given on the left and right edges).\r'
        print 'Win by making every column have a * in it.\r'
        print '(Columns with no *s appear in yellow.)\r'

    def show(self, coloring=False):
        "Display the board."

        def write(color, s):
            if coloring: set_color(color)
            sys.stdout.write(s)

        def present(v, clause):
            color = (satisfied if self.clause_is_satisfied(clause) else unsatisfied)
            pos, neg = v in clause, -v in clause
            if not pos and not neg:
                write(color, '.')
            elif self.env[v] is None:
                write(color, 'O*'[pos])
            else:
                write(color, 'O*'[self.env[v] == pos])

        for v in sat.problem_variables(self.problem):
            write(other, self.name_of_variable(v) + ' ')
            for clause in self.problem:
                present(v, clause)
            write(other, ' ' + self.name_of_variable(v))
            write(other, '\r\n')
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


bg = ansi.black

other       = (bg, ansi.bright(ansi.white))

satisfied   = (bg, ansi.blue)
unsatisfied = (bg, ansi.bright(ansi.yellow))
#unsatisfied = (bg, ansi.yellow)

def set_color((bg, fg)):
    sys.stdout.write(ansi.set_background(bg))
    sys.stdout.write(ansi.set_foreground(fg))

helping = (ansi.bright(ansi.white), ansi.black)


if __name__ == '__main__':
    main()
