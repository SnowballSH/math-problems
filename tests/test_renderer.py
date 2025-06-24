import json
import os
import sys
import shutil
import base64
import re
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from aops_downloader import download_contest
from renderer import render_json, render_wikitext, MATHJAX_SCRIPT, DIAGRAM_SIZE

pandoc_exists = True
try:
    import pypandoc

    pypandoc.get_pandoc_path()
except (ImportError, OSError):
    pandoc_exists = False

asy_exists = shutil.which("asy") is not None

skip_render = pytest.mark.skipif(
    not (pandoc_exists and asy_exists), reason="renderer dependencies missing"
)


@skip_render
def test_render_json(tmp_path):
    problems = download_contest("2025", "8")
    subset = [p for p in problems if p["ID"] in ("2025-8-1", "2025-8-5")]
    json_path = tmp_path / "problems.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(subset, f, ensure_ascii=False)

    # verify json structure
    with open(json_path, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert isinstance(saved, list)
    assert all("ID" in item for item in saved)

    render_json(str(json_path), str(tmp_path))

    index_path = tmp_path / "index.html"
    assert index_path.is_file()
    idx_html = index_path.read_text(encoding="utf-8")
    assert MATHJAX_SCRIPT in idx_html
    assert "Answer:" not in idx_html

    file1 = (tmp_path / "2025-8-1.html").read_text(encoding="utf-8")
    assert "Answer:" in file1
    file5 = (tmp_path / "2025-8-5.html").read_text(encoding="utf-8")
    assert "Answer:" in file5


@skip_render
def test_render_wikitext_asy():
    problems = download_contest("2025", "8")
    q = next(item["Question"] for item in problems if item["ID"] == "2025-8-5")
    html = render_wikitext(q)
    assert "data:image/svg+xml;base64" in html


@skip_render
def test_math_rendering():
    html = render_wikitext("The sum is <math>a+b=c</math> and also \\(d\\)")
    assert "math inline" in html


@skip_render
def test_svg_fixed_size():
    html = render_wikitext("<asy>size(100);draw((0,0)--(1,0));</asy>")
    m = re.search(r"data:image/svg\\+xml;base64,([^\"]+)", html)
    assert m
    svg = base64.b64decode(m.group(1)).decode("utf-8")
    assert f'width="{DIAGRAM_SIZE}px"' in svg
    assert f'height="{DIAGRAM_SIZE}px"' in svg
