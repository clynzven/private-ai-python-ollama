"""Structured answers: make the model fill in a Pydantic model instead of writing free text."""

from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from docmate.llm import DEFAULT_MODEL, make_client


class DocSummary(BaseModel):
    title: str = Field(description="a short title for the document")
    summary: str = Field(description="what the document says, in one or two sentences")
    topics: list[str] = Field(description="up to five topics, one or two words each", max_length=5)
    audience: Literal["everyone", "adults", "children", "staff"]


class ExtractionError(Exception):
    """The model did not produce valid data, even after retrying."""


def extract(
    text: str, schema: type[BaseModel], model: str = DEFAULT_MODEL, client=None, retries: int = 2
) -> BaseModel:
    """Ask the model to fill in `schema` from `text`, and check the answer with Pydantic."""
    client = client or make_client()
    messages = [{"role": "user", "content": f"Read the document and fill in the fields.\n\n{text}"}]
    for _ in range(retries + 1):
        response = client.chat(
            model=model,
            messages=messages,
            format=schema.model_json_schema(),  # Ollama only lets the model write this shape
            options={"temperature": 0},
        )
        reply = response.message.content
        try:
            return schema.model_validate_json(reply)
        except ValidationError as err:
            # Show the model its mistake and let it try again.
            messages += [
                {"role": "assistant", "content": reply},
                {"role": "user", "content": f"That was not valid: {err}. Please fix it."},
            ]
    raise ExtractionError(f"no valid {schema.__name__} after {retries + 1} tries")
