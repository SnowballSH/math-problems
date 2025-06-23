# Simple AoPS wikitext renderer
import base64
import re
import subprocess
import tempfile

import pypandoc

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


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Render AoPS wikitext to HTML')
    parser.add_argument('input', help='Input wikitext file')
    parser.add_argument('output', help='Output HTML file')
    args = parser.parse_args()
    with open(args.input, 'r', encoding='utf-8') as f:
        text = f.read()
    html = render_wikitext(text)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)
