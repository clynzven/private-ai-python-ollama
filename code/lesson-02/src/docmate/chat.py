"""A conversation with memory: every message is sent back to the model each turn."""

from collections.abc import Iterator

from docmate.llm import DEFAULT_MODEL, make_client

SYSTEM_PROMPT = (
    "You are DocMate, a helpful assistant that runs privately on the user's computer. "
    "Keep your answers short and clear."
)


class Chat:
    def __init__(self, model: str = DEFAULT_MODEL, client=None, system: str = SYSTEM_PROMPT):
        self.model = model
        self.client = client or make_client()
        self.messages = [{"role": "system", "content": system}]

    def send(self, text: str) -> Iterator[str]:
        """Send a message and yield the reply piece by piece as the model writes it."""
        self.messages.append({"role": "user", "content": text})
        pieces = []
        stream = self.client.chat(model=self.model, messages=self.messages, stream=True)
        for chunk in stream:
            piece = chunk.message.content
            pieces.append(piece)
            yield piece
        # Remember the full reply so the model sees it next turn.
        self.messages.append({"role": "assistant", "content": "".join(pieces)})

    def reset(self) -> None:
        """Forget the conversation but keep the system prompt."""
        del self.messages[1:]
