"""
https://en.wikipedia.org/wiki/Hex_%28board_game%29
XXX untested
"""

def play(player1, player2, n):
    assert 1 < n
    board = {}
    move = player1(board, n, 'v')
    board[move] = 'v'
    move = player2(board, n, '?')
    if move == 'swap':
        player1, player2 = player2, player1
        move = player2(board, n, 'h')
    board[move] = 'h'
    p_, p_mark, q, q_mark = player1, 'v', player2, 'h'
    while True:
        board[player1(board, n, 'v')] = 'v'
        if connected_vertically(board, n): return player1
        board[player2(board, n, 'h')] = 'h'
        if connected_horizontally(board, n): return player2

def connected_vertically(board, n):
    return connected(board, n, 'v', set(),
                     {(x, n) for x in range(n)},
                     {(x, 0) for x in range(n)})

def connected_horizontally(board, n):
    return connected(board, n, 'h', set(),
                     {(n, x) for x in range(n)},
                     {(0, x) for x in range(n)})

def connected(board, n, mark, seen, frontier, goal):
    while frontier:
        square = frontier.pop()
        if square in seen: continue
        seen.add(square)
        if square in goal: return True
        for neighbor in connected_neighbors(board, n, mark, square):
            if neighbor not in seen:
                frontier.add(neighbor)
    return False

def connected_neighbors(board, n, mark, (x, y)):
    for nx, ny in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
        if (board.get((nx, ny)) == mark
            or (nx in (0, n) and mark == 'v')
            or (ny in (0, n) and mark == 'h')):
                yield nx, ny
