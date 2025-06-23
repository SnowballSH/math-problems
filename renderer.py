# Simple AoPS wikitext renderer
import base64
import re
import subprocess
import tempfile

import pypandoc
import json
from pathlib import Path

ASY_RE = re.compile(r'<asy>(.*?)</asy>', re.DOTALL | re.IGNORECASE)


def _render_asy(code: str) -> bytes:
    """Render Asymptote code to PNG and return bytes."""
    # Ensure olympiad module for AoPS diagrams
    if 'import olympiad;' not in code:
        code = 'import olympiad;\n' + code
    with tempfile.TemporaryDirectory() as tmpdir:
        asy_path = f"{tmpdir}/fig.asy"
        with open(asy_path, 'w', encoding='utf-8') as f:
            f.write(code)
        try:
            subprocess.run(
                ['asy', '-f', 'png', '-o', 'out', asy_path],
                check=True,
                cwd=tmpdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise RuntimeError('Asymptote not installed') from e
        out_path = f"{tmpdir}/out.png"
        with open(out_path, 'rb') as img:
            return img.read()


def render_wikitext(wikitext: str) -> str:
    """Convert AoPS wikitext containing <math> and <asy> tags to HTML."""

    def repl(match: re.Match) -> str:
        img_data = _render_asy(match.group(1).strip())
        b64 = base64.b64encode(img_data).decode('ascii')
        return f'<img src="data:image/png;base64,{b64}" alt="diagram"/>'

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
        out_path = Path(output_dir) / f"{key}.html"
        out_path.write_text(html, encoding='utf-8')
        all_sections.append(f"<h2>Problem {key}</h2>\n{html}")

    index = "<html><body>\n" + "\n".join(all_sections) + "\n</body></html>"
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
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(html)
    elif args.cmd == 'json':
        render_json(args.input, args.output_dir)
