from ollama import Client
import threading

def ask_model(model):
    client = Client(
      host='http://localhost:11434',
    )

    print(f"Asking Model {model}")
    response = client.chat(model=m, messages=[
      {
        'role': 'user',
        'content': '1 + 4 + 7 + ... + 100',
      },
    ])
    print(f"Model {model} answered:")
    print(response.message.content)
    print("--------")

models = ['deepseek-r1', 'llama3.2', 'mistral', 'qwen']

for m in models:
    threading.Thread(target=ask_model, args=(m,)).start()
    # ask_model(m)
