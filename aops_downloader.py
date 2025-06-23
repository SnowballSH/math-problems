import requests
import re
from typing import Dict

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


def download_contest(year: int, contest: str) -> Dict[int, str]:
    """Download contest problems wikitext from AoPS."""
    title = f"{year} AMC {contest} Problems"
    text = fetch_page_wikitext(title)
    return parse_problems(text)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Download AMC problems from AoPS")
    parser.add_argument("year", type=int, help="Contest year")
    parser.add_argument("contest", help="Contest name, e.g. '8', '10A', '10B', '12A', '12B'")
    parser.add_argument("--output", help="Output JSON file")

    args = parser.parse_args()
    problems = download_contest(args.year, args.contest)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(problems, f, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(problems, indent=2, ensure_ascii=False))
