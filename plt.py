from ollama import Client
import time
from datetime import datetime

from mnk.mnk import MNKGame
from shared import MoveResponse


class Printer:
    def __init__(self, prefix):
        formatted_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.file_path = f'{prefix}_{formatted_time}.log'
        self.file = open(self.file_path, 'w', encoding='utf-8')

    def print(self, message, end='\n', flush=False):
        print(message, end=end, flush=flush)
        self.file.write(f'{message}{end}')
        self.file.flush()

    def __del__(self):
        self.file.close()

def run_single_game(models, printer):
    game = MNKGame()

    client1 = Client(
      host='http://localhost:11434',
    )
    client2 = Client(
      host='http://localhost:11434'
    )
    clients = [client1, client2]

    # Setup
    retries = 0
    player = 0
    stats = [{
        "wins": 0, "loses": 0, "draws": 0, "errors": 0, "forfeits": 0, "other_forfeits": 0, "time": 0,
    }, {
        "wins": 0, "loses": 0, "draws": 0, "errors": 0, "forfeits": 0, "other_forfeits": 0, "time": 0,
    }]
    while True:
        if player == 1:
            other = 0
        else:
            other = 1

        if retries > 5:
            printer.print(f"System: Model {player} {models[player]} is unable to make a valid move after 5 tries. Aborting.")
            stats[other]["other_forfeits"] += 1
            stats[player]["forfeits"] += 1
            break
        retries += 1

        # Compose message
        message = game.make_message()

        # Ask LLM
        printer.print(f"System: Asking Model {player} {models[player]}: \n<prompt>\n{message}\n</prompt>\n")
        time_start = time.time()
        stream = clients[player].chat(model=models[player], stream=True, messages=[
            {
                'role': 'user',
                'content': message,
            },
        ])

        # Receive answer from LLM
        printer.print('System: receiving answer...\n<answer>')
        answer = ''
        for chunk in stream:
            answer_chunk = chunk['message']['content']
            answer += answer_chunk
            printer.print(answer_chunk, end='', flush=True)
        printer.print('\n</answer>\n')
        time_end = time.time()
        stats[player]["time"] += time_end - time_start
        printer.print(f'System: Time taken: {time_end - time_start}')

        # Resolve answer
        message, status = game.make_move(answer)
        printer.print(message)

        if status == MoveResponse.INVALID:
            stats[player]["errors"] += 1
            continue
        if status == MoveResponse.WIN:
            stats[player]["wins"] += 1
            stats[other]["loses"] += 1
            break
        if status == MoveResponse.DRAW:
            stats[player]["draws"] += 1
            stats[other]["draws"] += 1
            break

        # Switch player
        retries = 0
        if player == 0:
            player = 1
        else:
            player = 0

    printer.print('System: Game ended.')

    return stats

# mai
printer = Printer('output/mnk')

models = ['qwen2.5', 'llama3.1', 'phi4', 'mistral', 'deepseek-r1']
stats = [{
    "wins": 0, "loses": 0, "draws": 0, "errors": 0, "forfeits": 0, "other_forfeits": 0, "time": 0,
}] * len(models)
for c in range(0, 1):
    for i in range(0, len(models)):
        for j in range(0, len(models)):
            if i == j:
                continue
            printer.print(f"League System: Starting game {models[i]} vs. {models[j]}")
            round_stat = run_single_game([models[i], models[j]], printer)

            stats[i] = {k: stats[i][k] + round_stat[0][k] for k in stats[i]}
            stats[j] = {k: stats[j][k] + round_stat[1][k] for k in stats[j]}

            printer.print("Current tally:")
            printer.print(f"Model {models[i]}:\n{stats[i]}")
            printer.print(f"Model {models[j]}:\n{stats[j]}")

printer.print("****************************************************************")
printer.print("League concluded.")
for i in range(0, len(models)):
    printer.print(f"Model {models[i]}:\n{stats[i]}")
