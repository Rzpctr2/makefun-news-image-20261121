#!/usr/bin/env python3
"""news-image-20261121 v1 generator — written fresh in this session.
Flat-vector broadsheet, 1024x1024, cream paper, serif masthead.
Layout follows the winning single-newspaper genre (autopsy 20 Nov):
masthead + subhead, 6-number stat strip, region bar, 3 hero scenes,
10 mid scenes with standfirsts, dotted world map + numbered index,
sequential hard-news tail, DATE CHECK box. NO verdict box, NO UTC
timeline, NO how-sure legend. Heroes = consensus stories of 21 Nov.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (244, 234, 211)
INK = (26, 21, 18)
RED = (166, 43, 31)
DARKRED = (140, 35, 24)
NAVY = (30, 58, 95)
TEAL = (46, 110, 106)
GOLD = (201, 154, 46)
MUTED = (107, 93, 79)
CREAM2 = (250, 243, 226)
RULE = (26, 21, 18)

F_PLAYFAIR = "/home/hatch/.fonts/PlayfairDisplay-Black.ttf"
F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SERIF_BI = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

_font_cache = {}
def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]

def text_w(draw, s, f):
    return draw.textlength(s, font=f)

def wrap(draw, s, f, max_w):
    """Greedy word wrap by pixel width; returns list of lines."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_text(draw, x, y, s, f, fill=INK, anchor="la", spacing=0):
    draw.text((x, y), s, font=f, fill=fill, anchor=anchor)

def para(draw, x, y, s, f, max_w, fill=INK, leading=None, max_lines=None):
    """Draw wrapped paragraph; return y after last line."""
    lh = leading or int(f.size * 1.22)
    lines = wrap(draw, s, f, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y

def ls_text(draw, cx, y, s, f, fill=INK, tracking=2):
    """Centered letter-spaced caps text; returns width used."""
    widths = [draw.textlength(ch, font=f) for ch in s]
    total = sum(widths) + tracking * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += w + tracking
    return total

def chip(draw, x, y, label, bg, fg=(255, 255, 255)):
    """Small status chip at top-right of a scene; x,y = top-right corner."""
    f = font(F_SANS_B, 9)
    tw = draw.textlength(label, font=f)
    w, h = int(tw) + 12, 15
    draw.rounded_rectangle([x - w, y, x, y + h], radius=3, fill=bg)
    draw.text((x - w + 6, y + 3), label, font=f, fill=fg)

def num_badge(draw, x, y, n):
    """Red square number badge, top-left of a scene."""
    f = font(F_SANS_B, 12)
    s = str(n)
    w = max(18, int(draw.textlength(s, font=f)) + 10)
    draw.rectangle([x, y, x + w, y + 18], fill=RED)
    draw.text((x + (w - draw.textlength(s, font=f)) / 2, y + 3), s, font=f, fill=(255, 255, 255))

# ---------------------------------------------------------------- map
# Coarse continent outlines (lon, lat), stylised — good enough for a
# dotted map at ~600x110. Equirectangular projection.
CONTINENTS = [
    # North America
    [(-168,65),(-150,70),(-130,71),(-120,70),(-105,68),(-95,66),(-85,69),(-78,71),(-70,62),(-65,60),(-60,55),(-55,47),(-65,44),(-70,42),(-75,38),(-80,32),(-81,26),(-85,29),(-90,21),(-95,19),(-100,18),(-105,20),(-110,23),(-115,28),(-120,34),(-125,40),(-125,49),(-135,58),(-150,60),(-165,60)],
    # Greenland
    [(-58,64),(-45,60),(-40,65),(-30,68),(-25,70),(-35,76),(-55,76),(-60,74)],
    # South America
    [(-80,10),(-75,11),(-70,12),(-62,10),(-55,6),(-50,0),(-44,-3),(-35,-8),(-40,-20),(-48,-28),(-55,-35),(-62,-41),(-68,-52),(-70,-55),(-73,-45),(-73,-35),(-70,-20),(-77,-12),(-80,-5)],
    # Africa
    [(-17,15),(-17,21),(-10,30),(-5,35),(10,37),(20,32),(30,31),(35,28),(40,15),(48,11),(51,10),(48,0),(42,-10),(40,-20),(35,-28),(28,-33),(20,-35),(15,-30),(12,-18),(9,-2),(9,4),(-8,5),(-13,8)],
    # Eurasia
    [(-10,36),(-9,43),(-2,48),(-5,50),(0,51),(5,53),(8,57),(10,59),(18,56),(21,55),(24,58),(28,60),(30,62),(40,68),(55,68),(68,73),(75,72),(90,75),(110,76),(130,72),(150,70),(170,66),(178,65),(170,60),(162,56),(158,52),(150,59),(142,55),(140,50),(135,43),(130,42),(127,40),(122,38),(120,32),(115,23),(110,20),(105,10),(103,2),(100,6),(98,10),(95,16),(92,21),(88,22),(85,19),(80,15),(77,8),(75,12),(72,20),(68,23),(65,25),(60,25),(57,26),(54,27),(50,29),(48,30),(44,29),(40,31),(36,36),(30,36),(26,38),(22,37),(19,40),(15,44),(12,44),(8,44),(3,43),(0,40),(-2,37),(-6,36)],
    # Australia
    [(113,-22),(114,-30),(115,-35),(120,-34),(129,-32),(132,-32),(136,-35),(140,-38),(145,-38),(150,-37),(153,-32),(153,-27),(150,-22),(146,-19),(142,-15),(142,-11),(136,-12),(132,-11),(126,-14),(122,-17),(118,-20)],
    # Borneo
    [(109,1),(113,4),(117,6),(119,0),(117,-3),(112,-3)],
    # Sumatra
    [(95,5),(100,0),(104,-3),(106,-6),(103,-5),(98,2)],
    # Java
    [(105,-6),(110,-7),(114,-8),(114,-9),(108,-8)],
    # New Guinea
    [(131,-1),(136,-2),(141,-3),(146,-6),(147,-8),(141,-8),(136,-7),(132,-4)],
    # UK
    [(-5,50),(-3,53),(-5,56),(-2,58),(0,53),(-1,51)],
    # Japan
    [(130,31),(133,34),(137,35),(140,38),(141,41),(143,43),(145,44),(142,42),(140,36),(136,34),(132,33)],
    # New Zealand
    [(167,-45),(170,-42),(174,-39),(176,-38),(178,-37),(175,-40),(172,-43),(168,-46)],
    # Madagascar
    [(44,-16),(48,-17),(50,-22),(47,-25),(44,-22)],
]

def _point_in_poly(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside

def lonlat_to_xy(lon, lat, x0, y0, w, h):
    # map window: lon -170..190, lat -56..78
    x = x0 + (lon + 170) / 360.0 * w
    y = y0 + (78 - lat) / 134.0 * h
    return x, y

def draw_dotted_map(draw, x0, y0, w, h, pins):
    """pins: list of (lon, lat, number). Dots where land, pins on top."""
    step = 7
    # precompute land test in lon/lat space
    for gy in range(int(y0), int(y0 + h), step):
        for gx in range(int(x0), int(x0 + w), step):
            lon = (gx - x0) / w * 360.0 - 170
            lat = 78 - (gy - y0) / h * 134.0
            for poly in CONTINENTS:
                if _point_in_poly(lon, lat, poly):
                    draw.ellipse([gx - 1.4, gy - 1.4, gx + 1.4, gy + 1.4],
                                 fill=(150, 128, 96))
                    break
    for lon, lat, n in pins:
        px, py = lonlat_to_xy(lon, lat, x0, y0, w, h)
        r = 8
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=(255, 255, 255), width=1)
        f = font(F_SANS_B, 8)
        s = str(n)
        draw.text((px - draw.textlength(s, font=f) / 2, py - 4), s,
                  font=f, fill=(255, 255, 255))

# ---------------------------------------------------------------- scenes
# Every scene painter draws a distinct flat-vector scene into (x, y, w, h).
# Palettes differ per scene so the page reads at 300px.

def scene_sky(draw, x, y, w, h, top, bottom):
    """Vertical gradient sky (banded steps, cheap)."""
    steps = 24
    for i in range(steps):
        t = i / (steps - 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        draw.rectangle([x, y + i * h / steps, x + w, y + (i + 1) * h / steps + 1],
                       fill=c)

def scene_climate(draw, x, y, w, h):
    """COP31: cracked dry earth, big low sun, empty chairs / flags."""
    scene_sky(draw, x, y, w, h, (232, 164, 96), (246, 214, 150))
    cx, cy, r = x + w * 0.72, y + h * 0.42, h * 0.30
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(214, 96, 44))
    # ground: cracked earth
    gy = y + h * 0.62
    draw.polygon([(x, gy), (x + w, gy), (x + w, y + h), (x, y + h)],
                 fill=(146, 96, 52))
    draw.polygon([(x, gy), (x + w * 0.45, gy), (x + w * 0.35, y + h), (x, y + h)],
                 fill=(128, 82, 44))
    # cracks
    for (x1, y1, x2, y2) in [(0.15, 0.66, 0.30, 0.80), (0.30, 0.80, 0.22, 0.95),
                             (0.55, 0.64, 0.62, 0.78), (0.62, 0.78, 0.75, 0.72),
                             (0.80, 0.66, 0.86, 0.90)]:
        draw.line([x + w * x1, y + h * y1, x + w * x2, y + h * y2],
                  fill=(90, 56, 28), width=2)
    # small flag row (nations, no deal)
    for i, c in enumerate([(30, 58, 95), (166, 43, 31), (46, 110, 106),
                           (201, 154, 46), (90, 60, 120)]):
        fx = x + w * (0.10 + i * 0.16)
        draw.line([fx, gy - h * 0.16, fx, gy], fill=(60, 40, 24), width=2)
        draw.polygon([(fx, gy - h * 0.16), (fx + w * 0.11, gy - h * 0.12),
                      (fx, gy - h * 0.08)], fill=c)

def scene_bridge(draw, x, y, w, h):
    """Kyiv bridges: river, bridge deck + cables, city, smoke."""
    scene_sky(draw, x, y, w, h, (58, 74, 110), (214, 164, 120))
    # sun low
    draw.ellipse([x + w * 0.78 - 14, y + h * 0.18 - 14, x + w * 0.78 + 14,
                  y + h * 0.18 + 14], fill=(232, 178, 90))
    # city skyline
    base = y + h * 0.58
    for (bx, bw, bh, c) in [(0.02, 0.10, 0.30, (52, 56, 74)),
                            (0.14, 0.08, 0.42, (40, 44, 60)),
                            (0.24, 0.12, 0.26, (62, 66, 84)),
                            (0.62, 0.09, 0.36, (48, 52, 70)),
                            (0.73, 0.11, 0.28, (58, 62, 80)),
                            (0.86, 0.10, 0.40, (42, 46, 62))]:
        draw.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                       fill=c)
    # smoke columns (kept inside the box)
    for sx in (0.17, 0.77):
        for i, r in enumerate((6, 8, 10)):
            draw.ellipse([x + w * sx - r, base - h * 0.30 - i * 11 - r,
                          x + w * sx + r, base - h * 0.30 - i * 11 + r],
                         fill=(120, 116, 110))
    # river
    draw.rectangle([x, y + h * 0.72, x + w, y + h], fill=(52, 96, 128))
    draw.rectangle([x, y + h * 0.72, x + w, y + h * 0.75], fill=(120, 170, 200))
    # bridge deck + cables
    by = y + h * 0.66
    draw.rectangle([x, by, x + w, by + 5], fill=(30, 30, 34))
    for px in (0.30, 0.70):
        draw.rectangle([x + w * px - 3, y + h * 0.30, x + w * px + 3, by],
                       fill=(30, 30, 34))
        draw.line([x + w * px, y + h * 0.30, x + w * 0.05, by], fill=(30, 30, 34), width=1)
        draw.line([x + w * px, y + h * 0.30, x + w * 0.55, by], fill=(30, 30, 34), width=1)
        draw.line([x + w * px, y + h * 0.30, x + w * 0.95, by], fill=(30, 30, 34), width=1)
    # broken span gap (hit bridge)
    draw.rectangle([x + w * 0.44, by, x + w * 0.56, by + 5], fill=(52, 96, 128))
    draw.polygon([(x + w * 0.44, by), (x + w * 0.47, by + 16),
                  (x + w * 0.44, by + 16)], fill=(30, 30, 34))
    draw.polygon([(x + w * 0.56, by), (x + w * 0.53, by + 16),
                  (x + w * 0.56, by + 16)], fill=(30, 30, 34))

def scene_drone(draw, x, y, w, h):
    """Strait of Hormuz: sea, tanker, drone silhouette, burst."""
    scene_sky(draw, x, y, w, h, (34, 68, 96), (232, 158, 92))
    draw.ellipse([x + w * 0.20 - 16, y + h * 0.20 - 16, x + w * 0.20 + 16,
                  y + h * 0.20 + 16], fill=(240, 200, 120))
    # sea
    draw.rectangle([x, y + h * 0.62, x + w, y + h], fill=(28, 74, 106))
    for wy in (0.68, 0.78, 0.90):
        draw.line([x + w * 0.05, y + h * wy, x + w * 0.95, y + h * wy],
                  fill=(90, 150, 185), width=2)
    # tanker
    tx, ty = x + w * 0.08, y + h * 0.70
    draw.rectangle([tx, ty, tx + w * 0.42, ty + h * 0.16], fill=(120, 40, 32))
    draw.rectangle([tx + w * 0.30, ty - h * 0.10, tx + w * 0.40, ty], fill=(200, 200, 200))
    draw.rectangle([tx + w * 0.05, ty - h * 0.05, tx + w * 0.12, ty], fill=(200, 200, 200))
    # drone silhouette
    dx, dy = x + w * 0.68, y + h * 0.34
    draw.ellipse([dx - 22, dy - 5, dx + 22, dy + 5], fill=(24, 24, 28))
    draw.polygon([(dx - 22, dy), (dx - 34, dy - 10), (dx - 30, dy + 2)], fill=(24, 24, 28))
    draw.polygon([(dx + 22, dy), (dx + 34, dy - 10), (dx + 30, dy + 2)], fill=(24, 24, 28))
    draw.ellipse([dx - 4, dy - 8, dx + 4, dy + 8], fill=(24, 24, 28))
    # burst
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        draw.line([dx + 26 * math.cos(a), dy + 26 * math.sin(a),
                   dx + 40 * math.cos(a), dy + 40 * math.sin(a)],
                  fill=(240, 180, 60), width=3)

def scene_fire(draw, x, y, w, h):
    """Basra power station fire: towers, flames, smoke."""
    scene_sky(draw, x, y, w, h, (70, 60, 70), (200, 130, 80))
    base = y + h * 0.78
    # cooling towers
    for tx, tw in ((0.08, 0.20), (0.34, 0.20), (0.60, 0.20)):
        draw.polygon([(x + w * tx, base), (x + w * (tx + 0.03), y + h * 0.30),
                      (x + w * (tx + tw - 0.03), y + h * 0.30),
                      (x + w * (tx + tw), base)], fill=(120, 118, 112))
        draw.rectangle([x + w * (tx + 0.01), y + h * 0.28,
                        x + w * (tx + tw - 0.01), y + h * 0.32], fill=(90, 88, 84))
    # flames
    for fx, fh in ((0.16, 0.34), (0.44, 0.42), (0.70, 0.30)):
        draw.polygon([(x + w * (fx - 0.06), base), (x + w * fx, base - h * fh),
                      (x + w * (fx + 0.06), base)], fill=(214, 96, 32))
        draw.polygon([(x + w * (fx - 0.03), base), (x + w * fx, base - h * fh * 0.62),
                      (x + w * (fx + 0.03), base)], fill=(240, 180, 60))
    # smoke (kept inside the box)
    for sx in (0.44, 0.70):
        for i, r in enumerate((6, 8, 10)):
            draw.ellipse([x + w * sx - r, y + h * 0.46 - i * 9 - r,
                          x + w * sx + r, y + h * 0.46 - i * 9 + r],
                         fill=(80, 76, 72))
    draw.rectangle([x, base, x + w, y + h], fill=(52, 48, 44))

def scene_space(draw, x, y, w, h):
    """BepiColombo at Mercury: black sky, stars, grey planet, craft."""
    draw.rectangle([x, y, x + w, y + h], fill=(12, 14, 26))
    import random
    rnd = random.Random(7)
    for _ in range(26):
        sx = x + rnd.random() * w
        sy = y + rnd.random() * h * 0.7
        r = rnd.choice((1, 1, 2))
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 220, 230))
    # Mercury
    mx, my, mr = x + w * 0.68, y + h * 0.62, h * 0.34
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(150, 138, 122))
    for (cx, cy, cr) in ((0.55, 0.50, 0.06), (0.78, 0.66, 0.08), (0.62, 0.78, 0.05),
                         (0.82, 0.46, 0.05)):
        draw.ellipse([x + w * cx - cr * h, y + h * cy - cr * h,
                      x + w * cx + cr * h, y + h * cy + cr * h], fill=(120, 108, 94))
    # sunlit crescent edge
    draw.arc([mx - mr, my - mr, mx + mr, my + mr], start=200, end=340,
             fill=(240, 220, 180), width=3)
    # spacecraft: two panels + body
    bx, by = x + w * 0.16, y + h * 0.30
    draw.rectangle([bx, by - 6, bx + w * 0.16, by + 6], fill=(200, 200, 210))
    draw.rectangle([bx - w * 0.20, by - 4, bx - 2, by + 4], fill=(70, 110, 180))
    draw.rectangle([bx + w * 0.16 + 2, by - 4, bx + w * 0.36, by + 4], fill=(70, 110, 180))
    draw.line([bx + w * 0.36, by, mx - mr + 6, my - 6], fill=(240, 180, 60), width=2)

def scene_missile(draw, x, y, w, h):
    """Riyadh night: city lights, intercept streaks."""
    scene_sky(draw, x, y, w, h, (16, 22, 44), (60, 60, 96))
    import random
    rnd = random.Random(11)
    for _ in range(20):
        sx = x + rnd.random() * w
        sy = y + rnd.random() * h * 0.45
        draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(220, 220, 230))
    # city
    base = y + h * 0.82
    for (bx, bw, bh) in [(0.02, 0.08, 0.30), (0.12, 0.06, 0.42), (0.20, 0.10, 0.26),
                         (0.32, 0.07, 0.38), (0.42, 0.09, 0.30), (0.55, 0.06, 0.44),
                         (0.63, 0.10, 0.28), (0.75, 0.08, 0.36), (0.85, 0.10, 0.26)]:
        draw.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                       fill=(22, 26, 40))
        for wy in range(2):
            draw.rectangle([x + w * (bx + 0.015), base - h * bh + 4 + wy * 9,
                            x + w * (bx + 0.035), base - h * bh + 8 + wy * 9],
                           fill=(240, 200, 90))
    # intercept streaks
    draw.line([x + w * 0.30, y + h * 0.10, x + w * 0.55, y + h * 0.55],
              fill=(240, 200, 90), width=3)
    draw.line([x + w * 0.78, y + h * 0.06, x + w * 0.60, y + h * 0.50],
              fill=(240, 200, 90), width=3)
    draw.ellipse([x + w * 0.55 - 6, y + h * 0.55 - 6, x + w * 0.55 + 6,
                  y + h * 0.55 + 6], fill=(255, 220, 120))
    draw.ellipse([x + w * 0.60 - 5, y + h * 0.50 - 5, x + w * 0.60 + 5,
                  y + h * 0.50 + 5], fill=(255, 220, 120))
    draw.rectangle([x, base, x + w, y + h], fill=(18, 20, 34))

def scene_flags(draw, x, y, w, h):
    """UK-EU deal: two flags + stars circle on cream."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 228, 200))
    # EU flag
    ex, ey, ew, eh = x + w * 0.06, y + h * 0.22, w * 0.40, h * 0.56
    draw.rectangle([ex, ey, ex + ew, ey + eh], fill=(30, 58, 120))
    for k in range(12):
        a = math.radians(k * 30 - 90)
        sx = ex + ew / 2 + ew * 0.32 * math.cos(a)
        sy = ey + eh / 2 + eh * 0.32 * math.sin(a)
        draw.ellipse([sx - 2.5, sy - 2.5, sx + 2.5, sy + 2.5], fill=(240, 200, 60))
    # UK flag (stylised)
    ux, uy, uw, uh = x + w * 0.54, y + h * 0.22, w * 0.40, h * 0.56
    draw.rectangle([ux, uy, ux + uw, uy + uh], fill=(30, 58, 120))
    draw.polygon([(ux, uy), (ux + uw, uy + uh), (ux + uw, uy + uh * 0.82),
                  (ux, uy + uh * 0.18)], fill=(255, 255, 255))
    draw.polygon([(ux + uw, uy), (ux, uy + uh), (ux, uy + uh * 0.82),
                  (ux + uw, uy + uh * 0.18)], fill=(255, 255, 255))
    draw.rectangle([ux + uw * 0.44, uy, ux + uw * 0.56, uy + uh], fill=(200, 40, 40))
    draw.rectangle([ux, uy + uh * 0.44, ux + uw, uy + uh * 0.56], fill=(200, 40, 40))
    # handshake arc
    draw.arc([x + w * 0.30, y + h * 0.02, x + w * 0.70, y + h * 0.30],
             start=200, end=340, fill=RED, width=3)

def scene_court(draw, x, y, w, h):
    """Court columns + gavel."""
    scene_sky(draw, x, y, w, h, (210, 196, 170), (240, 228, 200))
    base = y + h * 0.80
    # columns
    for cx in (0.12, 0.32, 0.52, 0.72):
        draw.rectangle([x + w * cx, y + h * 0.22, x + w * (cx + 0.07), base],
                       fill=(120, 100, 70))
        draw.rectangle([x + w * (cx - 0.015), y + h * 0.18,
                        x + w * (cx + 0.085), y + h * 0.22], fill=(100, 82, 56))
    draw.rectangle([x + w * 0.06, y + h * 0.12, x + w * 0.88, y + h * 0.18],
                   fill=(100, 82, 56))
    draw.rectangle([x, base, x + w, y + h], fill=(90, 74, 50))
    # scales
    sx, sy = x + w * 0.50, y + h * 0.52
    draw.line([sx, sy - h * 0.16, sx, sy + h * 0.10], fill=(60, 50, 36), width=3)
    draw.line([sx - w * 0.14, sy - h * 0.10, sx + w * 0.14, sy - h * 0.10],
              fill=(60, 50, 36), width=3)
    for dx in (-0.14, 0.14):
        draw.line([sx + w * dx, sy - h * 0.10, sx + w * dx, sy - h * 0.02],
                  fill=(60, 50, 36), width=2)
        draw.polygon([(sx + w * (dx - 0.05), sy - h * 0.02),
                      (sx + w * (dx + 0.05), sy - h * 0.02),
                      (sx + w * dx, sy + h * 0.08)], fill=(201, 154, 46))

def scene_market(draw, x, y, w, h):
    """Markets: bank facade + falling coins, no chart lines."""
    scene_sky(draw, x, y, w, h, (96, 120, 140), (220, 200, 160))
    base = y + h * 0.80
    # bank building
    draw.rectangle([x + w * 0.18, y + h * 0.30, x + w * 0.82, base], fill=(180, 168, 140))
    draw.polygon([(x + w * 0.12, y + h * 0.30), (x + w * 0.50, y + h * 0.10),
                  (x + w * 0.88, y + h * 0.30)], fill=(150, 136, 108))
    for cx in (0.24, 0.40, 0.56, 0.70):
        draw.rectangle([x + w * cx, y + h * 0.38, x + w * (cx + 0.05), base],
                       fill=(140, 126, 98))
    draw.rectangle([x, base, x + w, y + h], fill=(110, 98, 76))
    # falling coins
    for (cx, cy, r) in ((0.10, 0.30, 9), (0.88, 0.22, 8), (0.92, 0.55, 10),
                        (0.06, 0.62, 8)):
        draw.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                      y + h * cy + r], fill=(201, 154, 46),
                     outline=(140, 100, 20), width=2)
        draw.text((x + w * cx - 3, y + h * cy - 5), "$", font=font(F_SANS_B, 10),
                  fill=(120, 84, 16))

def scene_city(draw, x, y, w, h):
    """Generic city street scene."""
    scene_sky(draw, x, y, w, h, (140, 160, 180), (240, 210, 170))
    base = y + h * 0.72
    for (bx, bw, bh, c) in [(0.00, 0.16, 0.40, (90, 80, 96)),
                            (0.18, 0.14, 0.55, (70, 62, 80)),
                            (0.34, 0.16, 0.34, (100, 90, 104)),
                            (0.52, 0.14, 0.50, (76, 68, 86)),
                            (0.68, 0.16, 0.38, (94, 84, 100)),
                            (0.86, 0.14, 0.46, (72, 64, 82))]:
        draw.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base], fill=c)
        for wy in range(3):
            draw.rectangle([x + w * (bx + 0.03), base - h * bh + 6 + wy * 12,
                            x + w * (bx + 0.06), base - h * bh + 12 + wy * 12],
                           fill=(240, 200, 110))
    draw.rectangle([x, base, x + w, y + h], fill=(60, 56, 52))
    draw.line([x, y + h * 0.86, x + w, y + h * 0.86], fill=(220, 200, 90), width=2)

def scene_sea(draw, x, y, w, h):
    """Sea + ship + storm clouds."""
    scene_sky(draw, x, y, w, h, (120, 130, 140), (200, 190, 170))
    for (cx, cy, r) in ((0.20, 0.18, 26), (0.55, 0.12, 32), (0.85, 0.20, 24)):
        draw.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                      y + h * cy + r], fill=(90, 92, 100))
    draw.rectangle([x, y + h * 0.60, x + w, y + h], fill=(40, 84, 110))
    for wy in (0.68, 0.80, 0.92):
        draw.line([x + w * 0.04, y + h * wy, x + w * 0.96, y + h * wy],
                  fill=(110, 170, 200), width=2)
    # ship
    sx, sy = x + w * 0.30, y + h * 0.62
    draw.polygon([(sx, sy), (sx + w * 0.42, sy), (sx + w * 0.36, sy + h * 0.14),
                  (sx + w * 0.06, sy + h * 0.14)], fill=(60, 50, 44))
    draw.rectangle([sx + w * 0.16, sy - h * 0.16, sx + w * 0.26, sy], fill=(200, 200, 200))
    draw.line([sx + w * 0.21, sy - h * 0.30, sx + w * 0.21, sy - h * 0.16],
              fill=(60, 50, 44), width=2)
    draw.polygon([(sx + w * 0.21, sy - h * 0.30), (sx + w * 0.33, sy - h * 0.24),
                  (sx + w * 0.21, sy - h * 0.18)], fill=RED)

def scene_lab(draw, x, y, w, h):
    """Science/lab: flask + molecule."""
    draw.rectangle([x, y, x + w, y + h], fill=(216, 228, 220))
    # flask
    fx, fy = x + w * 0.30, y + h * 0.22
    draw.rectangle([fx + w * 0.06, fy, fx + w * 0.12, fy + h * 0.18],
                   fill=(200, 210, 215), outline=(60, 70, 80), width=2)
    draw.polygon([(fx + w * 0.06, fy + h * 0.18), (fx + w * 0.12, fy + h * 0.18),
                  (fx + w * 0.24, fy + h * 0.58), (fx - w * 0.06, fy + h * 0.58)],
                 fill=(120, 180, 200), outline=(60, 70, 80))
    # molecule
    for (mx, my, r) in ((0.68, 0.30, 9), (0.82, 0.50, 7), (0.64, 0.62, 8)):
        draw.ellipse([x + w * mx - r, y + h * my - r, x + w * mx + r,
                      y + h * my + r], fill=TEAL)
    draw.line([x + w * 0.68, y + h * 0.30, x + w * 0.82, y + h * 0.50],
              fill=(60, 70, 80), width=2)
    draw.line([x + w * 0.82, y + h * 0.50, x + w * 0.64, y + h * 0.62],
              fill=(60, 70, 80), width=2)
    draw.line([x + w * 0.68, y + h * 0.30, x + w * 0.64, y + h * 0.62],
              fill=(60, 70, 80), width=2)
    draw.rectangle([x, y + h * 0.86, x + w, y + h], fill=(180, 190, 182))

def scene_parliament(draw, x, y, w, h):
    """Parliament / summit hall: dome + flags."""
    scene_sky(draw, x, y, w, h, (150, 170, 190), (235, 220, 190))
    base = y + h * 0.78
    # dome building
    draw.rectangle([x + w * 0.14, y + h * 0.42, x + w * 0.86, base], fill=(170, 156, 128))
    draw.pieslice([x + w * 0.36, y + h * 0.08, x + w * 0.64, y + h * 0.52],
                  start=180, end=360, fill=(140, 126, 100))
    draw.rectangle([x + w * 0.48, y + h * 0.02, x + w * 0.52, y + h * 0.10],
                   fill=(120, 106, 82))
    for cx in (0.20, 0.36, 0.52, 0.68):
        draw.rectangle([x + w * cx, y + h * 0.50, x + w * (cx + 0.06), base],
                       fill=(140, 126, 100))
    # flags
    for i, c in enumerate([(166, 43, 31), (30, 58, 95), (46, 110, 106)]):
        fx = x + w * (0.30 + i * 0.20)
        draw.line([fx, base - h * 0.22, fx, base], fill=(60, 40, 24), width=2)
        draw.polygon([(fx, base - h * 0.22), (fx + w * 0.10, base - h * 0.18),
                      (fx, base - h * 0.14)], fill=c)
    draw.rectangle([x, base, x + w, y + h], fill=(120, 108, 88))

def scene_tech(draw, x, y, w, h):
    """Tech: dark screen, chip, circuit traces."""
    draw.rectangle([x, y, x + w, y + h], fill=(18, 26, 40))
    # chip
    cx, cy, s = x + w * 0.50, y + h * 0.52, h * 0.26
    draw.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(30, 58, 95),
                   outline=(90, 140, 200), width=2)
    draw.rectangle([cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.5],
                   fill=(70, 110, 180))
    for k in range(4):
        t = -s + k * (2 * s / 3)
        draw.line([cx + t, cy - s - 8, cx + t, cy - s], fill=(90, 140, 200), width=2)
        draw.line([cx + t, cy + s, cx + t, cy + s + 8], fill=(90, 140, 200), width=2)
        draw.line([cx - s - 8, cy + t, cx - s, cy + t], fill=(90, 140, 200), width=2)
        draw.line([cx + s, cy + t, cx + s + 8, cy + t], fill=(90, 140, 200), width=2)
    # traces
    for (x1, y1, x2, y2) in [(0.06, 0.20, 0.30, 0.20), (0.70, 0.16, 0.94, 0.16),
                             (0.08, 0.80, 0.28, 0.80), (0.72, 0.82, 0.94, 0.82)]:
        draw.line([x + w * x1, y + h * y1, x + w * x2, y + h * y2],
                  fill=(90, 140, 200), width=2)
        draw.ellipse([x + w * x2 - 3, y + h * y2 - 3, x + w * x2 + 3,
                      y + h * y2 + 3], fill=(240, 200, 60))

def scene_village(draw, x, y, w, h):
    """Rural village: hills, houses, road."""
    scene_sky(draw, x, y, w, h, (160, 190, 200), (245, 225, 180))
    draw.ellipse([x + w * 0.82 - 13, y + h * 0.18 - 13, x + w * 0.82 + 13,
                  y + h * 0.18 + 13], fill=(240, 200, 110))
    # hills
    draw.polygon([(x, y + h * 0.62), (x + w * 0.30, y + h * 0.42),
                  (x + w * 0.62, y + h * 0.62), (x, y + h)], fill=(110, 150, 90))
    draw.polygon([(x + w * 0.40, y + h * 0.62), (x + w * 0.72, y + h * 0.46),
                  (x + w, y + h * 0.62), (x + w, y + h), (x + w * 0.40, y + h)],
                 fill=(90, 130, 76))
    # houses
    for hx, c in ((0.12, (180, 120, 80)), (0.30, (200, 150, 100)),
                  (0.58, (170, 110, 70))):
        draw.rectangle([x + w * hx, y + h * 0.62, x + w * (hx + 0.14), y + h * 0.78],
                       fill=c)
        draw.polygon([(x + w * (hx - 0.02), y + h * 0.62),
                      (x + w * (hx + 0.07), y + h * 0.50),
                      (x + w * (hx + 0.16), y + h * 0.62)], fill=(140, 60, 44))
    draw.rectangle([x, y + h * 0.78, x + w, y + h], fill=(120, 100, 70))

def paste_scene(img, scene, x, y, w, h):
    """Draw a scene into a temp image and paste it — clips any painter
    overflow (e.g. smoke/clouds) to the scene box."""
    tmp = Image.new("RGB", (w, h), PAPER)
    td = ImageDraw.Draw(tmp)
    SCENES[scene](td, 0, 0, w, h)
    img.paste(tmp, (x, y))

# ---------------------------------------------------------------- data
# FINAL story list — verified 21 Nov 2026 by 4 research agents + my own
# checks (COP31/Zelensky/MQ-9 re-verified by me via search).
# Every story: (n, scene, kicker, headline, standfirst, region, lon, lat,
# chip). Regions use the geographic bar (Middle East = ASIA).
# chip: REPORTED = confirmed happened; CLAIM = single-source claim.
HEROES = [
    (1, "climate", "ANTALYA · CLIMATE", "COP31 deadlocked as fossil fuels vanish from draft",
     "Talks run into overtime; $120bn aid figure dropped.", "WORLD", 30, 36, "REPORTED"),
    (2, "bridge", "UKRAINE · WAR", "Zelensky: Putin is a killer",
     "Rebuke after Trump calls Putin a friend in China.", "EUROPE", 30, 50, "REPORTED"),
    (3, "market", "MARKETS · CRYPTO", "Bitcoin sinks below $56,000",
     "Lowest since September 2024; $2.4bn liquidated.", "WORLD", -74, 41, "REPORTED"),
]

MIDS = [
    (4, "drone", "HORMUZ · CONFLICT", "Iran says it downed a US drone",
     "IRGC claims 58th MQ-9 shot down over the strait.", "ASIA", 56, 26, "CLAIM"),
    (5, "fire", "IRAQ · BASRA", "Fire kills four at power station",
     "Blaze at Hartha plant injures 35; 800 MW halted.", "ASIA", 47, 30, "REPORTED"),
    (6, "village", "INDIA · MANIPUR", "Toxic alcohol kills 11",
     "More than 180 poisoned; inquiry opened.", "ASIA", 94, 24, "REPORTED"),
    (7, "tech", "U.S. · CYBER", "FBI crime database hacked",
     "Bureau probes NCIC breach; USDA also hit.", "NORTH AMERICA", -77, 39, "REPORTED"),
    (8, "space", "SPACE · MERCURY", "BepiColombo arrives at Mercury",
     "Orbit burn due 18:24 UTC after 8 years, 10bn km.", "WORLD", -52, 5, "REPORTED"),
    (9, "missile", "RIYADH · DEFENCE", "Three missiles downed",
     "Third night of Houthi fire intercepted.", "ASIA", 47, 25, "REPORTED"),
    (10, "parliament", "TAIWAN · MARKETS", "Taiwan fund steps in after rout",
     "Stabilisation fund buys after worst week since 1990.", "ASIA", 121, 25, "REPORTED"),
    (11, "flags", "BRITAIN · EUROPE", "UK-EU deal: fees no bar",
     "Miliband says pact stands without tuition deal.", "EUROPE", 0, 51, "REPORTED"),
    (12, "court", "GENEVA · ARMS", "Killer-robot talks end with no rules",
     "UN talks end; binding rules pushed to 2028.", "EUROPE", 6, 46, "REPORTED"),
    (13, "city", "SOUTH AFRICA · POLITICS", "ANC fights to keep its cities",
     "Vote share falls to 31% after poll setback.", "AFRICA", 28, -26, "REPORTED"),
]

# Tail briefs: (region, place, headline fragment) — hard news only,
# each happened or first reported 21 Nov 2026. Numbered 14–33.
TAIL = [
    ("ASIA", "ODISHA", "Akvan weakens; 209 mm rain"),
    ("EUROPE", "KRYVYI RIH", "New overnight strike wounds 58"),
    ("EUROPE", "WARSAW", "NATO chief Rutte due in Warsaw"),
    ("NORTH AMERICA", "WASHINGTON", "Lukoil sale deadline expires"),
    ("WORLD", "CAMBRIDGE", "Riemann proof passes checks"),
    ("AFRICA", "BAYELSA", "Funeral boat capsizes, four dead"),
    ("SOUTH AMERICA", "PERU", "M6.7 quake shakes Andes, no deaths"),
    ("ASIA", "TIMOR-LESTE", "M6.8 quake off Lospalos"),
    ("ASIA", "JAKARTA", "Fires burned 7.1m acres in 2026"),
    ("ASIA", "TOKYO", "Supercomputer Fugaku hacked"),
    ("NORTH AMERICA", "SAN FRANCISCO", "Open-weight AI model ships"),
    ("NORTH AMERICA", "WASHINGTON", "Trump vows AI-centre tax"),
    ("WORLD", "ADDIS ABABA", "Ethiopia to host COP32 in 2027"),
    ("EUROPE", "LONDON", "Gove calls EU deal a step back"),
    ("EUROPE", "KYIV", "Bridge traffic restored"),
    ("EUROPE", "STOCKHOLM", "Swedish jets join NATO watch"),
    ("ASIA", "TEHRAN", "Iran seeks diplomacy guarantees"),
    ("ASIA", "KUALA LUMPUR", "Haze drifts over the strait"),
    ("NORTH AMERICA", "WASHINGTON", "Farm department also hacked"),
    ("NORTH AMERICA", "NEW YORK", "Crypto fear gauge at extreme 12"),
]

# Stat strip: (big number, label) — each from a DIFFERENT story, all 21 Nov.
STATS = [
    ("$120BN", "adaptation aid cut from COP31 draft"),
    ("58", "US drones Iran claims downed"),
    ("180", "poisoned by toxic alcohol in Manipur"),
    ("$2.4BN", "crypto liquidations in 24 hours"),
    ("800 MW", "power halted by Basra fire"),
    ("6.7", "magnitude of Peru quake"),
]

# DATE CHECK: high-salience items that look like 21 Nov news but are NOT.
# Must not contradict anything on the page.
DATECHECK = [
    "Russia's Kyiv bridges barrage — overnight 19–20 Nov, not today.",
    "ICJ Myanmar genocide ruling — 19 Nov; only reactions are new today.",
    "AI sell-off, S&P −3.7% — Friday 20 Nov close, not Saturday.",
    "Trump–Xi–Putin summit, Shenzhen — Thursday 19 Nov.",
    "GTA VI $3.79bn day-one sales — announced 20 Nov; launch 19 Nov.",
    "UK–EU reset deal — signed Friday 20 Nov; only reaction is new today.",
]

SOURCES = ("Sources: BBC · AP · Reuters · Al Jazeera · The Guardian · TBS News · "
           "Tasnim · AAP · USGS — 21 November 2026. All drawings original. "
           "THE WORLD IN ONE DAY · PAGE 1 · 13 DRAWN SCENES")

REGION_ORDER = ["NORTH AMERICA", "SOUTH AMERICA", "EUROPE", "AFRICA",
                "ASIA", "OCEANIA", "WORLD"]

def all_stories():
    return HEROES + MIDS

SCENES = {
    "climate": scene_climate, "bridge": scene_bridge, "drone": scene_drone,
    "fire": scene_fire, "space": scene_space, "missile": scene_missile,
    "flags": scene_flags, "court": scene_court, "market": scene_market,
    "city": scene_city, "sea": scene_sea, "lab": scene_lab,
    "parliament": scene_parliament, "tech": scene_tech, "village": scene_village,
}

# ---------------------------------------------------------------- layout
MX = 24                      # side margin
CW = W - 2 * MX              # content width = 976

def render(stories_heroes, stories_mids, tail, stats, datecheck, out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    total = len(stories_heroes) + len(stories_mids) + len(tail)

    # --- kicker + masthead
    y = 12
    ls_text(d, W // 2, y, "THE WORLD IN ONE DAY", font(F_SANS_B, 11), fill=INK, tracking=4)
    y = 28
    mast = font(F_PLAYFAIR, 50)
    d.text((W // 2, y), "Saturday 21 November 2026", font=mast, fill=INK, anchor="ma")
    y = 92
    sub = " · ".join(h[3] for h in stories_heroes)
    f_sub = font(F_SERIF_I, 16)
    d.text((W // 2, y), sub, font=f_sub, fill=RED, anchor="ma")
    y = 118
    d.line([MX, y, W - MX, y], fill=RULE, width=2)
    d.line([MX, y + 4, W - MX, y + 4], fill=RULE, width=1)

    # --- stat strip: 6 boxes
    y = 130
    bw = CW // 6
    for i, (num, lab) in enumerate(stats):
        bx = MX + i * bw
        d.rectangle([bx + 2, y, bx + bw - 2, y + 50], outline=INK, width=1)
        f_n = font(F_SANS_B, 21)
        d.text((bx + bw / 2, y + 4), num, font=f_n, fill=RED, anchor="ma")
        para(d, bx + 8, y + 29, lab, font(F_SANS, 9), bw - 16, fill=INK,
             leading=11, max_lines=2)
    y = 188
    # --- region bar (counts sum to total)
    counts = {r: 0 for r in REGION_ORDER}
    for s in stories_heroes + stories_mids:
        counts[s[5] if s[5] in counts else "WORLD"] += 1
    for t in tail:
        counts[t[0] if t[0] in counts else "WORLD"] += 1
    parts = [f"{r}  {counts[r]}" for r in REGION_ORDER if counts[r] > 0]
    f_rb = font(F_SANS_B, 11)
    d.text((W // 2, y), "   ·   ".join(parts), font=f_rb, fill=INK, anchor="ma")

    # --- heroes
    y = 210
    hw = (CW - 2 * 12) // 3
    hh = 118
    for i, s in enumerate(stories_heroes):
        n, scene, kicker, head, stand, region, lon, lat, stchip = s
        hx = MX + i * (hw + 12)
        paste_scene(img, scene, hx, y, hw, hh)
        d.rectangle([hx, y, hx + hw, y + hh], outline=INK, width=1)
        num_badge(d, hx + 4, y + 4, n)
        chip(d, hx + hw - 4, y + 4, stchip,
             (34, 120, 60) if stchip == "REPORTED" else (180, 120, 20))
        ky = y + hh + 8
        d.text((hx, ky), kicker, font=font(F_SANS_B, 9), fill=RED)
        hy = ky + 14
        para(d, hx, hy, head, font(F_SERIF_B, 19), hw, fill=INK,
             leading=21, max_lines=2)
        sy = hy + 44
        para(d, hx, sy, stand, font(F_SANS, 11), hw, fill=(60, 54, 48),
             leading=13, max_lines=2)
    y = 210 + hh + 8 + 14 + 44 + 28  # = 422

    # --- MORE FROM THE DAY band
    d.rectangle([MX, y, W - MX, y + 20], fill=RED)
    d.text((MX + 8, y + 4), "MORE FROM THE DAY", font=font(F_SANS_B, 12),
           fill=(255, 255, 255))
    y += 28

    # --- mid grid: 5 cols x 2 rows
    mw = (CW - 4 * 10) // 5
    mh = 62
    for row in range(2):
        for col in range(5):
            s = stories_mids[row * 5 + col]
            n, scene, kicker, head, stand, region, lon, lat, stchip = s
            mx = MX + col * (mw + 10)
            my = y
            paste_scene(img, scene, mx, my, mw, mh)
            d.rectangle([mx, my, mx + mw, my + mh], outline=INK, width=1)
            num_badge(d, mx + 3, my + 3, n)
            chip(d, mx + mw - 3, my + 3, stchip,
                 (34, 120, 60) if stchip == "REPORTED" else (180, 120, 20))
            ky = my + mh + 5
            d.text((mx, ky), kicker, font=font(F_SANS_B, 8), fill=RED)
            hy = ky + 11
            para(d, mx, hy, head, font(F_SERIF_B, 13), mw, fill=INK,
                 leading=14, max_lines=2)
            sy = hy + 29
            para(d, mx, sy, stand, font(F_SANS, 9), mw, fill=(60, 54, 48),
                 leading=11, max_lines=2)
        y += mh + 5 + 11 + 29 + 24
    # y now ~ 422+28 + 2*125 = 700

    # --- map + index
    d.text((MX, y), "WHERE IT HAPPENED", font=font(F_SANS_B, 12), fill=RED)
    d.text((W - MX, y + 2), "Red numbers mark stories 1–13. Positions are approximate.",
           font=font(F_SANS, 9), fill=MUTED, anchor="ra")
    y += 18
    map_x, map_y, map_w, map_h = MX, y, 600, 104
    # Nudge display positions so close pins (London/Hague, Basra/Riyadh,
    # Kyiv/Antalya) do not overlap. Values are display-only.
    PIN_NUDGE = {1: (3, -2), 2: (-6, 3), 3: (6, 3), 4: (5, 3), 5: (-6, 4),
                 7: (-3, -3), 9: (4, -4), 11: (-4, 2), 12: (4, 1)}
    pins = []
    for s in stories_heroes + stories_mids:
        if s[6] == 0 and s[7] == 0:
            continue
        dlon, dlat = PIN_NUDGE.get(s[0], (0, 0))
        pins.append((s[6] + dlon, s[7] + dlat, s[0]))
    draw_dotted_map(d, map_x, map_y, map_w, map_h, pins)
    # index, right of map: two columns
    ix = MX + 620
    idx_items = [(s[0], s[3]) for s in stories_heroes + stories_mids]
    f_idx = font(F_SANS, 10)
    f_idxn = font(F_SANS_B, 10)
    col_h = 7
    for j, (n, head) in enumerate(idx_items):
        col = j // col_h
        r = j % col_h
        tx = ix + col * 178
        ty = map_y + r * 15
        d.text((tx, ty), str(n), font=f_idxn, fill=RED)
        short = head if len(head) <= 26 else head[:25] + "…"
        d.text((tx + 16, ty), short, font=f_idx, fill=INK)
    y = map_y + map_h + 8  # ~ 830

    # --- tail
    d.text((MX, y), "ALSO ON SATURDAY 21 NOVEMBER", font=font(F_SANS_B, 12),
           fill=RED)
    y += 17
    n_tail = len(tail)
    cols = 4
    rows = (n_tail + cols - 1) // cols
    col_w = CW // cols
    f_tn = font(F_SANS_B, 10)
    f_tt = font(F_SANS, 10)
    start_n = len(stories_heroes) + len(stories_mids) + 1
    for j, (region, place, frag) in enumerate(tail):
        col = j // rows
        r = j % rows
        tx = MX + col * col_w
        ty = y + r * 15
        d.text((tx, ty), str(start_n + j), font=f_tn, fill=RED)
        d.text((tx + 20, ty), f"{place} — {frag}", font=f_tt, fill=INK)
    y += rows * 15 + 6

    # --- DATE CHECK (red box)
    box_h = 58
    d.rectangle([MX, y, W - MX, y + box_h], fill=DARKRED)
    d.text((MX + 10, y + 6),
           "DATE CHECK — Every story above happened or was first reported on Saturday 21 November 2026.",
           font=font(F_SANS_B, 11), fill=(255, 255, 255))
    dc_y = y + 22
    dc_txt = "  ".join("• " + item for item in datecheck)
    para(d, MX + 10, dc_y, dc_txt, font(F_SANS, 9), CW - 20,
         fill=(255, 235, 220), leading=12, max_lines=3)
    y += box_h + 6

    # --- footer
    d.line([MX, y, W - MX, y], fill=RULE, width=1)
    d.text((MX, y + 4), SOURCES, font=font(F_SANS, 8), fill=MUTED)
    y += 16
    print(f"render done: bottom y={y} (limit 1024), total stories={total}")
    assert y <= 1024, f"OVERFLOW: bottom y={y}"
    img.save(out_path, optimize=True)
    return y

if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry-final-v1.png")
    render(HEROES, MIDS, TAIL, STATS, DATECHECK, out)
    print("saved", out)

