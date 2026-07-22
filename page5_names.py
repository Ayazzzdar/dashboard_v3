"""
Page 5: "Top Baby Names {Year}".
Title + year (Playfair Regular), two short rules flanking the blue pram
icon, BOYS / GIRLS headers (LB Bold), and numbered 1-10 name lists
(bold numbers, regular names, Libre Baskerville).
Geometry measured from the Canva reference.
"""

from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 2480, 3508
import os as _os
FONT_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fonts")
PLAYFAIR = f"{FONT_DIR}/PlayfairDisplay-Regular.ttf"
LIBRE_BASK = f"{FONT_DIR}/LibreBaskerville-Variable.ttf"

INK = (0, 0, 0, 255)

MARGIN_L, MARGIN_R = 162, 2318

# pram between two short rules
PRAM_CY = 848
PRAM_H = 365
RULE_Y = 845

# columns
BOYS_CX, GIRLS_CX = 610, 1745
BOYS_NUM_X, BOYS_NAME_X = 220, 425
GIRLS_NUM_X, GIRLS_NAME_X = 1345, 1550
HEADER_BL = 1180
LIST_START_BL = 1432
LIST_PITCH = 180

def F(size, style=None):
    f = ImageFont.truetype(PLAYFAIR, size)
    if style:
        try:
            f.set_variation_by_name(style)
        except Exception:
            pass
    return f


def LB(size, style=None):
    f = ImageFont.truetype(LIBRE_BASK, size)
    try:
        f.set_variation_by_name(style if style else "Regular")
    except Exception:
        pass
    return f


_BORDER_CACHE = None


def _get_border():
    """Load and resize the border once, then reuse it for every page.
    Re-decoding + LANCZOS-resizing a full-page RGBA image on every render
    was a major source of peak memory on large batches."""
    global _BORDER_CACHE
    if _BORDER_CACHE is None:
        _p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                           "assets", "border.png")
        _BORDER_CACHE = Image.open(_p).convert("RGBA").resize(
            (CANVAS_W, CANVAS_H), Image.LANCZOS)
    return _BORDER_CACHE


_ICON_CACHE = {}       # (name, w, h) -> resized RGBA icon
_ICON_SIZE_CACHE = {}  # name -> (w, h) of the alpha-cropped source


def _icon_path(name):
    return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                         "assets", "icons", name)


def _load_icon_source(name):
    """Decode + alpha-crop an icon. Deliberately NOT cached: the source
    files are ~3000px (~30 MB each in RAM). We only cache the small
    resized versions actually drawn, which keeps peak memory low on
    large batches while producing identical output."""
    im = Image.open(_icon_path(name)).convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    if bbox:
        im = im.crop(bbox)
    return im


def _icon_size(name):
    """Cropped source dimensions (cached), without holding the pixels."""
    if name not in _ICON_SIZE_CACHE:
        src = _load_icon_source(name)
        _ICON_SIZE_CACHE[name] = src.size
        src.close()
    return _ICON_SIZE_CACHE[name]


def load_icon(name):
    """Compatibility shim - returns the alpha-cropped source image."""
    return _load_icon_source(name)


def paste_icon(canvas, name, cx, cy, w=None, h=None):
    iw, ih = _icon_size(name)
    if w and not h:
        h = max(1, int(ih * w / iw))
    elif h and not w:
        w = max(1, int(iw * h / ih))
    w, h = int(w), int(h)
    key = (name, w, h)
    im = _ICON_CACHE.get(key)
    if im is None:
        src = _load_icon_source(name)
        im = src.resize((w, h), Image.LANCZOS)
        src.close()
        _ICON_CACHE[key] = im
    canvas.alpha_composite(im, (int(cx - w / 2), int(cy - h / 2)))
    return w, h
def tc(draw, text, font, cx, baseline, fill=INK):
    draw.text((cx, baseline), text, font=font, fill=fill, anchor="ms")


def tl(draw, text, font, x, baseline, fill=INK):
    draw.text((x, baseline), text, font=font, fill=fill, anchor="ls")


def render_page5(order, output_path):
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    year = str(order.get("Year", ""))

    # ---- Title: Regular Playfair sized to span ~1624px ----
    tsize = 160
    while tsize < 250:
        if draw.textlength("TOP BABY NAMES", font=F(tsize)) >= 1624:
            break
        tsize += 2
    tc(draw, "TOP BABY NAMES", F(tsize), CANVAS_W // 2, 368)
    ysize = 140
    while ysize < 220 and draw.textlength(year, font=F(ysize)) < 400:
        ysize += 2
    tc(draw, year, F(ysize), CANVAS_W // 2, 588)

    # ---- Pram icon + flanking rules ----
    pw, ph = paste_icon(canvas, "pram.png", CANVAS_W // 2, PRAM_CY, h=PRAM_H)
    draw = ImageDraw.Draw(canvas)
    gap = 90
    pram_l = CANVAS_W // 2 - pw // 2
    pram_r = CANVAS_W // 2 + pw // 2
    draw.line([(MARGIN_L, RULE_Y), (pram_l - gap, RULE_Y)], fill=INK, width=6)
    draw.line([(pram_r + gap, RULE_Y), (MARGIN_R, RULE_Y)], fill=INK, width=6)

    # ---- BOYS / GIRLS headers ----
    hdr_f = LB(165, "Bold")
    tc(draw, "BOYS", hdr_f, BOYS_CX, HEADER_BL)
    tc(draw, "GIRLS", hdr_f, GIRLS_CX, HEADER_BL)

    # ---- Name lists: bold numbers, regular names ----
    # one shared size for all 20 entries, shrunk if any name is too wide
    def fits(size):
        nf = LB(size)
        for i in range(1, 11):
            for prefix, name_x, col_r in (
                ("BoyName", BOYS_NAME_X, GIRLS_NUM_X - 80),
                ("GirlName", GIRLS_NAME_X, MARGIN_R - 20),
            ):
                nm = order.get(f"{prefix}{i}", "")
                if name_x + draw.textlength(nm, font=nf) > col_r:
                    return False
        return True

    nsize = 115
    while nsize > 70 and not fits(nsize):
        nsize -= 2
    num_f = LB(nsize, "Bold")
    name_f = LB(nsize)

    for i in range(1, 11):
        bl = LIST_START_BL + (i - 1) * LIST_PITCH
        num = f"{i}."
        # right-align numbers so single- and double-digit end at the same x
        # (the point just left of the name column), matching the reference
        bnw = draw.textlength(num, font=num_f)
        gnw = draw.textlength(num, font=num_f)
        tl(draw, num, num_f, BOYS_NAME_X - 40 - bnw, bl)
        tl(draw, order.get(f"BoyName{i}", ""), name_f, BOYS_NAME_X, bl)
        tl(draw, num, num_f, GIRLS_NAME_X - 40 - gnw, bl)
        tl(draw, order.get(f"GirlName{i}", ""), name_f, GIRLS_NAME_X, bl)

    # ---- border overlay ----
    canvas.alpha_composite(_get_border())
    canvas.save(output_path)
    return output_path


if __name__ == "__main__":
    import csv
    with open("1996_-_2025.csv", encoding="utf-8", errors="replace") as fcsv:
        rows = list(csv.DictReader(fcsv))
    row = next((r for r in rows if r["Year"] == "1961"), rows[0])
    render_page5(row, "output/page5_test.png")
    print("Rendered Page 5 for year", row["Year"])
