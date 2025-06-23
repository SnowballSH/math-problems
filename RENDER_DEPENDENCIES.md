# Dependencies for renderer

## System packages
- `pandoc` - used via `pypandoc` to convert MediaWiki wikitext to HTML.
- `asymptote` - command line tool to render `<asy>` diagrams.
- `poppler-utils` - provides `pdftocairo` for converting Asymptote PDFs to SVG.

## Python packages
- `pypandoc`
- `Pillow`
- `mwparserfromhell` (optional if wikitext preprocessing needed)
- `requests` (for downloading problems)
