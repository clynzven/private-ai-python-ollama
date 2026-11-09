from fakes import FakeClient

from docmate.llm import Settings, Timing, ask, strip_thinking, timed_ask


def test_unset_settings_are_left_out():
    assert Settings().options() == {}
    assert Settings(temperature=0, seed=7).options() == {"temperature": 0, "seed": 7}


def test_ask_sends_the_options():
    client = FakeClient()
    ask("Hi", client=client, settings=Settings(temperature=0.2))
    assert client.calls[0]["options"] == {"temperature": 0.2}


def test_timing_reports_tokens_per_second():
    answer, timing = timed_ask("Hi", client=FakeClient(reply="Hello"))
    assert answer == "Hello"
    assert timing == Timing(model="llama3.2:3b", seconds=2.0, tokens=12)
    assert timing.tokens_per_second == 6.0


def test_thinking_is_removed_from_the_answer():
    assert (
        strip_thinking("Hmm, let me think...\n</think>\n\nThe answer is 4.") == "The answer is 4."
    )
    assert strip_thinking("  Just an answer. ") == "Just an answer."


def test_ask_hides_thinking_text():
    client = FakeClient(reply="I should add them.</think>4")
    assert ask("2+2?", client=client) == "4"
