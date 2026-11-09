import json
from pathlib import Path

from fakes import FakeClient

from docmate.evaluate import Result, load_cases, run_eval, summary
from docmate.index import Hit


class FakeIndex:
    def search(self, query, k):
        return [Hit("borrowing-rules.md", 0, "DVDs: 1 week.", 0.9)]


def test_a_good_answer_scores_on_both_counts():
    cases = [{"question": "DVD?", "source": "borrowing-rules.md", "words": ["1 week"]}]
    [result] = run_eval(cases, FakeIndex(), client=FakeClient(reply="You can keep it 1 week [1]."))
    assert result.found_source and result.right_answer


def test_wrong_file_and_wrong_answer_are_caught():
    cases = [{"question": "Wi-Fi?", "source": "wifi-and-printing.txt", "words": ["MapleGuest"]}]
    [result] = run_eval(cases, FakeIndex(), client=FakeClient(reply="It is called LibraryNet."))
    assert not result.found_source and not result.right_answer


def test_curly_apostrophes_still_match():
    cases = [{"question": "Cafe?", "source": None, "words": ["don't know"]}]
    [result] = run_eval(cases, FakeIndex(), client=FakeClient(reply="I don’t know."))
    assert result.right_answer


def test_summary_counts():
    results = [Result("a", True, True, ""), Result("b", True, False, "")]
    assert summary(results) == "search found the right file: 2/2   answer had the facts: 1/2"


def test_the_shipped_cases_are_valid():
    cases = load_cases(Path(__file__).parent.parent / "evals" / "questions.json")
    assert len(cases) >= 8
    assert all({"question", "source", "words"} <= set(c) for c in cases)
    json.dumps(cases)
