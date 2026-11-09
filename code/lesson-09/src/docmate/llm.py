"""Talk to a local model through the Ollama server."""

from dataclasses import asdict, dataclass

import ollama

DEFAULT_MODEL = "llama3.2:3b"


@dataclass
class Settings:
    """Knobs that change how the model answers. None means: use the model's default."""

    temperature: float | None = None  # 0 = focused and repeatable, higher = more creative
    seed: int | None = None  # same seed + same temperature = same answer
    num_ctx: int | None = None  # how many tokens the model can read at once

    def options(self) -> dict:
        return {name: value for name, value in asdict(self).items() if value is not None}


@dataclass
class Timing:
    model: str
    seconds: float
    tokens: int

    @property
    def tokens_per_second(self) -> float:
        return self.tokens / self.seconds if self.seconds else 0.0


def make_client(host: str | None = None) -> ollama.Client:
    """Create a client for Ollama. With no host it uses http://localhost:11434."""
    return ollama.Client(host=host)


def strip_thinking(text: str) -> str:
    """Some models (like qwen3) reason before a </think> tag. Keep only the answer."""
    if "</think>" in text:
        text = text.split("</think>", 1)[1]
    return text.strip()


def ask(
    prompt: str, model: str = DEFAULT_MODEL, client=None, settings: Settings | None = None
) -> str:
    """Send one prompt to the model and return its answer as text."""
    answer, _ = timed_ask(prompt, model=model, client=client, settings=settings)
    return answer


def timed_ask(prompt: str, model: str = DEFAULT_MODEL, client=None, settings=None):
    """Like ask(), but also return how long the model took and how many tokens it wrote."""
    client = client or make_client()
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options=(settings or Settings()).options(),
    )
    timing = Timing(
        model=model,
        seconds=(response.total_duration or 0) / 1e9,  # Ollama reports nanoseconds
        tokens=response.eval_count or 0,
    )
    return strip_thinking(response.message.content), timing


def list_models(client=None) -> list[str]:
    """Return the names of the models downloaded on this computer."""
    client = client or make_client()
    return sorted(m.model for m in client.list().models)
