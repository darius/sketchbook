"""
Chess board
No computer player yet
Sucks in other ways too
"""

## b = InitialChessBoard()
## print str(b)
#. rnbqkbnr
#. pppppppp
#.         
#.         
#.         
#.         
#. PPPPPPPP
#. RNBQKBNR
## pw = HumanPlayer(white)
## pb = HumanPlayer(black)
## b.outcome
## ' '.join(sorted(map(str, b.get_moves())))
#. 'a2-a3 a2-a4 b1-a3 b1-c3 b2-b3 b2-b4 c2-c3 c2-c4 d2-d3 d2-d4 e2-e3 e2-e4 f2-f3 f2-f4 g1-f3 g1-h3 g2-g3 g2-g4 h2-h3 h2-h4 resign'
## m = b.parse_move('resign')
## b1 = m.update(b)
## b1.outcome
#. 'black'

def main():
    print "(Moves look like 'e2-e3')"
    play_chess(HumanPlayer, HumanPlayer)

def play_chess(white_strategy, black_strategy):
    return play(InitialChessBoard(), [white_strategy, black_strategy])

def play(board, strategies):
    players = [strategy(side)
               for strategy, side in zip(strategies, board.get_sides())]
    while board.get_outcome() is None:
        board = board.play_turn(players)
    for player in players:
        player.on_game_over(board)

class HumanPlayer:

    def __init__(self, side):
        self.side = side

    def pick_move(self, board):
        board.show()
        while True:
            string = raw_input('%s, your move? ' % self.side.capitalize())
            try:
                move = board.parse_move(string)
            except MoveIllegal:
                print 'Illegal move.'
            else:
                return move

    def on_game_over(self, board):
        board.show()
        if board.get_outcome() is None:
            pass
        elif board.get_outcome() == self.side:
            print '%s, you win!' % self.side.capitalize()
        elif board.get_outcome() == 'draw':
            print 'You draw.'
        else:
            print '%s, you lose!' % self.side.capitalize()

def InitialChessBoard():
    squares = ['----------',
               '-rnbqkbnr-',
               '-pppppppp-',
               '-        -',
               '-        -',
               '-        -',
               '-        -',
               '-PPPPPPPP-',
               '-RNBQKBNR-',
               '----------',]
    return ChessBoard(white, squares, (False, False), None)

class MoveIllegal(Exception):
    pass

class ChessBoard:

    def __init__(self, mover, squares, castled, outcome):
        self.mover = mover
        self.squares = squares
        self.castled = castled
        self.outcome = outcome

    def __str__(self):
        return '\n'.join(line[1:-1] for line in self.squares[1:-1])

    def has_castled(self, player):
        return self.castled[player == black]

    def get_outcome(self):
        "Return None, 'draw', black, or white (meaning the winner)."
        return self.outcome

    def resign(self):
        return ChessBoard(opponent(self.mover),
                          self.squares,
                          self.castled,
                          opponent(self.mover))

    def move_piece(self, (r0, c0), (r1, c1)):
        squares = list(map(list, self.squares))
        piece = squares[r0][c0]
        squares[r0][c0] = ' '
        squares[r1][c1] = piece
        return ChessBoard(opponent(self.mover),
                          list(map(''.join, squares)),
                          self.castled,
                          None) # XXX check for checkmate or draw

    def show(self):
        print self

    def get_sides(self):
        return (white, black)

    def play_turn(self, (white_player, black_player)):
        player = white_player if self.mover == white else black_player
        move = player.pick_move(self)
        if move in self.get_moves():
            return move.update(self)
        raise Exception("Bad move")

    def parse_move(self, string):
        for move in self.get_moves():
            if move.matches(string):
                return move
        raise MoveIllegal()

    def get_moves(self):
        return [ResignMove()] + self.get_piece_moves()

    def get_piece_moves(self):
        return sum(map(self.moves_from, self.army(self.mover)), [])

    def army(self, player):
        for r, row in enumerate(self.squares):
            for c, piece in enumerate(row):
                if piece.isalpha() and piece.isupper() == (player == white):
                    yield r, c

    def moves_from(self, pos):
        return list(self.gen_moves_from(pos))

    def gen_moves_from(self, (r, c)):
        piece = self.squares[r][c]
        piece, white = piece.upper(), piece.isupper()

        def is_takeable(r1, c1):
            return is_empty(r1, c1) or has_opponent(r1, c1)

        def is_empty(r1, c1):
            return self.squares[r1][c1] == ' '

        def has_opponent(r1, c1):
            there = self.squares[r1][c1]
            return there.isalpha() and there.isupper() != white

        def move_to(r1, c1):
            return PieceMove((r, c), (r1, c1))

        def move_freely(dirs):
            for dr, dc in dirs:
                for i in range(1, 9):
                    if is_empty(r+dr*i, c+dc*i):
                        yield move_to(r+dr*i, c+dc*i)
                    else:
                        if has_opponent(r+dr*i, c+dc*i):
                            yield move_to(r+dr*i, c+dc*i)
                        break

        if piece in ' -':
            pass
        elif piece == 'P':
            # TODO: pawn promotion
            # TODO: en passant
            forward = -1 if white else 1
            if is_empty(r+forward, c):
                yield move_to(r+forward, c)
                if r == (7 if white else 2): # initial 2 steps
                    if is_empty(r+forward*2, c): yield move_to(r+forward*2, c)
            if has_opponent(r+forward, c-1): yield move_to(r+forward, c-1)
            if has_opponent(r+forward, c+1): yield move_to(r+forward, c+1)
        elif piece == 'K':
            # TODO castling
            # TODO forbid moving into check
            # (and this can apply to moves of other pieces)
            for dr, dc in queen_dirs:
                if is_takeable(r+dr, c+dc):
                    yield move_to(r+dr, c+dc)
        elif piece == 'Q':
            for move in move_freely(queen_dirs):  yield move
        elif piece == 'R':
            for move in move_freely(rook_dirs):   yield move
        elif piece == 'B':
            for move in move_freely(bishop_dirs): yield move
        elif piece == 'N':
            for dr, dc in knight_jumps:
                if 1 <= r+dr <= 8 and 1 <= c+dc <= 8:
                    if is_takeable(r+dr, c+dc):
                        yield move_to(r+dr, c+dc)
        else:
            assert False

rook_dirs   = [( 0, 1), ( 0,-1), ( 1, 0), (-1, 0)]
bishop_dirs = [(-1,-1), (-1, 1), ( 1,-1), ( 1, 1)]
queen_dirs  = rook_dirs + bishop_dirs

knight_jumps = [( 2, 1), ( 2,-1), ( 1, 2), ( 1,-2),
                (-2, 1), (-2,-1), (-1, 2), (-1,-2)]

white, black = 'white', 'black'

def opponent(side):
    return black if side == white else white

class ResignMove:
    def __eq__(self, other):
        return isinstance(other, ResignMove)
    def update(self, board):
        return board.resign()
    def matches(self, string):
        return string.lower() == 'resign'
    def matches(self, string):
        return string.lower() == str(self)
    def __str__(self):
        return 'resign'

class PieceMove:
    def __init__(self, from_pos, to_pos):
        self.from_pos = from_pos
        self.to_pos   = to_pos
    def __eq__(self, other):
        return (isinstance(other, PieceMove)
                and self.from_pos == other.from_pos
                and self.to_pos == other.to_pos)
    def update(self, board):
        return board.move_piece(self.from_pos, self.to_pos)
    def matches(self, string):
        return string.lower() == str(self)
    def __str__(self):
        # XXX 'a' is top of board for Black?
        fr, fc = self.from_pos
        tr, tc = self.to_pos
        return '%s%d-%s%d' % ('abcdefgh'[fc-1], 9-fr,
                              'abcdefgh'[tc-1], 9-tr)

if __name__ == '__main__':
    main()
