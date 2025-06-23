# Simple AoPS wikitext renderer
import base64
import re
import subprocess
import tempfile
import shutil

import pypandoc
import json
from pathlib import Path

ASY_RE = re.compile(r'<asy>(.*?)</asy>', re.DOTALL | re.IGNORECASE)
MATHJAX_SCRIPT = (
    '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>'
)


def _render_asy(code: str) -> bytes:
    """Render Asymptote code to SVG and return bytes."""
    # Ensure olympiad module for AoPS diagrams
    if 'import olympiad;' not in code:
        code = 'import olympiad;\n' + code
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        asy_path = tmp / "fig.asy"
        with open(asy_path, 'w', encoding='utf-8') as f:
            f.write(code)
        # copy bundled Asymptote modules
        lib_dir = Path(__file__).parent / "libs"
        if lib_dir.is_dir():
            for lib in lib_dir.glob("*.asy"):
                shutil.copy(lib, tmp / lib.name)
        try:
            subprocess.run(
                ['asy', '-f', 'pdf', '-o', 'out', asy_path],
                check=True,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise RuntimeError('Asymptote not installed') from e
        pdf_path = tmp / 'out.pdf'
        svg_path = tmp / 'out.svg'
        subprocess.run(
            ['pdftocairo', '-svg', str(pdf_path), str(svg_path)],
            check=True,
            cwd=tmpdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        with open(svg_path, 'rb') as img:
            return img.read()


def render_wikitext(wikitext: str) -> str:
    """Convert AoPS wikitext containing <math> and <asy> tags to HTML."""

    def repl(match: re.Match) -> str:
        img_data = _render_asy(match.group(1).strip())
        b64 = base64.b64encode(img_data).decode('ascii')
        return f'<img src="data:image/svg+xml;base64,{b64}" alt="diagram"/>'

    replaced = ASY_RE.sub(repl, wikitext)
    html = pypandoc.convert_text(
        replaced,
        'html',
        format='mediawiki',
        extra_args=['--mathjax']
    )
    return html


def render_json(json_file: str, output_dir: str) -> None:
    """Render problems stored in a JSON file to individual HTML files and a combined page."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(json_file, 'r', encoding='utf-8') as f:
        problems = json.load(f)

    all_sections = []
    for key in sorted(problems, key=lambda k: int(k)):
        html = render_wikitext(problems[key])
        page = f"<html><head>{MATHJAX_SCRIPT}</head><body>\n{html}\n</body></html>"
        out_path = Path(output_dir) / f"{key}.html"
        out_path.write_text(page, encoding='utf-8')
        all_sections.append(f"<h2>Problem {key}</h2>\n{html}")

    index = (
        f"<html><head>{MATHJAX_SCRIPT}</head><body>\n"
        + "\n".join(all_sections)
        + "\n</body></html>"
    )
    (Path(output_dir) / "index.html").write_text(index, encoding='utf-8')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Render AoPS wikitext to HTML')
    sub = parser.add_subparsers(dest='cmd', required=True)

    file_p = sub.add_parser('file', help='Render a wikitext file')
    file_p.add_argument('input')
    file_p.add_argument('output')

    json_p = sub.add_parser('json', help='Render problems from a JSON file')
    json_p.add_argument('input')
    json_p.add_argument('output_dir')

    args = parser.parse_args()

    if args.cmd == 'file':
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
        html = render_wikitext(text)
        page = f"<html><head>{MATHJAX_SCRIPT}</head><body>\n{html}\n</body></html>"
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(page)
    elif args.cmd == 'json':
        render_json(args.input, args.output_dir)
