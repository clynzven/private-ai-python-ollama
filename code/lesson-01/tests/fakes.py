"""A pretend Ollama client, so tests run fast and without a model."""

from types import SimpleNamespace


class FakeClient:
    def __init__(self, reply="Hello from the fake model!", models=()):
        self.reply = reply
        self.models = list(models)
        self.calls = []

    def chat(self, model, messages, **kwargs):
        self.calls.append({"model": model, "messages": messages, **kwargs})
        return SimpleNamespace(message=SimpleNamespace(content=self.reply))

    def list(self):
        return SimpleNamespace(models=[SimpleNamespace(model=m) for m in self.models])
