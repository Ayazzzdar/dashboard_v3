# Memorial pack — locked reference set (approved 2026-10-21)

The five pages in this folder are the approved reference for the memorial pack.

| # | Page | File | Render |
|---|------|------|--------|
| 1 | On the Day You Passed | page1.html | MEM_page1.png |
| 2 | This Day in History | page2.html | MEM_page2.png |
| 3 | The Economy in {year} | page3.html | MEM_page3.png |
| 4 | A Cultural Snapshot of {year} | page4.html | MEM_page4.png |
| 5 | A Life in Numbers | page5.html | MEM_page5.png |

Overview of all five: MEM_all_pages.png

## Page format
- 1414 × 2000 px (A-series portrait), rendered with headless Chrome via `./render.sh page1 … page5`.

## Colour
- Paper `#f3eee2` with a faint radial vignette
- Ink `#1b1815` (text), rules `#2a2622`, secondary text `#5b544a`
- No accent colours — everything is ink on paper (the old blue was removed), except the red authenticity seal on page 1.

## Type
- Headings and numbers: **Playfair Display** 400, uppercase titles with ~0.05em tracking; numbers use lining figures.
- Body and labels: **Cormorant Garamond** — body 500, labels 600 uppercase with 0.2–0.3em tracking, often flanked by short rules.
- Italic Playfair for titles of works (songs, books, shows) and for "billion".

## Border and ornaments (same on every page)
- Double-rule frame inset 56 px (1.5 px outer, 0.75 px inner at +9 px).
- Acanthus corner flourish (`assets/corner.png`), 250 px, mirrored into all four corners.
- Section dividers: rule with a centred outline diamond.
- Boxes/cards: square double-rule boxes (1.25 px + 0.6 px inner at +7 px); circles use the same double ring.
- Page 1 carries the red foil **Certificate of Authenticity** seal at the foot of the right column, matching the seal from the original birthday pack: 46-tooth serrated disc, bright red satin gradient, white Times-style lettering (Tinos) — "CERTIFICATE OF AUTHENTICITY" around the top, "THE DAY / ARCHIVE" in the centre. It is drawn as inline SVG in page1.html (no image file) and is the only colour on any page.

## Icons
All icons are Kie (GPT Image 2.5 Sunburst, transparent background) in one style, stored trimmed in `assets/`.
Prompt style to reuse for any new icon:

> Victorian copperplate engraving, fine black ink line art with delicate cross-hatching and stipple shading, no color, no text, no letters, no frames. Isolated on a transparent background. Refined antique almanac / memorial keepsake aesthetic.

Generate four per 2K sheet (2×2 grid, "wide empty space between them") and split at the empty gaps; this is the cheapest way (10 credits per four icons).

Current icon set: sunrise, sun, hourglass, moon, heart, dove, daffodil, crown, record, flag, globe, australia, house, milk, bread, eggs, chocolate, pump, inflation, books, tv, mannequin, bulb, pram, quill, corner.

## Handoff to the repo / cloud session
- This folder is the **design reference**, not the production renderer. Production pages come from the repo's own pipeline (`render_pack.py` / `dashboard_v3.py`); port the look into that pipeline rather than replacing it.
- Text and figures in these pages are Arthur James Whelan's sample data (died 16 Aug 2023); every value must still come from the pipeline's per-order data.
- `renders/` holds the approved PNGs to compare against; `assets/` holds the icons (256-colour PNG with transparency, max 900 px) and the corner flourish.
- The HTML loads Playfair Display and Cormorant Garamond from Google Fonts; a Python/PIL renderer will need the TTF files for both fonts.
- Before changing any repo file, fetch and work from the live `origin/main` (the repo is also edited through the GitHub website), and diff against it before handing back full-file replacements.
