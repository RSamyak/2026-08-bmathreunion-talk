# B Math Reunion Talk

Quarto (reveal.js) slide deck. Source of truth: `slides.qmd`.

## Render

```bash
quarto render slides.qmd          # -> _output/slides.html (self-contained)
```

Present from the HTML: `F` fullscreen, `S` speaker notes, `O` overview.

## Export to PDF

Reveal's `?print-pdf` mode re-flows every slide and breaks layouts. Instead,
`deck_to_pdf.py` screenshots the *native* HTML rendering one click at a time
and stitches the frames into a PDF — deterministic and pixel-faithful to what
you present, with each fragment/click on its own page (beamer-style).

```bash
python3 tools/deck_to_pdf.py _output/slides.html slides.pdf
```

Deps (one-time): `pip3 install --user websocket-client PyMuPDF`.

## Layout

- `plans/` — talk planning (`outline.md` = structure, `ideas.md` = raw material)
- `slides.qmd` — the deck
- `_quarto.yml`, `theme.scss` — reveal config + visual theme
- `tools/` — HTML→PDF export and PNG capture helpers
- `_output/` — rendered HTML (generated)
