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
        "Source",
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
    assert first["Source"] == "AMC8"
    assert "Video Solution" not in first["Solution"]


def test_redirect_page():
    text = fetch_page_wikitext("2023 AMC 10A Problems/Problem 5")
    # should automatically follow redirect
    assert "#redirect" not in text.lower()
    solution = parse_solutions(text)
    assert solution


def test_aime_and_ahsme():
    # AIME without I/II (1998)
    aime_text = fetch_page_wikitext("1998 AIME Problems")
    aime_problems = parse_problems(aime_text)
    assert 1 in aime_problems and 15 in aime_problems

    aime_ans_text = fetch_page_wikitext("1998 AIME Answer Key")
    aime_answers = parse_answers(aime_ans_text)
    assert aime_answers[1].isdigit()

    aime_data = download_contest("1998", "AIME")
    first = next(item for item in aime_data if item["ProblemNumber"] == 1)
    assert first["Answer"].isdigit()
    assert first["Source"] == "AIME"

    # AHSME (1999)
    ahsme_text = fetch_page_wikitext("1999 AHSME Problems")
    ahsme_problems = parse_problems(ahsme_text)
    assert 1 in ahsme_problems and 30 in ahsme_problems

    ahsme_ans_text = fetch_page_wikitext("1999 AHSME Answer Key")
    ahsme_answers = parse_answers(ahsme_ans_text)
    assert ahsme_answers[1] in "ABCDE"

    ahsme_data = download_contest("1999", "AHSME")
    first_h = next(item for item in ahsme_data if item["ProblemNumber"] == 1)
    assert first_h["Answer"] in "ABCDE"
    assert first_h["Source"] == "AHSME"
