import json
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aops_downloader import fetch_page_wikitext, parse_problems


def test_fetch_and_parse_and_clean():
    text = fetch_page_wikitext("2025 AMC 8 Problems")
    assert "Problem 1" in text
    problems = parse_problems(text)
    assert 1 in problems and 25 in problems
    # last problem should not include trailing sections or MAA notice
    assert "MAA Notice" not in problems[25]
    assert "See Also" not in problems[25]
    # image references should be removed
    assert "[[File:" not in problems[2]
    # latex markup still present
    assert "<math>" in problems[1]

