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
        "redirects": 1,
        "format": "json",
    }
    response = requests.get(API_URL, params=params, timeout=1000)
    response.raise_for_status()
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        raise ValueError("Page not found")
    page = next(iter(pages.values()))
    revisions = page.get("revisions")
    if not revisions:
        raise ValueError("No revisions found")
    text = revisions[0].get("*") or revisions[0].get("slots", {}).get("main", {}).get(
        "*"
    )
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
        section = wikitext[header.end() : end].strip()
        section = _SOLUTION_LINK_RE.sub("", section)
        section = _FILE_RE.sub("", section)
        section = section.strip()
        problems[number] = section
    return problems


_ANSWER_RE = re.compile(r"^#\s*([A-E]|\d{1,3})\b", re.MULTILINE)


def parse_answers(wikitext: str) -> Dict[int, str]:
    """Parse answer key wikitext and return mapping from problem number to answer string.

    Answers may be single letters (A-E) for AMC/AHSME contests or numeric
    values for AIME contests.
    """
    answers: Dict[int, str] = {}
    idx = 1
    for line in wikitext.splitlines():
        m = _ANSWER_RE.match(line.strip())
        if m:
            answers[idx] = m.group(1)
            idx += 1
    return answers


def parse_solutions(wikitext: str) -> str:
    """Extract solution sections from a problem page wikitext."""
    solutions: List[str] = []
    headers = list(_HEADER_RE.finditer(wikitext))
    for i, header in enumerate(headers):
        title = header.group(1).strip().lower()
        if "solution" in title and "video" not in title:
            end = headers[i + 1].start() if i + 1 < len(headers) else len(wikitext)
            section = wikitext[header.end() : end].strip()
            section = _FILE_RE.sub("", section)
            section = re.sub(r"^~.*$", "", section, flags=re.MULTILINE)
            solutions.append(section.strip())
    return "\n\n".join(filter(None, solutions))


from typing import List


def download_contest(year: str | int, contest: str) -> List[Dict[str, Any]]:
    """Download contest problems, answers, and solutions from AoPS.

    The returned structure is a list where each item contains the fields:
    ``ID``, ``Year``, ``ProblemNumber``, ``QuestionType``, ``Question``,
    ``Answer``, ``Solution`` and ``source``.
    """
    year_str = str(year)

    # Determine base wiki page prefix based on contest type
    contest_clean = contest.strip()
    is_aime = contest_clean.upper().startswith("AIME")
    if is_aime:
        base = f"{year_str} {contest_clean}"
        source = "AIME"
    elif contest_clean.upper() == "AHSME":
        base = f"{year_str} AHSME"
        source = "AHSME"
    else:
        base = f"{year_str} AMC {contest_clean}"
        if contest_clean.startswith("8"):
            source = "AMC8"
        elif contest_clean.startswith("10"):
            source = "AMC10"
        else:
            source = "AMC12"

    # Download main contest page with all problems
    print("Fetching problems for", year_str, contest)
    problems_title = f"{base} Problems"
    problems_text = fetch_page_wikitext(problems_title)
    problems = parse_problems(problems_text)

    # Download answer key
    print("Fetching answers for", year_str, contest)
    answer_title = f"{base} Answer Key"
    answers_text = fetch_page_wikitext(answer_title)
    answers = parse_answers(answers_text)

    result: List[Dict[str, Any]] = []
    for number in sorted(problems):
        print(f"Processing problem {number} for {year_str} {contest}")
        question = problems[number]
        problem_page = f"{base} Problems/Problem {number}"
        sol_text = fetch_page_wikitext(problem_page)
        solution = parse_solutions(sol_text)
        pid = f"{year_str}-{contest}-{number}"
        result.append(
            {
                "ID": pid,
                "Year": year_str,
                "ProblemNumber": number,
                "QuestionType": "int3" if is_aime else "choice",
                "Question": question,
                "Answer": answers.get(number, ""),
                "Solution": solution,
                "Source": source,
            }
        )
    return result


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Download AMC, AIME, or AHSME problems from AoPS"
    )
    parser.add_argument("year", help="Contest year")
    parser.add_argument(
        "contest",
        help="Contest name, e.g. '8', '10A', '10B', '12A', '12B', 'AIME I', 'AHSME'",
    )
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()
    problems = download_contest(args.year, args.contest)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(problems, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(problems, indent=2, ensure_ascii=False))
