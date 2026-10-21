"""
Memorial pack renderer.

Fills the tokenised HTML templates in memorial/templates/ with one order's data
and screenshots each page to a PNG using headless Chromium. This preserves the
approved HTML/CSS design exactly (engraved seal, fine typography) rather than
re-drawing it in Pillow.

Fonts are injected from the repo's own fonts/ folder so rendering works offline
in production (no dependency on Google Fonts at render time).

Public API:
    from memorial_render import render_memorial_pack
    paths = render_memorial_pack(data, output_dir)   # -> [page1.png ... page5.png]

`data` is a flat dict keyed by the template tokens (see TOKENS below), produced by
memorial_research.build_pack_data().
"""

import os
import shutil
import subprocess
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
TPL_DIR = os.path.join(_HERE, "memorial", "templates")
ASSETS_DIR = os.path.join(_HERE, "memorial", "assets")
STYLE_PATH = os.path.join(_HERE, "memorial", "style.css")
FONT_DIR = os.path.join(_HERE, "fonts")

PAGE_W, PAGE_H = 1414, 2000

# Every token the templates expect. Missing keys render as empty (never a raw {{token}}).
TOKENS = [
    # page 1
    "NAME", "DATE_LINE", "LIFESPAN", "AGE", "PM", "INCOMING_PM", "MONARCH", "SALARY",
    "REM1_NAME", "REM1_ROLE", "REM2_NAME", "REM2_ROLE", "REM3_NAME", "REM3_ROLE",
    "NEWS1", "NEWS2", "NEWS3", "NRL", "AFL", "BEST_ACTOR", "BEST_ACTRESS",
    "BATHURST", "AUSOPEN", "WORLD_POP", "AUS_POP", "FLOWER_IMG", "FLOWER_NAME",
    "SONG", "ARTIST", "AVG_HOUSE", "MILK", "BREAD", "EGGS",
    # page 2
    "P2_DATE", "YEAR1", "EVENT1", "YEAR2", "EVENT2", "YEAR3", "EVENT3", "YEAR4", "EVENT4",
    # page 3
    "YEAR", "YEARS_WAGES", "PETROL", "INFLATION", "STAMP", "CINEMA", "CADBURY",
    # page 4
    "BOOK", "BOOK_DESC", "TV", "TV_DESC", "FASHION", "FASHION_DESC",
    "TECH", "TECH_DESC", "BIRTHS", "BIRTHS_DESC",
    # page 5
    "DAYS", "YEARS", "WEEKS", "MOONS", "HEARTBEATS",
]

_CHROME_CANDIDATES = [
    os.environ.get("MEMORIAL_CHROME", ""),
    "/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable", "chromium", "chromium-browser", "google-chrome",
]


def find_chrome():
    """Locate a Chromium/Chrome binary. Honours $MEMORIAL_CHROME, then PATH, then
    the Playwright cache (useful in dev)."""
    for c in _CHROME_CANDIDATES:
        if not c:
            continue
        p = shutil.which(c) if os.path.sep not in c else (c if os.path.exists(c) else None)
        if p:
            return p
    # Playwright-style cache (dev containers)
    pw = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    if os.path.isdir(pw):
        for root, _dirs, files in os.walk(pw):
            for name in ("chrome", "headless_shell", "chromium"):
                if name in files:
                    return os.path.join(root, name)
    raise RuntimeError(
        "No Chromium/Chrome found. On Streamlit Cloud add a packages.txt containing "
        "'chromium', or set $MEMORIAL_CHROME to a browser binary."
    )


def _font_css():
    """@font-face block pointing at the repo's own TTFs (offline-safe)."""
    def face(family, filename, italic=False):
        path = os.path.join(FONT_DIR, filename)
        if not os.path.exists(path):
            return ""
        style = "italic" if italic else "normal"
        return (f"@font-face{{font-family:'{family}';font-style:{style};font-weight:1 999;"
                f"src:url('file://{path}') format('truetype');}}\n")
    return (
        face("Playfair Display", "PlayfairDisplay-Regular.ttf")
        + face("Playfair Display", "PlayfairDisplay-Italic.ttf", italic=True)
        + face("Cormorant Garamond", "CormorantGaramond-Variable.ttf")
        + face("Cormorant Garamond", "CormorantGaramond-Italic-Variable.ttf", italic=True)
    )


def _fill(template_html, data):
    """Replace {{TOKEN}} with values; wire asset/style paths to absolute file URLs;
    swap the remote Google-Fonts link for local @font-face."""
    out = template_html
    out = out.replace("{{ASSETS}}", ASSETS_DIR)
    for key in TOKENS:
        out = out.replace("{{" + key + "}}", str(data.get(key, "")))
    # absolute stylesheet path
    out = out.replace('href="style.css"', f'href="file://{STYLE_PATH}"')
    # replace the Google Fonts <link> (if present) with local @font-face, and
    # force a transparent page background so the output is ink-only like the
    # birthday pack (prints onto parchment stock; the cream is design-reference only).
    import re as _re
    out = _re.sub(r'<link href="https://fonts\.googleapis\.com[^"]*" rel="stylesheet">', "", out)
    transparent = "html,body{background:transparent !important}body::before{display:none !important}"
    out = out.replace("</head>", f"<style>\n{_font_css()}{transparent}</style>\n</head>", 1)
    return out


def render_page(page_num, data, out_path, chrome=None, timeout=60, scale=2):
    """Render one page (1-5) to out_path (PNG).

    scale is the device pixel ratio: 1 -> 1414x2000, 2 -> 2828x4000 (crisp for
    A4 print, ~240 DPI). Default 2 so generated packs are print-ready.
    """
    chrome = chrome or find_chrome()
    tpl = open(os.path.join(TPL_DIR, f"page{page_num}.html"), encoding="utf-8").read()
    filled = _fill(tpl, data)
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=TPL_DIR, delete=False, encoding="utf-8") as f:
        tmp_html = f.name
        f.write(filled)
    try:
        cmd = [
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
            "--default-background-color=00000000",  # transparent screenshot (ink only)
            f"--force-device-scale-factor={scale}", f"--window-size={PAGE_W},{PAGE_H}",
            "--virtual-time-budget=8000", f"--screenshot={out_path}", f"file://{tmp_html}",
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout)
    finally:
        try:
            os.remove(tmp_html)
        except OSError:
            pass
    if not os.path.exists(out_path):
        raise RuntimeError(f"Chromium produced no output for page {page_num}")
    return out_path


def render_memorial_pack(data, output_dir, order_id="", name="", scale=2):
    """Render all 5 memorial pages. Returns the list of PNG paths.

    Filenames follow the pack convention: "{order_id} - {NAME} - {page}.png" when
    order_id/name given, else "memorial - {page}.png". scale is the print DPI
    multiplier (default 2 -> 2828x4000, crisp on A4).
    """
    os.makedirs(output_dir, exist_ok=True)
    chrome = find_chrome()
    disp_name = (name or data.get("NAME", "") or "memorial").strip()
    paths = []
    for page in range(1, 6):
        if order_id:
            base = f"{order_id} - {disp_name} - {page}"
        else:
            base = f"{disp_name} - {page}"
        safe = "".join(ch for ch in base if ch not in '<>:"/\\|?*').strip()
        out = os.path.join(output_dir, f"{safe}.png")
        render_page(page, data, out, chrome=chrome, scale=scale)
        paths.append(out)
    return paths
