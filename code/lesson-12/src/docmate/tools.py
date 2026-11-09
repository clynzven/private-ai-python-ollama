"""Tools: Python functions the model may ask us to run, and the loop that runs them."""

import ast
import datetime
import json
import operator
from types import SimpleNamespace

from docmate.llm import make_client, strip_thinking

AGENT_MODEL = "qwen3:4b"  # better at using tools than llama3.2:3b (see lesson 9)

AGENT_RULES = (
    "You are DocMate, the assistant of Maple Grove Community Library. Rules: "
    "1. For any question about the library, ALWAYS call search_documents first; "
    "you know nothing about this library yourself. "
    "2. For anything about dates or days, call today. "
    "3. For arithmetic, call calculate. "
    "4. Answer only with facts from tool results. Prices are in euros."
)

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def safe_math(expression: str) -> float:
    """Evaluate + - * / on numbers only. Never eval() text that a model wrote!"""

    def walk(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](walk(node.operand))
        raise ValueError(f"not allowed: {ast.dump(node)[:40]}")

    return walk(ast.parse(expression, mode="eval").body)


def make_tools(index, now=datetime.date.today) -> dict:
    """The tools DocMate offers. The docstrings tell the model what each one does."""

    def today() -> str:
        """Get today's date and the day of the week."""
        return now().strftime("%A %d %B %Y")

    def search_documents(query: str) -> str:
        """Search the library's documents.

        Args:
            query: what to look for, in a few words
        """
        return "\n\n".join(f"({hit.source}) {hit.text}" for hit in index.search(query, 2))

    def calculate(expression: str) -> str:
        """Do arithmetic with + - * and /.

        Args:
            expression: numbers and operators, like 7 * 2.5
        """
        return f"{safe_math(expression):.2f}"

    return {tool.__name__: tool for tool in (today, search_documents, calculate)}


def tool_call_in_text(text: str, tools: dict):
    """Small models sometimes *write* a tool call as JSON instead of making one. Catch that."""
    try:
        data = json.loads(strip_thinking(text))
    except ValueError:
        return None
    if isinstance(data, dict) and data.get("name") in tools:
        function = SimpleNamespace(name=data["name"], arguments=data.get("arguments") or {})
        return [SimpleNamespace(function=function)]
    return None


def run_agent(
    question: str,
    tools: dict,
    model: str = AGENT_MODEL,
    client=None,
    on_tool=None,
    max_steps: int = 6,
) -> str:
    """Let the model call tools until it can answer."""
    client = client or make_client()
    messages = [{"role": "system", "content": AGENT_RULES}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        response = client.chat(
            model=model, messages=messages, tools=list(tools.values()), options={"temperature": 0}
        )
        messages.append(response.message)
        calls = response.message.tool_calls or tool_call_in_text(response.message.content, tools)
        if not calls:
            return strip_thinking(response.message.content)
        for call in calls:
            name, args = call.function.name, call.function.arguments
            try:
                result = tools[name](**args)
            except Exception as err:  # tell the model what went wrong instead of crashing
                result = f"error: {err}"
            if on_tool:
                on_tool(name, args, result)
            messages.append({"role": "tool", "tool_name": name, "content": str(result)})
    return "Sorry, I needed too many steps for that question."
