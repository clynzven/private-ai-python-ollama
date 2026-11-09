"""A pretend Ollama client, so tests run fast and without a model."""

from types import SimpleNamespace


def _message(content):
    return SimpleNamespace(message=SimpleNamespace(content=content))


class FakeClient:
    def __init__(self, reply="Hello from the fake model!", models=()):
        self.reply = reply
        self.models = list(models)
        self.calls = []

    def chat(self, model, messages, stream=False, **kwargs):
        # Copy the list: the caller keeps adding to it after this call.
        self.calls.append({"model": model, "messages": list(messages), **kwargs})
        if stream:
            # Send the reply a few characters at a time, like a real model.
            return (_message(self.reply[i : i + 4]) for i in range(0, len(self.reply), 4))
        return _message(self.reply)

    def list(self):
        return SimpleNamespace(models=[SimpleNamespace(model=m) for m in self.models])
