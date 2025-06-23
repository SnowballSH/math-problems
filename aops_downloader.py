import requests
import re
from typing import Dict, List, Any

API_URL = "https://artofproblemsolving.com/wiki/api.php"


def fetch_page_wikitext(page_title: str) -> str:
    """Fetch raw wikitext of a page from AoPS wiki."""
    params = {
        "action": "query",
        "titles": page_title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
    }
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        raise ValueError("Page not found")
    page = next(iter(pages.values()))
    revisions = page.get("revisions")
    if not revisions:
        raise ValueError("No revisions found")
    text = revisions[0].get("*") or revisions[0].get("slots", {}).get("main", {}).get("*")
    if text is None:
        raise ValueError("Content not available")
    return text


_HEADER_RE = re.compile(r"^==\s*([^=]+?)\s*==\s*$", re.MULTILINE)
_PROBLEM_HEADER_RE = re.compile(r"^==\s*Problem\s*(\d+)\s*==\s*$", re.MULTILINE)
_SOLUTION_LINK_RE = re.compile(r"\[\[[^\]]+\|Solution\]\]")
_FILE_RE = re.compile(r"\[\[File:[^\]]+\]\]")


def parse_problems(wikitext: str) -> Dict[int, str]:
    """Parse wikitext and return mapping from problem number to cleaned wikitext."""
    problems: Dict[int, str] = {}
    headers = list(_HEADER_RE.finditer(wikitext))
    for i, header in enumerate(headers):
        title = header.group(1).strip()
        m = _PROBLEM_HEADER_RE.match(header.group(0))
        if not m:
            continue
        number = int(m.group(1))
        end = headers[i + 1].start() if i + 1 < len(headers) else len(wikitext)
        section = wikitext[header.end():end].strip()
        section = _SOLUTION_LINK_RE.sub("", section)
        section = _FILE_RE.sub("", section)
        section = section.strip()
        problems[number] = section
    return problems


_ANSWER_RE = re.compile(r"^#\s*([A-E])\b", re.MULTILINE)


def parse_answers(wikitext: str) -> Dict[int, str]:
    """Parse answer key wikitext and return mapping from problem number to answer letter."""
    answers: Dict[int, str] = {}
    for i, line in enumerate(wikitext.splitlines(), start=1):
        m = _ANSWER_RE.match(line.strip())
        if m:
            answers[i] = m.group(1)
    return answers


def parse_solutions(wikitext: str) -> str:
    """Extract solution sections from a problem page wikitext."""
    solutions: List[str] = []
    headers = list(_HEADER_RE.finditer(wikitext))
    for i, header in enumerate(headers):
        title = header.group(1).strip().lower()
        if "solution" in title and "video" not in title:
            end = headers[i + 1].start() if i + 1 < len(headers) else len(wikitext)
            section = wikitext[header.end():end].strip()
            section = _FILE_RE.sub("", section)
            section = re.sub(r"^~.*$", "", section, flags=re.MULTILINE)
            solutions.append(section.strip())
    return "\n\n".join(filter(None, solutions))


def download_contest(year: str | int, contest: str) -> Dict[str, Dict[str, Any]]:
    """Download contest problems, answers, and solutions from AoPS."""
    year_str = str(year)

    # Download main contest page with all problems
    problems_title = f"{year_str} AMC {contest} Problems"
    problems_text = fetch_page_wikitext(problems_title)
    problems = parse_problems(problems_text)

    # Download answer key
    answer_title = f"{year_str} AMC {contest} Answer Key"
    answers_text = fetch_page_wikitext(answer_title)
    answers = parse_answers(answers_text)

    result: Dict[str, Dict[str, Any]] = {}
    for number, question in problems.items():
        problem_page = f"{year_str} AMC {contest} Problems/Problem {number}"
        sol_text = fetch_page_wikitext(problem_page)
        solution = parse_solutions(sol_text)
        pid = f"{year_str}-{contest}-{number}"
        result[pid] = {
            "ID": pid,
            "Year": year_str,
            "Problem Number": number,
            "Question": question,
            "Answer": answers.get(number, ""),
            "Solution": solution,
        }
    return result


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Download AMC problems from AoPS")
    parser.add_argument("year", help="Contest year")
    parser.add_argument("contest", help="Contest name, e.g. '8', '10A', '10B', '12A', '12B'")
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()
    problems = download_contest(args.year, args.contest)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(problems, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(problems, indent=2, ensure_ascii=False))
