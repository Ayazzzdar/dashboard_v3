"""
Core text-fitting engine for The Day Archive Pillow pipeline.

Replaces Canva's "just overflow past the border" behaviour with
auto-scaling: text starts at a target font size and steps down
until it fits the given box, wrapping onto multiple lines as needed.
"""

from PIL import ImageFont, ImageDraw


def ordinal_suffix(day):
    """Returns 'st', 'nd', 'rd', or 'th' for a given day number."""
    day = int(day)
    if 11 <= (day % 100) <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


def draw_date_with_ordinal(
    draw, prefix, day, suffix_extra, font_path, x, y,
    main_size, fill=(26, 26, 26, 255), suffix_ratio=0.55, style_name=None,
):
    """
    Draws text like "November 30th" with the ordinal suffix ('th')
    rendered smaller and raised, matching the Canva superscript style.
    prefix: text before the day number, e.g. "November "
    day: the day number, e.g. 30
    suffix_extra: text after the ordinal, e.g. " 1961" or "" (can be empty)
    Returns the total width drawn.
    """
    main_font = ImageFont.truetype(font_path, main_size)
    suffix_size = max(int(main_size * suffix_ratio), 8)
    suffix_font = ImageFont.truetype(font_path, suffix_size)
    if style_name:
        try:
            main_font.set_variation_by_name(style_name)
            suffix_font.set_variation_by_name(style_name)
        except Exception:
            pass

    ord_suffix = ordinal_suffix(day)
    day_str = str(day)

    cursor_x = x
    # prefix (e.g. "November ")
    if prefix:
        draw.text((cursor_x, y), prefix, font=main_font, fill=fill)
        bbox = draw.textbbox((0, 0), prefix, font=main_font)
        cursor_x += bbox[2] - bbox[0]

    # day number, baseline-aligned
    draw.text((cursor_x, y), day_str, font=main_font, fill=fill)
    day_bbox = draw.textbbox((0, 0), day_str, font=main_font)
    cursor_x += day_bbox[2] - day_bbox[0]

    # ordinal suffix, smaller and raised near the top of the day number
    ascent_main, _ = main_font.getmetrics()
    ascent_suffix, _ = suffix_font.getmetrics()
    raise_offset = ascent_main - ascent_suffix
    draw.text((cursor_x, y + raise_offset * 0.15), ord_suffix, font=suffix_font, fill=fill)
    suffix_bbox = draw.textbbox((0, 0), ord_suffix, font=suffix_font)
    cursor_x += suffix_bbox[2] - suffix_bbox[0]

    # trailing text (e.g. " 1961")
    if suffix_extra:
        draw.text((cursor_x, y), suffix_extra, font=main_font, fill=fill)
        extra_bbox = draw.textbbox((0, 0), suffix_extra, font=main_font)
        cursor_x += extra_bbox[2] - extra_bbox[0]

    return cursor_x - x  # total width


def measure_date_with_ordinal(draw, prefix, day, suffix_extra, font_path, main_size, suffix_ratio=0.55):
    """Same layout math as draw_date_with_ordinal but returns width only (no drawing)."""
    main_font = ImageFont.truetype(font_path, main_size)
    suffix_size = max(int(main_size * suffix_ratio), 8)
    suffix_font = ImageFont.truetype(font_path, suffix_size)
    ord_suffix = ordinal_suffix(day)
    day_str = str(day)

    total = 0
    if prefix:
        bbox = draw.textbbox((0, 0), prefix, font=main_font)
        total += bbox[2] - bbox[0]
    day_bbox = draw.textbbox((0, 0), day_str, font=main_font)
    total += day_bbox[2] - day_bbox[0]
    suffix_bbox = draw.textbbox((0, 0), ord_suffix, font=suffix_font)
    total += suffix_bbox[2] - suffix_bbox[0]
    if suffix_extra:
        extra_bbox = draw.textbbox((0, 0), suffix_extra, font=main_font)
        total += extra_bbox[2] - extra_bbox[0]
    return total


def _wrap_text(draw, text, font, max_width):
    """Greedy word-wrap: returns list of lines that each fit max_width."""
    words = text.split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = current + " " + word
        bbox = draw.textbbox((0, 0), candidate, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def fit_text_in_box(
    draw,
    text,
    font_path,
    box_width,
    box_height,
    max_font_size=48,
    min_font_size=14,
    line_spacing=1.25,
    step=1,
):
    """
    Finds the largest font size (within max/min bounds) at which `text`
    wraps to fit entirely within box_width x box_height.

    Returns (font_object, list_of_lines, actual_line_height).
    If even min_font_size overflows, returns min_font_size wrapped anyway
    (never shrinks below min â€” caller can decide to truncate or accept
    a slight overflow, but this never goes below legible size).
    """
    for size in range(max_font_size, min_font_size - 1, -step):
        font = ImageFont.truetype(font_path, size)
        lines = _wrap_text(draw, text, font, box_width)

        ascent, descent = font.getmetrics()
        line_height = int((ascent + descent) * line_spacing)
        total_height = line_height * len(lines)

        if total_height <= box_height:
            return font, lines, line_height

    # Fallback: min size, wrapped, even if it slightly overflows height
    font = ImageFont.truetype(font_path, min_font_size)
    lines = _wrap_text(draw, text, font, box_width)
    ascent, descent = font.getmetrics()
    line_height = int((ascent + descent) * line_spacing)
    return font, lines, line_height


def draw_fitted_text(
    draw,
    text,
    font_path,
    x,
    y,
    box_width,
    box_height,
    fill=(20, 20, 20, 255),
    max_font_size=48,
    min_font_size=14,
    line_spacing=1.25,
    align="left",
):
    """Fits and draws text within the box starting at (x, y)."""
    font, lines, line_height = fit_text_in_box(
        draw, text, font_path, box_width, box_height,
        max_font_size, min_font_size, line_spacing
    )

    cursor_y = y
    for line in lines:
        if align == "center":
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_x = x + (box_width - line_width) / 2
        else:
            line_x = x
        draw.text((line_x, cursor_y), line, font=font, fill=fill)
        cursor_y += line_height

    return cursor_y  # returns bottom y-coordinate after last line
