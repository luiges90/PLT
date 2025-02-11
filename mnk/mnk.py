from ollama import Client
import re
import time

class TicTacToe:
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

class Printer:
    pass
    # This class print messages to both console and file

def run_single_game(models):
    client1 = Client(
      host='http://localhost:11434',
    )
    client2 = Client(
      host='http://localhost:11434'
    )
    clients = [client1, client2]

    # Game loop
    game = TicTacToe()
    game_over = False

    # Setup
    intro_message = 'Here is a Tic Tac Toe game. '

    retries = 0
    player = 0
    stats = [{
        "wins": 0, "loses": 0, "draws": 0, "errors": 0, "forfeits": 0, "other_forfeits": 0, "time": 0,
    }, {
        "wins": 0, "loses": 0, "draws": 0, "errors": 0, "forfeits": 0, "other_forfeits": 0, "time": 0,
    }]
    message = intro_message + 'You play as X.\n'
    while not game_over:
        if player == 1:
            other = 0
        else:
            other = 1

        if retries > 5:
            print(f"System: Model {player} {models[player]} is unable to make a valid move after 5 tries. Aborting.")
            stats[other]["other_forfeits"] += 1
            stats[player]["forfeits"] += 1
            break
        retries += 1

        # Compose message
        message += game.print_board()
        message += 'Place your move as row and column index, 0-based. e.g. Top-right corner is 0,2'

        # Ask LLM
        print(f"System: Asking Model {player} {models[player]}: \n<prompt>\n{message}\n</prompt>\n")
        time_start = time.time()
        stream = clients[player].chat(model=models[player], stream=True, messages=[
            {
                'role': 'user',
                'content': message,
            },
        ])

        # Receive answer from LLM
        print('System: receiving answer...\n<answer>\n')
        answer = ''
        for chunk in stream:
            answer_chunk = chunk['message']['content']
            answer += answer_chunk
            print(answer_chunk, end='', flush=True)
        print('\n</answer>\n')
        time_end = time.time()
        stats[player]["time"] += time_end - time_start
        print('System: Time taken: ', time_end - time_start)

        # Interpret answer
        matches = re.findall(r'(\d)\s*,\s*(\d)', answer)
        if not matches:
            print('System: Unable to interpret move from the answer.')
            message = f'Unable to interpret your move from your answer. Try again.\n'
            stats[player]["errors"] += 1
            continue
        row, col = matches[-1]
        row = int(row)
        col = int(col)
        print(f'System: interpreted answer as move ({row}, {col})')

        # Make move
        message, valid, won = game.make_move(row, col)
        if not valid:
            stats[player]["errors"] += 1
            continue
        if won:
            stats[player]["wins"] += 1
            stats[other]["loses"] += 1
            break
        if game.is_full():
            message = "The game is a draw!" + '\n'
            stats[player]["draws"] += 1
            stats[other]["draws"] += 1
            break

        # Switch player
        retries = 0
        if player == 0:
            player = 1
            message += intro_message + 'You play as O.\n'
        else:
            player = 0
            message += intro_message + 'You play as X.\n'

    print('System: Game ended.')
    print(message)
    print(game.print_board())

    return stats

# main
models = ['qwen2.5', 'qwen', 'gemma', 'llama3', 'llama3.1', 'phi4', 'qwen', 'mistral', 'llama3.2', 'deepseek-r1']
stats = [{
    "wins": 0, "loses": 0, "draws": 0, "errors": 0, "forfeits": 0, "other_forfeits": 0, "time": 0,
}] * len(models)
for c in range(0, 1):
    for i in range(0, len(models)):
        for j in range(0, len(models)):
            if i == j:
                continue
            print(f"League System: Starting game {models[i]} vs. {models[j]}")
            round_stat = run_single_game([models[i], models[j]])

            stats[i] = {k: stats[i][k] + round_stat[0][k] for k in stats[i]}
            stats[j] = {k: stats[j][k] + round_stat[1][k] for k in stats[j]}

            print("Current tally:")
            print(f"Model {models[i]}:\n{stats[i]}")
            print(f"Model {models[j]}:\n{stats[j]}")

print("****************************************************************")
print("League concluded.")
for i in range(0, len(models)):
    print(f"Model {models[i]}:\n{stats[i]}")
