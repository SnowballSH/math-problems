import json
import re
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aops_downloader import fetch_page_wikitext, parse_problems


def test_fetch_and_parse():
    text = fetch_page_wikitext("2020 AMC 8 Problems")
    assert "Problem 1" in text
    problems = parse_problems(text)
    assert 1 in problems
    assert 25 in problems  # AMC 8 has 25 questions
    # check latex markup appears
    assert re.search(r"\\[math|cmath]", problems[1]) or "<math>" in problems[1]

