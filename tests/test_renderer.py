import json
import os
import sys
import shutil
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aops_downloader import download_contest
from renderer import render_json, render_wikitext


pandoc_exists = True
try:
    import pypandoc
    pypandoc.get_pandoc_path()
except (ImportError, OSError):
    pandoc_exists = False

asy_exists = shutil.which("asy") is not None

skip_render = pytest.mark.skipif(not (pandoc_exists and asy_exists), reason="renderer dependencies missing")


@skip_render
def test_render_json(tmp_path):
    problems = download_contest(2025, "8")
    subset = {"1": problems[1], "5": problems[5]}
    json_path = tmp_path / "problems.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(subset, f, ensure_ascii=False)

    render_json(str(json_path), str(tmp_path))

    assert (tmp_path / "index.html").is_file()
    assert (tmp_path / "1.html").is_file()
    assert (tmp_path / "5.html").is_file()


@skip_render
def test_render_wikitext_asy():
    problems = download_contest(2025, "8")
    html = render_wikitext(problems[5])
    assert "data:image/png;base64" in html
