"""Talk to a local model through the Ollama server."""

import ollama

DEFAULT_MODEL = "llama3.2:3b"


def make_client(host: str | None = None) -> ollama.Client:
    """Create a client for Ollama. With no host it uses http://localhost:11434."""
    return ollama.Client(host=host)


def ask(prompt: str, model: str = DEFAULT_MODEL, client=None) -> str:
    """Send one prompt to the model and return its answer as text."""
    client = client or make_client()
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.message.content


def list_models(client=None) -> list[str]:
    """Return the names of the models downloaded on this computer."""
    client = client or make_client()
    return sorted(m.model for m in client.list().models)
