# Lesson 2: Chat with Memory and Streaming

## What you built
- `src/docmate/chat.py`: a `Chat` class. It keeps a list of messages (system, user, assistant)
  and sends the whole list every turn, which is how the model "remembers".
- Streaming: `Chat.send()` is a generator that yields the reply piece by piece as the model writes it.
- `docmate chat`: an interactive chat with `/reset` and `/quit`.
- Tests for streaming, memory, reset, and the fact that a generator does nothing until you read it.

## Try it
```bash
uv run docmate chat
printf 'My name is Sam.\nWhat is my name?\n/quit\n' | uv run docmate chat
./check.sh
```

## Exercises
1. Add a `/history` command that prints how many messages the chat holds.
2. Add a `--system` option to `docmate chat` to change the system prompt.
3. Long chats grow without limit. Keep only the system prompt and the last 10 messages.
