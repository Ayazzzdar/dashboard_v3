"""
Page 4: "A Cultural Snapshot of {Year}".
Title (Playfair Regular, 2 lines) + blue year pill + rule, then five
icon rows: Top Selling Book, TV Highlights, Fashion Trend, Technology,
AU Births - each with header (LB caps), italic name, and wrapped
description. Geometry measured from the Canva reference.
"""

from PIL import Image, ImageDraw, ImageFont
from textfit import _wrap_text
import icons

CANVAS_W, CANVAS_H = 2480, 3508
import os as _os
FONT_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fonts")
PLAYFAIR = f"{FONT_DIR}/PlayfairDisplay-Regular.ttf"
LIBRE_BASK = f"{FONT_DIR}/LibreBaskerville-Variable.ttf"
LIBRE_BASK_IT = f"{FONT_DIR}/LibreBaskerville-Italic-Variable.ttf"

INK = (26, 26, 26, 255)
NAVY = (29, 111, 196, 255)
WHITE = (255, 255, 255, 255)

MARGIN_L, MARGIN_R = 162, 2318
RULE_Y = 813

ICON_CX = 380
TEXT_X = 660
TEXT_R = 2210
ICON_MAX_W = 360
ICON_MAX_H = 400

ROW_CENTERS = [1100, 1566, 2032, 2498, 2964]

_ICON_CACHE = {}


def F(size, style=None):
    f = ImageFont.truetype(PLAYFAIR, size)
    if style:
        try:
            f.set_variation_by_name(style)
        except Exception:
            pass
    return f


def LB(size, style=None, italic=False):
    f = ImageFont.truetype(LIBRE_BASK_IT if italic else LIBRE_BASK, size)
    try:
        f.set_variation_by_name(style if style else ("Italic" if italic else "Regular"))
    except Exception:
        pass
    return f


def tc(draw, text, font, cx, baseline, fill=INK):
    draw.text((cx, baseline), text, font=font, fill=fill, anchor="ms")


def load_icon(name):
    if name in _ICON_CACHE:
        return _ICON_CACHE[name]
    im = Image.open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets", "icons", name)).convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    if bbox:
        im = im.crop(bbox)
    _ICON_CACHE[name] = im
    return im


def paste_icon(canvas, name, cx, cy, w=None, h=None):
    im = load_icon(name)
    iw, ih = im.size
    if w and not h:
        h = max(1, int(ih * w / iw))
    elif h and not w:
        w = max(1, int(iw * h / ih))
    im = im.resize((int(w), int(h)), Image.LANCZOS)
    canvas.alpha_composite(im, (int(cx - w / 2), int(cy - h / 2)))


def tl(draw, text, font, x, baseline, fill=INK):
    draw.text((x, baseline), text, font=font, fill=fill, anchor="ls")


def render_page4(order, output_path):
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    year = str(order.get("Year", ""))

    # ---- Title: Regular Playfair sized so line 2 spans ~1214px ----
    tsize = 150
    while tsize < 230:
        tf = F(tsize)
        if draw.textlength("SNAPSHOT OF", font=tf) >= 1214:
            break
        tsize += 2
    title_f = F(tsize)
    tc(draw, "A CULTURAL", title_f, CANVAS_W // 2, 339)
    tc(draw, "SNAPSHOT OF", title_f, CANVAS_W // 2, 524)

    # ---- Blue year pill ----
    PILL_L, PILL_R, PILL_T, PILL_B = 936, 1542, 598, 767
    draw.rounded_rectangle([PILL_L, PILL_T, PILL_R, PILL_B],
                           radius=(PILL_B - PILL_T) // 2, fill=NAVY)
    tc(draw, year, LB(96, "Bold"), (PILL_L + PILL_R) // 2, 717, fill=WHITE)

    # ---- Rule ----
    draw.line([(MARGIN_L, RULE_Y), (MARGIN_R, RULE_Y)], fill=INK, width=8)

    # ---- Five rows (real PNG icons, heights matched to reference) ----
    rows = [
        ("TOP SELLING BOOK", order.get("TopBook", ""), order.get("TopBookDescription", ""),
         "book.png", 400),
        ("TV HIGHLIGHTS", order.get("TVShow", ""), order.get("TVShowDescription", ""),
         "tv.png", 330),
        ("FASHION TREND", order.get("FashionTrend", ""), order.get("FashionDescription", ""),
         "clothing.png", 400),
        ("TECHNOLOGY", order.get("Technology", ""), order.get("TechnologyDescription", ""),
         "tech.png", 420),
        ("AU BIRTHS", order.get("AustraliaBirths", ""), order.get("BirthsDescription", ""),
         "baby.png", 340),
    ]

    header_f = LB(66)
    name_f = LB(62, italic=True)
    text_w = TEXT_R - TEXT_X

    for (header, name, desc, icon_file, icon_h), cy in zip(rows, ROW_CENTERS):
        # fit each icon inside a fixed box (keeps a consistent left-border gap
        # and never reaches the text column)
        im = load_icon(icon_file)
        iw, ih = im.size
        scale = min(ICON_MAX_W / iw, ICON_MAX_H / ih)
        paste_icon(canvas, icon_file, ICON_CX, cy, h=int(ih * scale))
        draw = ImageDraw.Draw(canvas)

        header_bl = cy - 90
        tl(draw, header, header_f, TEXT_X, header_bl)

        # italic name - shrink if too wide for the column
        nsize = 62
        while nsize > 40 and draw.textlength(name, font=LB(nsize, italic=True)) > text_w:
            nsize -= 2
        tl(draw, name, LB(nsize, italic=True), TEXT_X, header_bl + 92)

        # description: wrapped, auto-shrink so it stays within the row
        dsize = 40
        while dsize > 30:
            df = LB(dsize)
            lines = _wrap_text(draw, desc, df, text_w)
            if len(lines) <= 3:
                break
            dsize -= 2
        df = LB(dsize)
        lines = _wrap_text(draw, desc, df, text_w)
        line_pitch = int(dsize * 1.55)
        dy = header_bl + 92 + 108
        for li, line in enumerate(lines):
            is_last = (li == len(lines) - 1)
            if is_last or " " not in line:
                tl(draw, line, df, TEXT_X, dy)
            else:
                # full justification: distribute extra space between words
                words = line.split(" ")
                widths = [draw.textlength(wd, font=df) for wd in words]
                extra = text_w - sum(widths)
                gap = extra / (len(words) - 1) if len(words) > 1 else 0
                wx = TEXT_X
                for wd, ww in zip(words, widths):
                    draw.text((wx, dy), wd, font=df, fill=INK, anchor="ls")
                    wx += ww + gap
            dy += line_pitch

    # ---- border overlay ----
    border = Image.open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets", "border.png")).convert("RGBA").resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    canvas = Image.alpha_composite(canvas, border)
    canvas.save(output_path)
    return output_path


if __name__ == "__main__":
    import csv
    with open("1996_-_2025.csv", encoding="utf-8", errors="replace") as fcsv:
        rows = list(csv.DictReader(fcsv))
    row = next((r for r in rows if r["Year"] == "1961"), rows[0])
    render_page4(row, "output/page4_test.png")
    print("Rendered Page 4 for year", row["Year"])
