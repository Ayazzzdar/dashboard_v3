"""
Simple black line-art icons drawn directly with Pillow primitives.
These are placeholders matching the general style/weight of the
Canva original (flags, crown, house, milk bottle, bread, egg,
globe, birthstone, record). Swap for real vector assets later by
replacing these functions with image-paste calls - the layout code
that positions them won't need to change.
"""

from PIL import ImageDraw


def draw_crown(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Simple 3-point crown icon centered at (cx, cy)."""
    w, h = size, size * 0.75
    left = cx - w / 2
    top = cy - h / 2
    base_y = top + h * 0.7
    points = [
        (left, base_y),
        (left, top + h * 0.35),
        (left + w * 0.2, top + h * 0.55),
        (left + w * 0.5, top),
        (left + w * 0.8, top + h * 0.55),
        (left + w, top + h * 0.35),
        (left + w, base_y),
    ]
    draw.polygon(points, fill=fill)
    draw.rectangle([left, base_y, left + w, base_y + h * 0.25], fill=fill)


def draw_house(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    w, h = size, size * 0.85
    left = cx - w / 2
    top = cy - h / 2
    roof_peak = (cx, top)
    roof_l = (left, top + h * 0.4)
    roof_r = (left + w, top + h * 0.4)
    draw.polygon([roof_peak, roof_l, roof_r], fill=fill)
    body_top = top + h * 0.35
    draw.rectangle([left + w * 0.12, body_top, left + w * 0.88, top + h], fill=fill)


def draw_milk_bottle(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    w, h = size * 0.55, size
    left = cx - w / 2
    top = cy - h / 2
    neck_w = w * 0.4
    draw.rectangle([cx - neck_w / 2, top, cx + neck_w / 2, top + h * 0.25], fill=fill)
    draw.polygon([
        (cx - neck_w / 2, top + h * 0.22), (cx + neck_w / 2, top + h * 0.22),
        (left + w, top + h * 0.4), (left, top + h * 0.4),
    ], fill=fill)
    draw.rounded_rectangle([left, top + h * 0.38, left + w, top + h], radius=w * 0.15, fill=fill)


def draw_bread(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Loaf silhouette: rounded dome top, flat-ish base, with a couple of score marks."""
    w, h = size, size * 0.65
    left = cx - w / 2
    top = cy - h / 2
    bottom = cy + h / 2
    draw.rounded_rectangle([left, top, left + w, bottom], radius=h * 0.5, fill=fill)
    # scoring lines (diagonal cuts) in the cream/background color to read as texture
    bg = (245, 240, 232, 255)
    for i in range(3):
        lx = left + w * (0.3 + i * 0.22)
        draw.line([(lx, top + h * 0.15), (lx - w * 0.08, bottom - h * 0.15)], fill=bg, width=max(int(size * 0.03), 2))


def draw_egg(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    w, h = size * 0.62, size * 0.85
    # true egg shape: narrower top, wider bottom (approximate with two arcs via polygon)
    top = cy - h / 2
    bottom = cy + h / 2
    points = []
    import math
    for t in range(0, 361, 10):
        a = math.radians(t)
        # egg profile: radius varies with angle for a pointed top
        rx = w / 2 * (1 - 0.18 * math.cos(a))
        ry = h / 2
        px = cx + rx * math.sin(a)
        py = cy - ry * math.cos(a)
        points.append((px, py))
    draw.polygon(points, fill=fill)


def draw_flag_circle(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Circular badge with a simplified Southern Cross (Australian flag reference)."""
    r = size / 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    bg = (245, 240, 232, 255)
    import math

    def star(sx, sy, sr):
        pts = []
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            rad = sr if i % 2 == 0 else sr * 0.42
            pts.append((sx + rad * math.cos(ang), sy - rad * math.sin(ang)))
        draw.polygon(pts, fill=bg)

    # Southern Cross-style star cluster, scaled to badge size
    star(cx - r * 0.05, cy - r * 0.42, r * 0.16)
    star(cx + r * 0.32, cy - r * 0.05, r * 0.14)
    star(cx + r * 0.02, cy + r * 0.40, r * 0.16)
    star(cx - r * 0.35, cy + r * 0.15, r * 0.12)
    star(cx - r * 0.32, cy - r * 0.10, r * 0.10)


def draw_globe(draw, cx, cy, size, fill=(26, 26, 26, 255), width=6):
    r = size / 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fill, width=width)
    draw.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=fill, width=width)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=fill, width=width)
    draw.line([(cx - r, cy - r * 0.5), (cx + r, cy - r * 0.5)], fill=fill, width=max(width - 2, 2))
    draw.line([(cx - r, cy + r * 0.5), (cx + r, cy + r * 0.5)], fill=fill, width=max(width - 2, 2))


def draw_diamond(draw, cx, cy, size, fill=(26, 26, 26, 255), width=6):
    w, h = size, size * 0.85
    top = (cx, cy - h / 2)
    bottom = (cx, cy + h / 2)
    left = (cx - w / 2, cy - h * 0.15)
    right = (cx + w / 2, cy - h * 0.15)
    draw.polygon([top, right, bottom, left], outline=fill, width=width)
    draw.line([left, right], fill=fill, width=max(width - 2, 2))


def draw_record(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    r = size / 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    inner_r = r * 0.32
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=(245, 240, 232, 255))
    center_r = r * 0.08
    draw.ellipse([cx - center_r, cy - center_r, cx + center_r, cy + center_r], fill=fill)


def draw_australia(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Simplified Australia silhouette."""
    s = size / 100.0
    pts = [
        (18, 42), (14, 52), (16, 62), (22, 70), (30, 74), (38, 78),
        (48, 80), (58, 78), (66, 74), (74, 68), (80, 58), (84, 48),
        (86, 38), (82, 30), (76, 26), (72, 30), (68, 26), (62, 20),
        (56, 24), (50, 20), (44, 16), (40, 22), (34, 20), (28, 26),
        (24, 34),
    ]
    poly = [(cx + (px - 50) * s, cy + (py - 48) * s) for px, py in pts]
    draw.polygon(poly, fill=fill)
    # Tasmania
    tx, ty = cx + (60 - 50) * s, cy + (88 - 48) * s
    draw.ellipse([tx - 5 * s, ty - 4 * s, tx + 5 * s, ty + 4 * s], fill=fill)


def draw_petrol(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Petrol pump silhouette."""
    w, h = size * 0.7, size
    left, top = cx - w / 2, cy - h / 2
    # pump body
    draw.rounded_rectangle([left, top, left + w * 0.62, top + h], radius=size * 0.05, outline=fill, width=max(int(size*0.05),4))
    # display window
    draw.rectangle([left + w*0.12, top + h*0.12, left + w*0.5, top + h*0.32], fill=fill)
    # droplet
    draw.ellipse([left + w*0.16, top + h*0.5, left + w*0.46, top + h*0.8], fill=fill)
    # hose/nozzle on right
    draw.line([(left + w*0.62, top + h*0.25),(left + w*0.9, top + h*0.25)], fill=fill, width=max(int(size*0.05),4))
    draw.line([(left + w*0.9, top + h*0.25),(left + w*0.9, top + h*0.55)], fill=fill, width=max(int(size*0.05),4))


def draw_inflation(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Rising bar chart with arrow."""
    w, h = size, size * 0.85
    left, base = cx - w/2, cy + h/2
    bw = w * 0.18
    heights = [0.35, 0.55, 0.78]
    for i, bh in enumerate(heights):
        bx = left + i * bw * 1.3
        draw.rectangle([bx, base - h*bh, bx + bw, base], fill=fill)
    # arrow rising
    ax0, ay0 = left, base - h*0.35
    ax1, ay1 = left + w*0.75, base - h*0.9
    draw.line([(ax0,ay0),(ax1,ay1)], fill=fill, width=max(int(size*0.05),4))
    draw.polygon([(ax1,ay1),(ax1-size*0.14,ay1+size*0.04),(ax1-size*0.04,ay1+size*0.14)], fill=fill)


def draw_stamp(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Postage stamp with perforated edge."""
    w = h = size * 0.9
    left, top = cx - w/2, cy - h/2
    # perforated border via small circles subtracted look - just draw dashed rect
    draw.rectangle([left, top, left+w, top+h], outline=fill, width=max(int(size*0.045),4))
    # inner frame
    draw.rectangle([left+w*0.14, top+h*0.14, left+w*0.86, top+h*0.86], outline=fill, width=max(int(size*0.03),3))


def draw_cinema(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Cinema/movie ticket."""
    w, h = size, size * 0.6
    left, top = cx - w/2, cy - h/2
    draw.rounded_rectangle([left, top, left+w, top+h], radius=size*0.06, outline=fill, width=max(int(size*0.045),4))
    # notches
    r = size*0.06
    draw.ellipse([cx-r, top-r, cx+r, top+r], fill=(245,240,232,255), outline=fill, width=3)
    draw.ellipse([cx-r, top+h-r, cx+r, top+h+r], fill=(245,240,232,255), outline=fill, width=3)


def draw_books(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Stack of 3 books, slightly offset."""
    w = size; h = size * 0.24
    for i, (dx, dy) in enumerate([(0.06, 0.62), (-0.02, 0.34), (0.03, 0.05)]):
        left = cx - w/2 + dx*w
        top = cy - size/2 + dy*size
        draw.rounded_rectangle([left, top, left + w*0.92, top + h], radius=size*0.03, fill=fill)
        # spine line
        draw.line([(left + w*0.1, top + h*0.5), (left + w*0.82, top + h*0.5)],
                  fill=(245,240,232,255), width=max(int(size*0.02), 2))


def draw_tv(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Retro TV with antenna."""
    w, h = size, size * 0.62
    top = cy - h/2 + size*0.10
    left = cx - w/2
    # antenna
    lw = max(int(size*0.035), 3)
    draw.line([(cx, top), (cx - size*0.16, top - size*0.20)], fill=fill, width=lw)
    draw.line([(cx, top), (cx + size*0.16, top - size*0.20)], fill=fill, width=lw)
    draw.rounded_rectangle([left, top, left + w, top + h], radius=size*0.08, fill=fill)
    # screen
    draw.rounded_rectangle([left + w*0.08, top + h*0.12, left + w*0.68, top + h*0.88],
                           radius=size*0.04, fill=(245,240,232,255))
    # knobs
    for ky in (0.3, 0.55):
        r = size*0.035
        draw.ellipse([left + w*0.8 - r, top + h*ky - r, left + w*0.8 + r, top + h*ky + r],
                     fill=(245,240,232,255))


def draw_tshirt(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Outline t-shirt."""
    w, h = size, size
    lw = max(int(size*0.04), 3)
    pts = [
        (cx - w*0.18, cy - h*0.42),  # left collar
        (cx - w*0.34, cy - h*0.34),
        (cx - w*0.5, cy - h*0.16),
        (cx - w*0.34, cy - h*0.02),
        (cx - w*0.30, cy - h*0.08),
        (cx - w*0.30, cy + h*0.45),
        (cx + w*0.30, cy + h*0.45),
        (cx + w*0.30, cy - h*0.08),
        (cx + w*0.34, cy - h*0.02),
        (cx + w*0.5, cy - h*0.16),
        (cx + w*0.34, cy - h*0.34),
        (cx + w*0.18, cy - h*0.42),
    ]
    draw.polygon(pts, outline=fill, width=lw)
    # collar arc
    draw.arc([cx - w*0.18, cy - h*0.50, cx + w*0.18, cy - h*0.30], 0, 180, fill=fill, width=lw)


def draw_floppy(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Floppy disk."""
    w = h = size
    left, top = cx - w/2, cy - h/2
    # body with clipped corner
    draw.polygon([
        (left, top), (left + w*0.82, top), (left + w, top + h*0.18),
        (left + w, top + h), (left, top + h),
    ], fill=fill)
    # label window
    draw.rounded_rectangle([left + w*0.2, top + h*0.45, left + w*0.8, top + h*0.88],
                           radius=size*0.03, fill=(245,240,232,255))
    for ly in (0.58, 0.68, 0.78):
        draw.line([(left + w*0.28, top + h*ly), (left + w*0.72, top + h*ly)],
                  fill=fill, width=max(int(size*0.03), 3))
    # shutter
    draw.rectangle([left + w*0.3, top + h*0.06, left + w*0.62, top + h*0.3], fill=(245,240,232,255))
    draw.rectangle([left + w*0.38, top + h*0.09, left + w*0.5, top + h*0.27], fill=fill)


def draw_baby(draw, cx, cy, size, fill=(26, 26, 26, 255)):
    """Outline baby face with curl."""
    r = size * 0.42
    lw = max(int(size*0.045), 4)
    draw.ellipse([cx - r, cy - r*0.88, cx + r, cy + r*0.95], outline=fill, width=lw)
    # curl on top
    draw.arc([cx - size*0.10, cy - r*1.25, cx + size*0.14, cy - r*0.75], 200, 60, fill=fill, width=lw)
    # eyes
    er = size*0.035
    for ex in (-0.16, 0.16):
        draw.ellipse([cx + ex*size - er, cy - er, cx + ex*size + er, cy + er], fill=fill)
    # smile
    draw.arc([cx - size*0.12, cy + size*0.02, cx + size*0.12, cy + size*0.2], 20, 160, fill=fill, width=lw)
