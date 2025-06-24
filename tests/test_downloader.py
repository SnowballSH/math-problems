import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aops_downloader import (
    fetch_page_wikitext,
    parse_problems,
    parse_answers,
    parse_solutions,
    download_contest,
)


def test_parsers_and_download():
    text = fetch_page_wikitext("2025 AMC 8 Problems")
    problems = parse_problems(text)
    assert 1 in problems and 25 in problems
    assert "[[File:" not in problems[2]

    ans_text = fetch_page_wikitext("2025 AMC 8 Answer Key")
    answers = parse_answers(ans_text)
    assert answers[1] in "ABCDE"

    sol_text = fetch_page_wikitext("2025 AMC 8 Problems/Problem 5")
    solution = parse_solutions(sol_text)
    assert "Video Solution" not in solution

    data = download_contest("2025", "8")
    assert isinstance(data, list)
    required_keys = {
        "ID",
        "Year",
        "ProblemNumber",
        "QuestionType",
        "Question",
        "Answer",
        "Solution",
    }
    for item in data:
        assert set(item.keys()) == required_keys
        assert isinstance(item["ProblemNumber"], int)
        assert isinstance(item["QuestionType"], str)
    first = next(item for item in data if item["ID"] == "2025-8-1")
    assert first["ID"] == "2025-8-1"
    assert first["ProblemNumber"] == 1
    assert first["QuestionType"] == "choice"
    assert first["Answer"] in "ABCDE"
    assert "Video Solution" not in first["Solution"]


def test_redirect_page():
    text = fetch_page_wikitext("2023 AMC 10A Problems/Problem 5")
    # should automatically follow redirect
    assert "#redirect" not in text.lower()
    solution = parse_solutions(text)
    assert solution
