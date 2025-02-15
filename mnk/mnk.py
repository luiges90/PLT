import re

from shared import MoveResponse

class MNKGame:
    def __init__(self):
        self.board = [['.' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'

    def make_message(self):
        message = f'Here is a Tic Tac Toe game. You play as {self.current_player}\n'
        message += self.print_board()
        message += 'Place your move as row and column index, 0-based. e.g. Top-right corner is 0,2\n'
        return message

    def print_board(self):
        s = ''
        for row in self.board:
            s += ''.join(row) + '\n'
        return s

    def make_move(self, answer):
        matches = re.findall(r'(\d)\s*,\s*(\d)', answer)
        if not matches:
            message = f'Unable to interpret your move from your answer. Try again.\n'
            return '', message, MoveResponse.INVALID

        row, col = matches[-1]
        row = int(row)
        col = int(col)
        sys_message = f'System: interpreted answer as move ({row}, {col})\n'

        if row > 2 or col > 2:
            message = f'Your move {row},{col} is invalid because it is out of bounds. Try again.\n'
            return sys_message, message, MoveResponse.INVALID

        if self.board[row][col] == '.':
            self.board[row][col] = self.current_player
            if self.check_winner(row, col):
                message = f"Player {self.current_player} wins!\n"
                return sys_message, message, MoveResponse.WIN
            self.current_player = 'O' if self.current_player == 'X' else 'X'
        else:
            message = f'Your move {row},{col} is invalid because it is occupied. Try again.\n'
            return sys_message, message, MoveResponse.INVALID

        if self.is_full():
            message = f"The game is a draw!" + '\n'
            return sys_message, message, MoveResponse.DRAW

        return sys_message, '', MoveResponse.VALID

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
