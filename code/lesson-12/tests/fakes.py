"""A pretend Ollama client, so tests run fast and without a model."""

from types import SimpleNamespace


def _message(content, tokens=12, nanoseconds=2_000_000_000):
    tool_calls = None
    if isinstance(content, dict):  # {"tool": name, "args": {...}} pretends to call a tool
        tool_calls = [
            SimpleNamespace(
                function=SimpleNamespace(name=content["tool"], arguments=content["args"])
            )
        ]
        content = ""
    return SimpleNamespace(
        message=SimpleNamespace(content=content, tool_calls=tool_calls),
        eval_count=tokens,
        total_duration=nanoseconds,
    )


class FakeClient:
    def __init__(self, reply="Hello from the fake model!", models=(), replies=None):
        self.reply = reply
        self.replies = list(replies or [])  # if set, answer with these one after another
        self.models = list(models)
        self.calls = []

    def chat(self, model, messages, stream=False, **kwargs):
        # Copy the list: the caller keeps adding to it after this call.
        self.calls.append({"model": model, "messages": list(messages), **kwargs})
        if self.replies:
            self.reply = self.replies.pop(0)
        if stream:
            # Send the reply a few characters at a time, like a real model.
            return (_message(self.reply[i : i + 4]) for i in range(0, len(self.reply), 4))
        return _message(self.reply)

    def embed(self, model, input):
        self.calls.append({"model": model, "input": list(input)})
        return SimpleNamespace(embeddings=[fake_vector(text) for text in input])

    def list(self):
        return SimpleNamespace(models=[SimpleNamespace(model=m) for m in self.models])


def fake_vector(text: str) -> list[float]:
    """A tiny pretend embedding: how often a few marker words appear."""
    text = text.lower()
    return [float(text.count(word)) for word in ("open", "print", "book", "wifi")] + [0.1]
