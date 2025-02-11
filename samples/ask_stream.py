from ollama import chat

stream = chat(
    model='llama3.2',
    messages=[{'role': 'user', 'content': '1 + 4 + 7 + ... + 100'}],
    stream=True,
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)