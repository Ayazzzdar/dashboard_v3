"""
Page 3: "The Economy in {Year}".
Structure (per reference):
- bigger title, rule below
- circle: bigger, sits BELOW the rule on the right, above the price box
- price box top == petrol icon top ; box bottom == cinema label bottom
- left column: salary, house-cost, petrol, inflation, stamp+cinema
"""

from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 2480, 3508
import os as _os
FONT_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fonts")
PLAYFAIR = f"{FONT_DIR}/PlayfairDisplay-Regular.ttf"
PLAYFAIR_IT = f"{FONT_DIR}/PlayfairDisplay-Italic.ttf"
LIBRE_BASK = f"{FONT_DIR}/LibreBaskerville-Variable.ttf"
LIBRE_BASK_IT = f"{FONT_DIR}/LibreBaskerville-Italic-Variable.ttf"

INK = (0, 0, 0, 255)
NAVY = (29, 111, 196, 255)   # #1d6fc4
WHITE = (255, 255, 255, 255)

MARGIN_L, MARGIN_R = 162, 2318
RULE_Y = 690
LCOL_L = MARGIN_L

# price box: SHORTER (top moved down), bottom near content bottom
RBOX_L, RBOX_R = 1580, 2280
RBOX_T, RBOX_B = 1600, 3230

# circle: bigger, further down, centered over price box, below the rule
CIRCLE_CX = (RBOX_L + RBOX_R) // 2
CIRCLE_R = 400
CIRCLE_CY = RULE_Y + 45 + CIRCLE_R   # top of circle ~45px below rule

def F(size, style=None, italic=False):
    f = ImageFont.truetype(PLAYFAIR_IT if italic else PLAYFAIR, size)
    if style:
        try:
            f.set_variation_by_name(style)
        except Exception:
            pass
    return f


def LB(size, style=None, italic=False):
    f = ImageFont.truetype(LIBRE_BASK_IT if italic else LIBRE_BASK, size)
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


def fmt_money(s):
    import re
    m = re.match(r"^\$?\s*([\d,]+)$", str(s).strip())
    if m:
        return f"${int(m.group(1).replace(',', '')):,}"
    return s


def render_page3(order, output_path):
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    year = order.get("Year", "")

    # ---- Title: Regular weight (matches page 2), tighter title-to-year gap ----
    tc(draw, "THE ECONOMY IN", F(200), CANVAS_W // 2, 393)
    tc(draw, str(year), F(185), CANVAS_W // 2, 622)
    draw.line([(MARGIN_L, RULE_Y), (MARGIN_R, RULE_Y)], fill=INK, width=8)

    # ================= LEFT COLUMN =================
    # AVERAGE SALARY (price bigger)
    tl(draw, "AVERAGE SALARY", LB(68), LCOL_L, 860)
    sal_txt = fmt_money(order.get("AverageSalary", ""))
    # dynamic: salary + "per year" must fit before the circle (x < 1500)
    sal_size = 120
    per_year_f = LB(52, italic=True)
    max_right = CIRCLE_CX - CIRCLE_R - 70
    while sal_size > 70:
        sw = draw.textlength(sal_txt, font=LB(sal_size, "Bold"))
        total = LCOL_L + sw + 34 + draw.textlength("per year", font=per_year_f)
        if total <= max_right:
            break
        sal_size -= 4
    sal_f = LB(sal_size, "Bold")
    tl(draw, sal_txt, sal_f, LCOL_L, 1015)
    sal_w = draw.textlength(sal_txt, font=sal_f)
    tl(draw, "per year", per_year_f, LCOL_L + sal_w + 34, 1015)

    # AVERAGE HOUSE WOULD COST (wages bigger)
    tl(draw, "AVERAGE HOUSE WOULD COST", LB(68), LCOL_L, 1245)
    tl(draw, order.get("YearsOfWages", ""), LB(120, "Bold"), LCOL_L, 1400)

    # PETROL: icon TOP aligned with price box top
    petrol_h = 370
    petrol_cy = RBOX_T + petrol_h // 2
    paste_icon(canvas, "petrol.png", LCOL_L + 185, petrol_cy, h=petrol_h)
    tl(draw, "PETROL (PER LITRE)", LB(68), LCOL_L + 440, petrol_cy - 55)
    tl(draw, order.get("PetrolPrice", ""), LB(100, "Bold"), LCOL_L + 440, petrol_cy + 92)

    # INFLATION
    inflation_cy = petrol_cy + 500
    paste_icon(canvas, "inflation.png", LCOL_L + 185, inflation_cy, h=340)
    tl(draw, "INFLATION RATE", LB(68), LCOL_L + 440, inflation_cy - 55)
    tl(draw, order.get("InflationRate", ""), LB(100, "Bold"), LCOL_L + 440, inflation_cy + 92)

    # STAMP + CINEMA: labels stacked, close to icons,
    # bottom label line aligned with price box bottom
    stamp_cx = LCOL_L + 240
    cinema_cx = LCOL_L + 820
    tickets_cy = inflation_cy + 535
    paste_icon(canvas, "stamp.png", stamp_cx, tickets_cy, h=440)
    paste_icon(canvas, "cinema.png", cinema_cx, tickets_cy, h=360)

    def fit_price(val, max_w, start=96, floor=44):
        s = start
        while s > floor and draw.textlength(val, font=LB(s)) > max_w:
            s -= 2
        return LB(s)

    tc(draw, order.get("StampPrice", ""), fit_price(order.get("StampPrice", ""), 290),
       stamp_cx, tickets_cy + 35)
    tc(draw, order.get("CinemaPrice", ""), fit_price(order.get("CinemaPrice", ""), 430),
       cinema_cx, tickets_cy + 35)

    # stacked labels: second line baseline == RBOX_B (aligned with box bottom)
    lbl_f = LB(50)
    line2_bl = RBOX_B
    line1_bl = line2_bl - 75
    tc(draw, "Postage", lbl_f, stamp_cx, line1_bl)
    tc(draw, "Stamp", lbl_f, stamp_cx, line2_bl)
    tc(draw, "Cinema", lbl_f, cinema_cx, line1_bl)
    tc(draw, "Ticket", lbl_f, cinema_cx, line2_bl)

    # ================= BLUE CADBURY CIRCLE =================
    draw.ellipse([CIRCLE_CX - CIRCLE_R, CIRCLE_CY - CIRCLE_R,
                  CIRCLE_CX + CIRCLE_R, CIRCLE_CY + CIRCLE_R], fill=NAVY)
    # words bigger + higher; bigger gap; price bigger
    tc(draw, "Price of a", LB(76, "Bold"), CIRCLE_CX, CIRCLE_CY - 135, fill=WHITE)
    tc(draw, "Cadbury Bar:", LB(76, "Bold"), CIRCLE_CX, CIRCLE_CY - 45, fill=WHITE)
    tc(draw, order.get("CadburyBarPrice", ""), LB(160, "Bold"), CIRCLE_CX, CIRCLE_CY + 175, fill=WHITE)

    # ================= RIGHT PRICE BOX =================
    draw.rounded_rectangle([RBOX_L, RBOX_T, RBOX_R, RBOX_B], radius=45, outline=INK, width=3)
    rc = (RBOX_L + RBOX_R) // 2
    price_items = [
        ("AVERAGE HOUSE", fmt_money(order.get("AverageHouse", "")), "house.png"),
        ("MILK (1L)", order.get("MilkPrice", ""), "milk.png"),
        ("BREAD (LOAF)", order.get("BreadPrice", ""), "bread.png"),
        ("DOZEN EGGS", order.get("EggsPrice", ""), "egg.png"),
    ]
    n = len(price_items)
    slot = (RBOX_B - RBOX_T - 80) / n
    plabel_f = LB(44)
    pval_f = LB(40, "Bold")
    for i, (lbl, val, icon_file) in enumerate(price_items):
        sy0 = RBOX_T + 40 + i * slot
        paste_icon(canvas, icon_file, rc, sy0 + slot * 0.29, h=140)
        tc(draw, lbl, plabel_f, rc, sy0 + slot * 0.66)
        tc(draw, str(val), pval_f, rc, sy0 + slot * 0.85)

    # ---- border overlay ----
    canvas.alpha_composite(_get_border())
    canvas.save(output_path)
    return output_path


if __name__ == "__main__":
    import csv
    with open("1996_-_2025.csv", encoding="utf-8", errors="replace") as fcsv:
        rows = list(csv.DictReader(fcsv))
    row = next((r for r in rows if r["Year"] == "1961"), rows[0])
    render_page3(row, "output/page3_test.png")
    print("Rendered Page 3 for year", row["Year"])
