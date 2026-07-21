"""
Page 1: main overview page - rebuilt from precise pixel measurement
of the reference Canva render (reference_page1_v2.png, 1224x1721),
scaled to 2480x3508. All baselines/boxes are measured, not guessed.
Scale: x *= 2480/1224 (2.0261), y *= 3508/1721 (2.0383).
"""

import re
from PIL import Image, ImageDraw, ImageFont
from textfit import _wrap_text, draw_date_with_ordinal, measure_date_with_ordinal

import icons

CANVAS_W, CANVAS_H = 2480, 3508
import os as _os
FONT_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fonts")
PLAYFAIR = f"{FONT_DIR}/PlayfairDisplay-Regular.ttf"
PLAYFAIR_IT = f"{FONT_DIR}/PlayfairDisplay-Italic.ttf"
LIBRE_BASK = f"{FONT_DIR}/LibreBaskerville-Variable.ttf"
LIBRE_BASK_IT = f"{FONT_DIR}/LibreBaskerville-Italic-Variable.ttf"

INK = (26, 26, 26, 255)

# ---- measured geometry (canvas px) ----
MARGIN_L, MARGIN_R = 120, 2357
RULE1_Y, RULE2_Y = 612, 834
VDIV_X = 824
CONTENT_BOTTOM = 3376

CELL1_L, CELL1_R = MARGIN_L, VDIV_X          # col1 cell
CELL1_C = (CELL1_L + CELL1_R) // 2           # 472
CELL2_L, CELL2_R = 851, 1814                 # col2 text area
CELL2_C = (CELL2_L + CELL2_R) // 2
COL3_L, COL3_R = 1875, 2320                  # col3 boxes

STARSIGN_DIR = "assets/starsigns"


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


_ICON_CACHE = {}


def load_icon(name):
    """Load a user-supplied icon PNG, cropped to its visible content."""
    if name in _ICON_CACHE:
        return _ICON_CACHE[name]
    im = Image.open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets", "icons", name)).convert("RGBA")
    bbox = im.getchannel("A").getbbox()
    if bbox:
        im = im.crop(bbox)
    _ICON_CACHE[name] = im
    return im


def paste_icon(canvas, name, cx, cy, w=None, h=None):
    """Paste icon centered at (cx, cy), scaled by width or height (aspect kept)."""
    im = load_icon(name)
    iw, ih = im.size
    if w and not h:
        h = max(1, int(ih * w / iw))
    elif h and not w:
        w = max(1, int(iw * h / ih))
    im = im.resize((int(w), int(h)), Image.LANCZOS)
    canvas.alpha_composite(im, (int(cx - w / 2), int(cy - h / 2)))


def tc(draw, text, font, cx, baseline, fill=INK):
    draw.text((cx, baseline), text, font=font, fill=fill, anchor="ms")


def tl(draw, text, font, x, baseline, fill=INK):
    draw.text((x, baseline), text, font=font, fill=fill, anchor="ls")


def fmt_money(s):
    m = re.match(r"^\$?\s*([\d,]+)$", str(s).strip())
    if m:
        return f"${int(m.group(1).replace(',', '')):,}"
    return s


def fit_paragraphs(draw, paras, box_w, box_h, max_size=52, min_size=30,
                   style="Bold", line_sp=1.18, gap_ratio=0.85, font_fn=None):
    """Single common font size for all paragraphs, shrunk until total fits."""
    font_fn = font_fn or F
    for size in range(max_size, min_size - 1, -1):
        f = font_fn(size, style)
        asc, desc = f.getmetrics()
        lh = int((asc + desc) * line_sp)
        gap = int(size * gap_ratio)
        wrapped = [_wrap_text(draw, p, f, box_w) for p in paras]
        total = sum(len(w) for w in wrapped) * lh + gap * (len(paras) - 1)
        if total <= box_h:
            return f, wrapped, lh, gap
    return f, wrapped, lh, gap


def render_page1(order, output_path):
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # ================= HEADER =================
    # Name: measured band 296-452 (caps), Regular weight, size ~220.
    # Fit within margins with a comfortable side buffer so long names
    # never crowd the border.
    name_text = order["Name"].strip().upper()
    name_max_w = (MARGIN_R - MARGIN_L) - 200  # 100px breathing room each side
    name_size = 220
    while name_size > 90:
        nf = F(name_size)
        if draw.textlength(name_text, font=nf) <= name_max_w:
            break
        name_size -= 4
    nf = F(name_size)
    tc(draw, name_text, nf, CANVAS_W // 2, 452)

    # Date: Libre Baskerville, slightly smaller, a few px lower
    date_size = 88
    prefix = f"{order['DayOfWeek']} {order['MonthName']} "
    suffix = f" {order['Year']}"
    dw = measure_date_with_ordinal(draw, prefix, order["Day"], suffix, LIBRE_BASK, date_size)
    main_f = ImageFont.truetype(LIBRE_BASK, date_size)
    asc, _ = main_f.getmetrics()
    draw_date_with_ordinal(draw, prefix, order["Day"], suffix, LIBRE_BASK,
                           (CANVAS_W - dw) / 2, 568 - asc, date_size, fill=INK)

    # Rules + header between them
    draw.line([(MARGIN_L, RULE1_Y), (MARGIN_R, RULE1_Y)], fill=INK, width=8)
    tc(draw, "ON THE DAY YOU WERE BORN", F(145), CANVAS_W // 2, 781)
    draw.line([(MARGIN_L, RULE2_Y), (MARGIN_R, RULE2_Y)], fill=INK, width=8)

    # Vertical divider (only ONE - col2/col3 has no divider)
    draw.line([(VDIV_X, RULE2_Y), (VDIV_X, CONTENT_BOTTOM)], fill=INK, width=8)

    # ================= COLUMN 1 =================
    # Star sign circle: center (472,1034) r=132, contains STAR SIGN text + glyph
    ccx, ccy, cr = CELL1_C, 1034, 132
    draw.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], outline=INK, width=5)
    ss_font = F(36, "SemiBold")
    tc(draw, "STAR", ss_font, ccx, ccy - 66)
    tc(draw, "SIGN", ss_font, ccx, ccy - 24)
    star_sign = order.get("StarSign", "").strip().lower()
    try:
        glyph = Image.open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets", "starsigns", f"{star_sign}.png")).convert("RGBA")
        # crop to visible content so all signs are placed consistently
        gb = glyph.getchannel("A").getbbox()
        if gb:
            glyph = glyph.crop(gb)
        # fit within a target box (keep aspect), then center in lower half of circle
        target = 80
        gw, gh = glyph.size
        scale = target / max(gw, gh)
        nw, nh = max(1, int(gw * scale)), max(1, int(gh * scale))
        glyph = glyph.resize((nw, nh), Image.LANCZOS)
        glyph_cy = ccy + 44  # fixed center, keeps clear of circle border below
        canvas.alpha_composite(glyph, (int(ccx - nw / 2), int(glyph_cy - nh / 2)))
        draw = ImageDraw.Draw(canvas)
    except FileNotFoundError:
        pass

    # CANCER label: bold caps ~64, baseline 1280
    tc(draw, order.get("StarSign", "").strip().upper(), LB(64, "Bold"), ccx, 1280)

    # Divider under star sign block
    draw.line([(CELL1_L, 1343), (CELL1_R, 1343)], fill=INK, width=8)

    # PM / Incoming PM / Monarch blocks: measured icon tops + text baselines
    blocks = [
        (1423, 161, "australian_flag.png", "Prime Minister", order.get("PrimeMinister", ""), 1661, 1745),
        (1816, 161, "australian_flag_2.png", "Incoming PM", order.get("IncomingPM", ""), 2073, 2155),
        (2234, 150, "british.png", "British Monarch", order.get("Monarch", ""), 2479, 2560),
    ]
    label_f = LB(58, "Bold")
    value_f = LB(58)
    for icon_top, icon_d, icon_file, label, value, lbl_bl, val_bl in blocks:
        paste_icon(canvas, icon_file, ccx, icon_top + icon_d / 2, h=icon_d)
        tc(draw, label, label_f, ccx, lbl_bl)
        # shrink value if too wide for cell
        vf = value_f
        if draw.textlength(value, font=vf) > (CELL1_R - CELL1_L - 40):
            vs = 58
            while vs > 30 and draw.textlength(value, font=LB(vs)) > (CELL1_R - CELL1_L - 40):
                vs -= 2
            vf = LB(vs)
        tc(draw, value, vf, ccx, val_bl)

    # Divider above salary
    draw.line([(CELL1_L, 2674), (CELL1_R, 2674)], fill=INK, width=8)

    # AVERAGE SALARY label
    tc(draw, "AVERAGE SALARY", LB(61), ccx, 2811)

    # Salary rounded box: measured x 188-725, y 2878-3116
    sal_box_top, sal_box_bottom = 2878, 3116
    draw.rounded_rectangle([188, sal_box_top, 725, sal_box_bottom], radius=45, outline=INK, width=5)
    sal_cx = (188 + 725) // 2
    sal_amount_f = LB(84, "Bold")
    per_year_f = LB(40, italic=True)
    amount_txt = fmt_money(order.get("AverageSalary", ""))
    # use real glyph bounding boxes (anchor 'ls' => baseline-left) for true centering
    amt_bbox = draw.textbbox((0, 0), amount_txt, font=sal_amount_f, anchor="ls")
    py_bbox = draw.textbbox((0, 0), "per year", font=per_year_f, anchor="ls")
    amt_top, amt_bot = amt_bbox[1], amt_bbox[3]      # relative to baseline (negative above)
    py_top, py_bot = py_bbox[1], py_bbox[3]
    amt_visible_h = amt_bot - amt_top
    py_visible_h = py_bot - py_top
    inner_gap = 14
    block_h = amt_visible_h + inner_gap + py_visible_h
    box_cy = (sal_box_top + sal_box_bottom) // 2
    block_top = box_cy - block_h / 2
    amount_baseline = block_top - amt_top          # shift so glyph top lands at block_top
    per_year_baseline = amount_baseline + amt_bot + inner_gap - py_top
    tc(draw, amount_txt, sal_amount_f, sal_cx, amount_baseline)
    tc(draw, "per year", per_year_f, sal_cx, per_year_baseline)

    # ================= COLUMN 2 =================
    # FAMOUS BIRTHDAYS (left aligned), baseline 942
    tl(draw, "FAMOUS BIRTHDAYS", LB(66), CELL2_L + 14, 942)

    # Celebrities: bold name - regular role, baselines 1025/1093/1160
    cel_entries = []
    for i in range(1, 4):
        val = order.get(f"Celebrity{i}", "")
        if " - " in val:
            nm, role = val.split(" - ", 1)
        else:
            nm, role = val, ""
        cel_entries.append((nm, role))

    x = CELL2_L + 14
    avail_w = CELL2_R - 30 - x
    size = 40
    while size > 26:
        fits = all(
            draw.textlength(nm, font=LB(size, "Bold")) +
            (draw.textlength(" - " + role, font=LB(size)) if role else 0) <= avail_w
            for nm, role in cel_entries
        )
        if fits:
            break
        size -= 1
    bf, rf = LB(size, "Bold"), LB(size)
    for (nm, role), bl in zip(cel_entries, (1025, 1093, 1160)):
        tl(draw, nm, bf, x, bl)
        if role:
            tl(draw, " - " + role, rf, x + draw.textlength(nm, font=bf), bl)

    # Divider under celebrities: y 1223, thick, to x1779
    draw.line([(CELL2_L, 1227), (1779, 1227)], fill=INK, width=8)

    # IN THE NEWS: centered, size 84, baseline 1333, divider asset underneath
    tc(draw, "IN THE NEWS", F(84), CELL2_C, 1333)
    nw = draw.textlength("IN THE NEWS", font=F(84))
    paste_icon(canvas, "in_the_news_divider.png", CELL2_C, 1370, w=int(nw + 60))

    # News box: x 945-1698 (inset within cell), y 1417-2118
    NB_L, NB_T, NB_R, NB_B = 945, 1417, 1698, 2118
    draw.rectangle([NB_L, NB_T, NB_R, NB_B], outline=INK, width=4)
    pad = 55
    paras = [order.get(f"NewsEvent{i}", "") for i in range(1, 4)]
    f, wrapped, lh, gap = fit_paragraphs(draw, paras, NB_R - NB_L - pad * 2, NB_B - NB_T - pad * 2, font_fn=LB)
    # compute total block height and vertically center within the box
    n_lines = sum(len(wl) for wl in wrapped)
    block_h = n_lines * lh + gap * (len(wrapped) - 1)
    box_inner_h = (NB_B - NB_T) - pad * 2
    top_offset = pad + max(0, (box_inner_h - block_h) / 2)
    ty = NB_T + top_offset + f.getmetrics()[0]
    for wl in wrapped:
        for line in wl:
            tl(draw, line, f, NB_L + pad, ty)
            ty += lh
        ty += gap

    # Thick rule below news box
    draw.line([(CELL2_L, 2168), (CELL2_R, 2168)], fill=INK, width=8)

    # Sports/awards: uniform size across all six, grouped in pairs -
    # tight gap within [NRL,AFL] [Actor,Actress] [Bathurst,AusOpen],
    # visible gap only BETWEEN groups. Full "Men:/Women:" text kept;
    # wraps to a 2nd line when needed (hanging wrap, no overflow).
    entries = [
        ("NRL Winner", order.get("NRLWinner", "")),
        ("AFL Winner", order.get("AFLWinner", "")),
        ("Best Actor", order.get("BestActor", "")),
        ("Best Actress", order.get("BestActress", "")),
        ("Bathurst 1000 Winners", order.get("Bathurst1000", "")),
        ("Australian Open Winners", order.get("AusOpenWinners", "")),
    ]
    lx = CELL2_L + 14
    avail_top, avail_bottom = 2215, 2946
    avail_h = avail_bottom - avail_top
    full_w = CELL2_R - 20 - lx

    def wrap_hanging(value, reg_f, first_w, rest_w):
        words = value.split()
        lines, cur, limit = [], "", first_w
        for wd in words:
            cand = (cur + " " + wd).strip()
            if not cur or draw.textlength(cand, font=reg_f) <= limit:
                cur = cand
            else:
                lines.append(cur)
                cur = wd
                limit = rest_w
        lines.append(cur)
        return lines

    def layout(size):
        bold_f, reg_f = LB(size, "Bold"), LB(size)
        asc, desc = reg_f.getmetrics()
        lh = int((asc + desc) * 1.05)
        pair_gap = int(size * 0.3)
        group_gap = int(size * 1.0)
        per_entry = []
        total = 0
        for label, value in entries:
            label_w = draw.textlength(label + ": ", font=bold_f)
            lines = wrap_hanging(value, reg_f, full_w - label_w, full_w)
            per_entry.append(lines)
            total += len(lines) * lh
        total += pair_gap * 3 + group_gap * 2
        return total, lh, pair_gap, group_gap, bold_f, reg_f, per_entry

    sp_size = 39
    while sp_size > 28:
        total, lh, pair_gap, group_gap, bold_f, reg_f, per_entry = layout(sp_size)
        if total <= avail_h:
            break
        sp_size -= 1

    y = avail_top + reg_f.getmetrics()[0]
    for idx, ((label, value), lines) in enumerate(zip(entries, per_entry)):
        tl(draw, label + ": ", bold_f, lx, y)
        vx = lx + draw.textlength(label + ": ", font=bold_f)
        tl(draw, lines[0], reg_f, vx, y)
        for extra in lines[1:]:
            y += lh
            tl(draw, extra, reg_f, lx, y)
        y += lh
        if idx < len(entries) - 1:
            y += pair_gap if idx % 2 == 0 else group_gap

    # Population boxes: rounded squares with icon + bold value inside.
    # Both boxes share ONE font size (sized to fit the wider value) so
    # World and Australia always match.
    pb_y1 = CONTENT_BOTTOM
    pb_y0 = pb_y1 - 360

    def normalize_pop(v):
        # lowercase the unit words: "3.1 Billion" -> "3.1 billion"
        for unit in ("Billion", "Million", "Thousand"):
            v = v.replace(unit, unit.lower())
        return v

    pop_boxes = [
        (920, 1295, "world_population.png", normalize_pop(order.get("WorldPopulation", ""))),
        (1400, 1775, "australia_population.png", normalize_pop(order.get("AustraliaPopulation", ""))),
    ]
    # find the largest size (<=48) at which BOTH values fit their box width
    box_inner = min(bx1 - bx0 - 30 for bx0, bx1, _, _ in pop_boxes)
    pop_size = 48
    while pop_size > 24:
        if all(draw.textlength(v, font=LB(pop_size, "Bold")) <= box_inner
               for _, _, _, v in pop_boxes):
            break
        pop_size -= 1
    pop_f = LB(pop_size, "Bold")
    for bx0, bx1, icon_file, val in pop_boxes:
        draw.rounded_rectangle([bx0, pb_y0, bx1, pb_y1], radius=40, outline=INK, width=5)
        bcx = (bx0 + bx1) / 2
        paste_icon(canvas, icon_file, bcx, pb_y0 + 135, h=185)
        tc(draw, val, pop_f, bcx, pb_y1 - 55)

    # ================= COLUMN 3 =================
    c3c = (COL3_L + COL3_R) // 2

    # Birthstone box: bottom raised to create a real gap before next box
    draw.rounded_rectangle([COL3_L, 880, COL3_R, 1190], radius=50, outline=INK, width=5)
    box_inner_w = COL3_R - COL3_L - 50
    hs = 61
    while hs > 34 and (60 + 20 + draw.textlength("BIRTHSTONE", font=LB(hs))) > box_inner_w:
        hs -= 2
    hdr_f = LB(hs)
    hw = draw.textlength("BIRTHSTONE", font=hdr_f)
    icon_gap = 20
    total_w = 60 + icon_gap + hw
    hx = c3c - total_w / 2
    paste_icon(canvas, "diamond_stone.png", hx + 30, 966 - 22, w=66)
    tl(draw, "BIRTHSTONE", hdr_f, hx + 60 + icon_gap, 966)
    stone = order.get("Birthstone", "")
    stone_size = 88
    while stone_size > 44 and draw.textlength(stone, font=LB(stone_size)) > (COL3_R - COL3_L - 60):
        stone_size -= 2
    tc(draw, stone, LB(stone_size), c3c, 1099)

    # #1 Single box
    SB_T, SB_B = 1235, 1505
    draw.rounded_rectangle([COL3_L, SB_T, COL3_R, SB_B], radius=50, outline=INK, width=5)
    hw2 = draw.textlength("#1 SINGLE", font=hdr_f)
    total_w2 = 60 + icon_gap + hw2
    hx2 = c3c - total_w2 / 2
    paste_icon(canvas, "record.png", hx2 + 30, 1310 - 22, w=66)
    tl(draw, "#1 SINGLE", hdr_f, hx2 + 60 + icon_gap, 1310)

    song = order.get("Number1Song", "")
    if " - " in song:
        title, artist = song.rsplit(" - ", 1)
        artist = "- " + artist
    else:
        title, artist = song, ""

    # Fit the title+artist block inside the space below the header
    # (header baseline 1310, box bottom SB_B). Shrink + wrap so nothing
    # crosses the border.
    song_zone_top = 1350
    song_zone_bottom = SB_B - 28
    song_zone_h = song_zone_bottom - song_zone_top
    song_w = COL3_R - COL3_L - 70

    def song_layout(size):
        f = LB(size, "Bold")
        asc, desc = f.getmetrics()
        lh = int((asc + desc) * 1.0)
        title_lines = _wrap_text(draw, title, f, song_w)
        artist_lines = _wrap_text(draw, artist, f, song_w) if artist else []
        all_lines = title_lines + artist_lines
        return f, all_lines, lh, lh * len(all_lines)

    ssz = 43
    while ssz > 22:
        sf, slines, slh, sh = song_layout(ssz)
        if sh <= song_zone_h:
            break
        ssz -= 1
    # vertically center the block within the zone
    start_y = song_zone_top + (song_zone_h - sh) / 2 + sf.getmetrics()[0]
    for i, line in enumerate(slines):
        tc(draw, line, sf, c3c, start_y + i * slh)

    # Price stack box: pushed down for a real gap after #1 Single box
    draw.rounded_rectangle([COL3_L, 1550, COL3_R, 2709], radius=50, outline=INK, width=5)
    price_items = [
        ("AVERAGE HOUSE", fmt_money(order.get("AverageHouse", "")), "house.png"),
        ("MILK (1L)", order.get("MilkPrice", ""), "milk.png"),
        ("BREAD (LOAF)", order.get("BreadPrice", ""), "bread.png"),
        ("DOZEN EGGS", order.get("EggsPrice", ""), "egg.png"),
    ]
    n = len(price_items)
    slot = (2709 - 1550 - 60) / n
    plabel_f = LB(32)
    pval_f = LB(40, "Bold")
    for i, (lbl, val, icon_file) in enumerate(price_items):
        sy0 = 1550 + 30 + i * slot
        paste_icon(canvas, icon_file, c3c, sy0 + slot * 0.32, h=105)
        tc(draw, lbl, plabel_f, c3c, sy0 + slot * 0.68)
        tc(draw, str(val), pval_f, c3c, sy0 + slot * 0.88)

    # ---- border overlay ----
    border = Image.open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "assets", "border.png")).convert("RGBA").resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    canvas = Image.alpha_composite(canvas, border)
    canvas.save(output_path)
    return output_path


if __name__ == "__main__":
    import csv
    with open("1996_-_2025.csv", encoding="utf-8", errors="replace") as fcsv:
        rows = list(csv.DictReader(fcsv))
    row = max(rows, key=lambda r: sum(len(r[f"HistoricalEvent{i}"]) for i in range(1, 5)))
    render_page1(row, "output/page1_test.png")
    print("Rendered for", row["Name"])
