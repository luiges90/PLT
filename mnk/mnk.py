class MNKGame:
    def __init__(self):
        self.board = [['.' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'

    def print_board(self):
        s = ''
        for row in self.board:
            s += ''.join(row) + '\n'
        return s

    def make_move(self, row, col):
        s = ''

        if row > 2 or col > 2:
            s += f'Your move {row},{col} is invalid because it is out of bounds. Try again.\n'
            return s, False, False

        if self.board[row][col] == '.':
            self.board[row][col] = self.current_player
            if self.check_winner(row, col):
                s += f"Player {self.current_player} wins!\n"
                return s, True, True
            self.current_player = 'O' if self.current_player == 'X' else 'X'
        else:
            s += f'Your move {row},{col} is invalid because it is occupied. Try again.\n'
            return s, False, False
        return s, True, False

    def check_winner(self, row, col):
        # Check row
        if all(self.board[row][c] == self.current_player for c in range(3)):
            return True
        # Check column
        if all(self.board[r][col] == self.current_player for r in range(3)):
            return True
        # Check diagonals
        if row == col and all(self.board[i][i] == self.current_player for i in range(3)):
            return True
        if row + col == 2 and all(self.board[i][2 - i] == self.current_player for i in range(3)):
            return True
        return False

    def is_full(self):
        return all(self.board[row][col] != '.' for row in range(3) for col in range(3))
