"""
Page 2: "Your Day In Archive" - 4 stacked historical events.

This is the highest overflow-risk page (HistoricalEvent fields range
142-221 chars in real data). Font auto-scales per-entry so every
entry fits its row regardless of length, with the year rendered
separately (never affected by scaling).
"""

from PIL import Image, ImageDraw, ImageFont
from textfit import fit_text_in_box, draw_fitted_text, draw_date_with_ordinal, measure_date_with_ordinal

# ---- Canvas setup: A4 at 300dpi, matches border.png aspect ratio ----
CANVAS_W, CANVAS_H = 2480, 3508

import os as _os
FONT_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "fonts")
PLAYFAIR = f"{FONT_DIR}/PlayfairDisplay-Regular.ttf"
CORMORANT = f"{FONT_DIR}/CormorantGaramond-Variable.ttf"

# Brand colors
INK = (0, 0, 0, 255)
NAVY = (30, 58, 138, 255)  # kept for other elements; dividers now use INK

# Layout margins (px, relative to 2480x3508 canvas)
MARGIN_X = 260
CONTENT_TOP = 560
CONTENT_BOTTOM = CANVAS_H - 300

YEAR_COL_WIDTH = 480
DIVIDER_X = MARGIN_X + YEAR_COL_WIDTH + 40
TEXT_COL_X = DIVIDER_X + 60
TEXT_COL_WIDTH = CANVAS_W - MARGIN_X - TEXT_COL_X


_BORDER_CACHE = None


def _get_border():
    """Load and resize the border once, then reuse it for every page.
    Re-decoding + LANCZOS-resizing a full-page RGBA image on every render
    was the main source of peak memory on large batches."""
    global _BORDER_CACHE
    if _BORDER_CACHE is None:
        _p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                           "assets", "border.png")
        _BORDER_CACHE = Image.open(_p).convert("RGBA").resize(
            (CANVAS_W, CANVAS_H), Image.LANCZOS)
    return _BORDER_CACHE


def set_variation(font, style_name):
    try:
        font.set_variation_by_name(style_name)
    except Exception:
        pass
    return font


def render_page2(order, output_path):
    """
    order: dict with keys MonthName, Day,
           HistoricalEventDate1-4 (e.g. "1874"), HistoricalEvent1-4
    """
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # ---- Title: Regular weight, sized so "IN ARCHIVE" spans ~1025px (ref) ----
    tsize = 150
    while tsize < 240:
        tf = ImageFont.truetype(PLAYFAIR, tsize)
        if draw.textlength("IN ARCHIVE", font=tf) >= 1025:
            break
        tsize += 2
    title_font = ImageFont.truetype(PLAYFAIR, tsize)
    draw.text((CANVAS_W // 2, 344), "YOUR DAY", font=title_font, fill=INK, anchor="ms")
    draw.text((CANVAS_W // 2, 529), "IN ARCHIVE", font=title_font, fill=INK, anchor="ms")

    # ---- Subtitle (date, with ordinal) - bigger, with a real gap above rule ----
    subtitle_size = 90
    subtitle_width = measure_date_with_ordinal(
        draw, f"{order['MonthName']} ", order['Day'], "", PLAYFAIR, subtitle_size
    )
    subtitle_x = (CANVAS_W - subtitle_width) / 2
    _df = ImageFont.truetype(PLAYFAIR, subtitle_size)
    _asc, _ = _df.getmetrics()
    draw_date_with_ordinal(
        draw, f"{order['MonthName']} ", order['Day'], "", PLAYFAIR,
        subtitle_x, 714 - _asc, subtitle_size, fill=INK
    )

    # ---- Horizontal rule ----
    rule_y = 804
    draw.line([(MARGIN_X, rule_y), (CANVAS_W - MARGIN_X, rule_y)], fill=INK, width=4)

    # ---- 4 historical event rows ----
    n_rows = 4
    row_area_top = rule_y + 60
    row_area_height = CONTENT_BOTTOM - row_area_top
    row_height = row_area_height // n_rows

    year_font = ImageFont.truetype(PLAYFAIR, 160)
    # symmetric gaps: border->year gap == year->divider gap
    max_year_w = max(
        draw.textlength(str(order.get(f"HistoricalEventDate{i}", "")), font=year_font)
        for i in range(1, n_rows + 1)
    )
    left_gap = MARGIN_X - 95  # distance from dotted border to year
    div_x = MARGIN_X + max_year_w + left_gap
    text_x = div_x + 60
    text_w = CANVAS_W - MARGIN_X - text_x

    for i in range(1, n_rows + 1):
        row_top = row_area_top + (i - 1) * row_height
        row_center_y = row_top + row_height / 2

        date_val = str(order.get(f"HistoricalEventDate{i}", ""))
        event_text = order.get(f"HistoricalEvent{i}", "")

        # Year (left column) - vertically centered in row
        ybbox = draw.textbbox((0, 0), date_val, font=year_font)
        yh = ybbox[3] - ybbox[1]
        draw.text(
            (MARGIN_X, row_center_y - yh / 2 - ybbox[1]),
            date_val, font=year_font, fill=INK
        )

        # Vertical divider for this row
        divider_pad = 55
        draw.line(
            [(div_x, row_top + divider_pad), (div_x, row_top + row_height - divider_pad)],
            fill=INK, width=5
        )

        # Event description - auto-scaled to fit row box
        body_font, lines, line_h = fit_text_in_box(
            draw, event_text, CORMORANT,
            box_width=text_w,
            box_height=row_height - 40,
            max_font_size=65,
            min_font_size=34,
            line_spacing=1.3,
        )
        set_variation(body_font, "Regular")

        text_block_height = line_h * len(lines)
        text_start_y = row_center_y - text_block_height / 2

        cy = text_start_y
        for li, line in enumerate(lines):
            is_last = (li == len(lines) - 1)
            if is_last or " " not in line:
                draw.text((text_x, cy), line, font=body_font, fill=INK)
            else:
                # full justification: distribute extra space between words
                words = line.split(" ")
                widths = [draw.textlength(wd, font=body_font) for wd in words]
                extra = text_w - sum(widths)
                gap = extra / (len(words) - 1) if len(words) > 1 else 0
                wx = text_x
                for wd, ww in zip(words, widths):
                    draw.text((wx, cy), wd, font=body_font, fill=INK)
                    wx += ww + gap
            cy += line_h

    # ---- Composite border on top ----
    canvas.alpha_composite(_get_border())

    canvas.save(output_path)
    return output_path


if __name__ == "__main__":
    # Stress test: Winston Churchill entry (221 chars) as the ceiling,
    # mixed with shorter entries to confirm no giant empty gaps either.
    stress_order = {
        "MonthName": "November",
        "Day": "30",
        "HistoricalEventDate1": "1874",
        "HistoricalEvent1": (
            "On November 30, 1874, Winston Churchill was born at Blenheim Palace "
            "in Oxfordshire, England, to Lord Randolph Churchill and his American "
            "wife Jennie Jerome, beginning the life of one of history's greatest "
            "wartime leaders."
        ),
        "HistoricalEventDate2": "1931",
        "HistoricalEvent2": (
            "On September 18, 1931, Japanese forces staged the Mukden Incident in "
            "Manchuria, using it as a pretext to invade and occupy northeastern China."
        ),
        "HistoricalEventDate3": "1978",
        "HistoricalEvent3": (
            "On September 17, 1978, Egyptian President Anwar Sadat and Israeli "
            "Prime Minister Menachem Begin signed the Camp David Accords, brokered "
            "by US President Jimmy Carter, establishing a framework for Middle "
            "East peace."
        ),
        "HistoricalEventDate4": "2010",
        "HistoricalEvent4": (
            "On July 24, 2010, a crowd crush disaster at the Love Parade music "
            "festival in Duisburg, Germany, killed 21 people and injured over 500 others."
        ),
    }
    render_page2(stress_order, "output/page2_stress_test.png")
    print("Rendered output/page2_stress_test.png")
