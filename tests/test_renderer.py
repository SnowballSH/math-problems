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

skip_render = pytest.mark.skipif(not (pandoc_exists and asy_exists), reason="renderer dependencies missing")


@skip_render
def test_render_json(tmp_path):
    problems = download_contest(2025, "8")
    subset = {"1": problems[1], "5": problems[5]}
    json_path = tmp_path / "problems.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(subset, f, ensure_ascii=False)

    render_json(str(json_path), str(tmp_path))

    index_path = tmp_path / "index.html"
    assert index_path.is_file()
    assert (tmp_path / "1.html").is_file()
    assert (tmp_path / "5.html").is_file()
    assert MATHJAX_SCRIPT in index_path.read_text(encoding="utf-8")


@skip_render
def test_render_wikitext_asy():
    problems = download_contest(2025, "8")
    html = render_wikitext(problems[5])
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
