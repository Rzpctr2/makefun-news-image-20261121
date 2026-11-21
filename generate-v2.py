#!/usr/bin/env python3
"""news-image-20261121 v2 generator — written fresh in this session.

Flat-vector broadsheet, 1024x1024, cream paper, serif masthead.
Single-newspaper genre per the 17-21 Nov winners cross-day analysis:
masthead + subhead, UTC strip, 6-number stat strip, region bar that
sums to 33, 3 drawn hero scenes with red label bars, 10 drawn mid
cards each tagged CONFIRMED/CLAIM, dotted world map with numbered
pins and a short legend, sequential tail #14-33, DATE CHECK box with
8 left-out items + 1 not-yet note, date-discipline footer.
Story set follows the v2 spec (story-gap doc section 6): hero trio
COP31 / Riyadh 3 missiles / Peru 6.7; Davao, Rahul 136, Vegas pole,
Canberra AI, China-Japan, Iran uranium and Trump data-centre tax in
the mid grid; Bitcoin and the Zelensky 'killer' quote demoted.
No VERDICT box. Output is RGB PNG, compress_level=9, optimize=True.
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "news-v2.json")))

W, H = 1024, 1024
PAPER = (244, 234, 211)
PAPER2 = (250, 243, 226)
INK = (26, 21, 18)
SOFT = (60, 54, 48)
RED = (166, 43, 31)
DEEPRED = (140, 35, 24)
NAVY = (30, 58, 95)
TEAL = (46, 110, 106)
GOLD = (201, 154, 46)
MUTED = (107, 93, 79)
GREEN = (34, 120, 60)
AMBER = (180, 120, 20)

PLAYFAIR = "/home/hatch/.fonts/PlayfairDisplay-Black.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def wrap(dr, text, fnt, max_w):
    """Greedy word wrap measured in pixels."""
    out, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if dr.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(dr, x, y, text, fnt, max_w, fill=INK, leading=None, limit=None):
    step = leading or int(fnt.size * 1.22)
    lines = wrap(dr, text, fnt, max_w)
    if limit:
        lines = lines[:limit]
    for line in lines:
        dr.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def tracked(dr, cx, y, text, fnt, fill=INK, gap=4):
    """Centred letter-spaced caps; returns total width."""
    widths = [dr.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + gap * (len(text) - 1)
    x = cx - total / 2
    for ch, wd in zip(text, widths):
        dr.text((x, y), ch, font=fnt, fill=fill)
        x += wd + gap
    return total


def tag(dr, right, top, label):
    """Small CONFIRMED/CLAIM chip, top-right of a scene."""
    fnt = F(SANS_B, 9)
    tw = dr.textlength(label, font=fnt)
    w, h = int(tw) + 12, 15
    bg = GREEN if label == "CONFIRMED" else AMBER
    dr.rounded_rectangle([right - w, top, right, top + h], radius=3, fill=bg)
    dr.text((right - w + 6, top + 3), label, font=fnt, fill=(255, 255, 255))


def badge(dr, x, y, n):
    """Red number badge, top-left of a scene."""
    fnt = F(SANS_B, 12)
    s = str(n)
    w = max(18, int(dr.textlength(s, font=fnt)) + 10)
    dr.rectangle([x, y, x + w, y + 18], fill=RED)
    dr.text((x + (w - dr.textlength(s, font=fnt)) / 2, y + 3), s,
            font=fnt, fill=(255, 255, 255))


def vgrad(dr, x, y, w, h, top, bottom, steps=20):
    for i in range(steps):
        t = i / (steps - 1)
        c = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        dr.rectangle([x, y + i * h / steps, x + w,
                      y + (i + 1) * h / steps + 1], fill=c)


# ------------------------------------------------------------------ map
# Stylised continent outlines (lon, lat), coarse on purpose: the map is
# a dotted halftone at ~600x92, not a survey chart.
LAND = [
    [(-168, 65), (-140, 70), (-120, 70), (-100, 68), (-85, 69), (-75, 70),
     (-65, 60), (-55, 47), (-65, 44), (-75, 38), (-80, 30), (-85, 29),
     (-90, 21), (-97, 18), (-105, 20), (-112, 25), (-120, 34), (-125, 42),
     (-125, 50), (-135, 58), (-152, 60), (-165, 60)],
    [(-58, 64), (-42, 60), (-32, 68), (-28, 71), (-45, 76), (-58, 75)],
    [(-79, 10), (-70, 12), (-60, 9), (-51, 4), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-57, -35), (-65, -45), (-70, -54), (-73, -40),
     (-71, -20), (-77, -12), (-80, -4)],
    [(-17, 15), (-15, 22), (-8, 31), (0, 36), (11, 37), (22, 33), (32, 31),
     (36, 27), (43, 12), (51, 11), (46, 0), (40, -15), (35, -26), (27, -33),
     (19, -35), (14, -28), (12, -18), (9, -1), (9, 4), (-8, 5), (-14, 9)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (6, 54), (9, 58), (18, 56),
     (22, 55), (26, 59), (30, 62), (42, 68), (58, 69), (70, 73), (90, 75),
     (112, 76), (135, 72), (155, 70), (172, 66), (178, 65), (163, 58),
     (156, 52), (142, 54), (140, 46), (132, 43), (127, 40), (121, 36),
     (117, 28), (110, 20), (105, 10), (103, 2), (99, 7), (95, 15), (91, 22),
     (86, 20), (80, 14), (76, 8), (72, 20), (66, 25), (60, 25), (55, 27),
     (50, 29), (44, 29), (38, 32), (35, 36), (28, 37), (23, 37), (19, 41),
     (13, 44), (8, 44), (3, 43), (-1, 38), (-7, 36)],
    [(113, -22), (114, -31), (119, -34), (128, -32), (134, -33), (139, -37),
     (146, -39), (150, -37), (153, -30), (150, -22), (146, -19), (142, -14),
     (141, -11), (134, -12), (128, -14), (122, -17), (117, -20)],
    [(109, 1), (114, 4), (118, 5), (119, -1), (116, -3), (111, -3)],
    [(95, 5), (100, 0), (104, -4), (106, -6), (102, -5), (98, 2)],
    [(105, -6), (110, -7), (114, -8), (113, -9), (107, -8)],
    [(131, -1), (137, -2), (141, -3), (146, -6), (147, -8), (141, -8),
     (135, -7), (131, -4)],
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (-1, 51)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (144, 44),
     (142, 41), (140, 36), (135, 34), (131, 33)],
    [(167, -45), (170, -42), (174, -39), (177, -38), (176, -40), (172, -43),
     (168, -46)],
    [(44, -16), (48, -17), (50, -22), (47, -25), (44, -21)],
]


def _inside(lon, lat, poly):
    hit = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
                (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            hit = not hit
        j = i
    return hit


def project(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 170) / 360.0 * w,
            y0 + (78 - lat) / 134.0 * h)


def dotted_map(dr, x0, y0, w, h, pins):
    step = 7
    for gy in range(int(y0), int(y0 + h), step):
        for gx in range(int(x0), int(x0 + w), step):
            lon = (gx - x0) / w * 360.0 - 170
            lat = 78 - (gy - y0) / h * 134.0
            if any(_inside(lon, lat, poly) for poly in LAND):
                dr.ellipse([gx - 1.4, gy - 1.4, gx + 1.4, gy + 1.4],
                           fill=(150, 128, 96))
    for lon, lat, n in pins:
        px, py = project(lon, lat, x0, y0, w, h)
        r = 8
        dr.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                   outline=(255, 255, 255), width=1)
        fnt = F(SANS_B, 8)
        s = str(n)
        dr.text((px - dr.textlength(s, font=fnt) / 2, py - 4), s,
                font=fnt, fill=(255, 255, 255))


# ------------------------------------------------------------------ scenes
# Each painter fills exactly (x, y, w, h). They run on a scratch image
# so nothing can bleed outside the scene box.

def sc_climate(dr, x, y, w, h):
    """COP31: dark teal hall, amber sun, globe, thermometer, clock."""
    vgrad(dr, x, y, w, h, (24, 62, 66), (16, 40, 52))
    cx, cy, r = x + w * 0.34, y + h * 0.46, h * 0.30
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(224, 148, 52))
    # globe
    gx, gy, gr = x + w * 0.66, y + h * 0.44, h * 0.30
    dr.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(38, 92, 140),
               outline=(240, 230, 210), width=2)
    for (ox, oy, ow, oh) in ((-0.20, -0.14, 0.26, 0.18), (0.00, 0.06, 0.24, 0.16),
                             (-0.08, -0.26, 0.16, 0.10)):
        dr.ellipse([gx + gr * ox, gy + gr * oy, gx + gr * (ox + ow),
                    gy + gr * (oy + oh)], fill=(96, 150, 84))
    # thermometer
    tx = x + w * 0.90
    dr.rounded_rectangle([tx - 5, y + h * 0.16, tx + 5, y + h * 0.72],
                         radius=5, fill=(240, 236, 224))
    dr.rectangle([tx - 2, y + h * 0.42, tx + 2, y + h * 0.70], fill=RED)
    dr.ellipse([tx - 9, y + h * 0.68, tx + 9, y + h * 0.86], fill=RED)
    # clock (no deal, time run out)
    kx, ky, kr = x + w * 0.10, y + h * 0.78, h * 0.13
    dr.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=(240, 236, 224),
               outline=INK, width=1)
    dr.line([kx, ky, kx, ky - kr + 3], fill=INK, width=2)
    dr.line([kx, ky, kx + kr - 4, ky + 2], fill=INK, width=2)
    # ground line
    dr.rectangle([x, y + h * 0.88, x + w, y + h], fill=(12, 30, 38))


def sc_missile(dr, x, y, w, h):
    """Riyadh night: skyline, lit windows, two intercept streaks."""
    vgrad(dr, x, y, w, h, (14, 20, 42), (52, 52, 88))
    rnd = random.Random(11)
    for _ in range(22):
        sx = x + rnd.random() * w
        sy = y + rnd.random() * h * 0.42
        dr.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(220, 220, 230))
    base = y + h * 0.82
    for (bx, bw, bh) in [(0.02, 0.08, 0.30), (0.12, 0.06, 0.44),
                         (0.20, 0.10, 0.26), (0.32, 0.07, 0.38),
                         (0.42, 0.09, 0.30), (0.55, 0.06, 0.46),
                         (0.63, 0.10, 0.28), (0.75, 0.08, 0.36),
                         (0.85, 0.10, 0.26)]:
        dr.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                     fill=(20, 24, 38))
        for wy in range(2):
            dr.rectangle([x + w * (bx + 0.015), base - h * bh + 4 + wy * 9,
                          x + w * (bx + 0.035), base - h * bh + 8 + wy * 9],
                         fill=(240, 200, 90))
    # intercept streaks + bursts
    dr.line([x + w * 0.28, y + h * 0.08, x + w * 0.55, y + h * 0.55],
            fill=(240, 200, 90), width=3)
    dr.line([x + w * 0.80, y + h * 0.05, x + w * 0.62, y + h * 0.48],
            fill=(240, 200, 90), width=3)
    for (bx, by, br) in ((0.55, 0.55, 6), (0.62, 0.48, 5)):
        dr.ellipse([x + w * bx - br, y + h * by - br, x + w * bx + br,
                    y + h * by + br], fill=(255, 220, 120))
    dr.rectangle([x, base, x + w, y + h], fill=(16, 18, 32))


def sc_quake(dr, x, y, w, h):
    """Peru: dust sky, seismograph trace, tilted house, cracked ground."""
    vgrad(dr, x, y, w, h, (206, 164, 110), (238, 214, 170))
    # seismograph panel
    px, py, pw, ph = x + w * 0.06, y + h * 0.12, w * 0.88, h * 0.38
    dr.rectangle([px, py, px + pw, py + ph], fill=(250, 244, 230),
                 outline=INK, width=1)
    pts = []
    n = 26
    for i in range(n + 1):
        xx = px + pw * i / n
        amp = (0.10 if i % 4 else 0.42) * ph * (1 if 8 <= i <= 18 else 0.25)
        yy = py + ph / 2 + (amp if i % 2 else -amp)
        pts.append((xx, yy))
    dr.line(pts, fill=RED, width=2)
    # ground + crack
    gy = y + h * 0.62
    dr.rectangle([x, gy, x + w, y + h], fill=(146, 100, 56))
    dr.line([x + w * 0.55, gy, x + w * 0.48, y + h], fill=(90, 56, 28), width=2)
    dr.line([x + w * 0.48, y + h * 0.82, x + w * 0.58, y + h * 0.92],
            fill=(90, 56, 28), width=2)
    # tilted house
    hx, hy = x + w * 0.14, gy
    dr.polygon([(hx, hy - h * 0.26), (hx + w * 0.10, hy - h * 0.26),
                (hx + w * 0.10, hy), (hx, hy)], fill=(196, 120, 70))
    dr.polygon([(hx - w * 0.02, hy - h * 0.26), (hx + w * 0.05, hy - h * 0.36),
                (hx + w * 0.12, hy - h * 0.26)], fill=(140, 60, 44))
    dr.rectangle([hx + w * 0.04, hy - h * 0.12, hx + w * 0.07, hy],
                 fill=(60, 40, 28))


def sc_bridge(dr, x, y, w, h):
    """Kyiv: dusk river, bridge deck, pylons, city, smoke."""
    vgrad(dr, x, y, w, h, (58, 74, 110), (214, 164, 120))
    dr.ellipse([x + w * 0.78 - 13, y + h * 0.16 - 13, x + w * 0.78 + 13,
                y + h * 0.16 + 13], fill=(232, 178, 90))
    base = y + h * 0.58
    for (bx, bw, bh, c) in [(0.02, 0.10, 0.30, (52, 56, 74)),
                            (0.14, 0.08, 0.42, (40, 44, 60)),
                            (0.24, 0.12, 0.26, (62, 66, 84)),
                            (0.62, 0.09, 0.36, (48, 52, 70)),
                            (0.73, 0.11, 0.28, (58, 62, 80)),
                            (0.86, 0.10, 0.40, (42, 46, 62))]:
        dr.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                     fill=c)
    for sx in (0.17, 0.77):
        for i, r in enumerate((5, 7, 9)):
            dr.ellipse([x + w * sx - r, base - h * 0.32 - i * 10 - r,
                        x + w * sx + r, base - h * 0.32 - i * 10 + r],
                       fill=(120, 116, 110))
    dr.rectangle([x, y + h * 0.72, x + w, y + h], fill=(52, 96, 128))
    dr.rectangle([x, y + h * 0.72, x + w, y + h * 0.75], fill=(120, 170, 200))
    by = y + h * 0.66
    dr.rectangle([x, by, x + w, by + 5], fill=(30, 30, 34))
    for px in (0.30, 0.70):
        dr.rectangle([x + w * px - 3, y + h * 0.30, x + w * px + 3, by],
                     fill=(30, 30, 34))
        dr.line([x + w * px, y + h * 0.30, x + w * 0.06, by],
                fill=(30, 30, 34), width=1)
        dr.line([x + w * px, y + h * 0.30, x + w * 0.94, by],
                fill=(30, 30, 34), width=1)


def sc_drone(dr, x, y, w, h):
    """Hormuz: sunset sea, tanker, drone silhouette, burst."""
    vgrad(dr, x, y, w, h, (34, 68, 96), (232, 158, 92))
    dr.ellipse([x + w * 0.20 - 15, y + h * 0.20 - 15, x + w * 0.20 + 15,
                y + h * 0.20 + 15], fill=(240, 200, 120))
    dr.rectangle([x, y + h * 0.62, x + w, y + h], fill=(28, 74, 106))
    for wy in (0.68, 0.78, 0.90):
        dr.line([x + w * 0.05, y + h * wy, x + w * 0.95, y + h * wy],
                fill=(90, 150, 185), width=2)
    tx, ty = x + w * 0.08, y + h * 0.70
    dr.rectangle([tx, ty, tx + w * 0.42, ty + h * 0.16], fill=(120, 40, 32))
    dr.rectangle([tx + w * 0.30, ty - h * 0.10, tx + w * 0.40, ty],
                 fill=(200, 200, 200))
    dx, dy = x + w * 0.68, y + h * 0.34
    dr.ellipse([dx - 22, dy - 5, dx + 22, dy + 5], fill=(24, 24, 28))
    dr.polygon([(dx - 22, dy), (dx - 34, dy - 10), (dx - 30, dy + 2)],
               fill=(24, 24, 28))
    dr.polygon([(dx + 22, dy), (dx + 34, dy - 10), (dx + 30, dy + 2)],
               fill=(24, 24, 28))
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        dr.line([dx + 26 * math.cos(a), dy + 26 * math.sin(a),
                 dx + 40 * math.cos(a), dy + 40 * math.sin(a)],
                fill=(240, 180, 60), width=3)


def sc_plane(dr, x, y, w, h):
    """Davao: pale sky, green fields, runway, airliner on the ground."""
    vgrad(dr, x, y, w, h, (168, 196, 214), (240, 228, 196))
    dr.ellipse([x + w * 0.84 - 12, y + h * 0.18 - 12, x + w * 0.84 + 12,
                y + h * 0.18 + 12], fill=(240, 200, 110))
    dr.rectangle([x, y + h * 0.58, x + w, y + h], fill=(110, 150, 90))
    dr.rectangle([x, y + h * 0.76, x + w, y + h], fill=(70, 70, 76))
    for i in range(5):
        xx = x + w * (0.08 + i * 0.20)
        dr.rectangle([xx, y + h * 0.84, xx + w * 0.10, y + h * 0.88],
                     fill=(240, 220, 120))
    # airliner, side view
    fx, fy = x + w * 0.12, y + h * 0.48
    dr.ellipse([fx, fy - h * 0.10, fx + w * 0.62, fy + h * 0.10],
               fill=(240, 240, 244))
    dr.polygon([(fx + w * 0.58, fy - h * 0.06), (fx + w * 0.72, fy - h * 0.02),
                (fx + w * 0.62, fy + h * 0.06)], fill=(240, 240, 244))
    dr.polygon([(fx + w * 0.20, fy), (fx + w * 0.34, fy + h * 0.22),
                (fx + w * 0.44, fy + h * 0.22), (fx + w * 0.36, fy)],
               fill=(200, 40, 40))
    dr.polygon([(fx + w * 0.52, fy - h * 0.08), (fx + w * 0.56, fy - h * 0.26),
                (fx + w * 0.62, fy - h * 0.26), (fx + w * 0.60, fy - h * 0.06)],
               fill=(30, 58, 95))
    for wx in (0.22, 0.48):
        dr.line([fx + w * wx, fy + h * 0.08, fx + w * wx, fy + h * 0.26],
                fill=(40, 40, 44), width=2)
        dr.ellipse([fx + w * wx - 3, fy + h * 0.26 - 3, fx + w * wx + 3,
                    fy + h * 0.26 + 3], fill=(20, 20, 24))
    for wx in range(6):
        dr.ellipse([fx + w * (0.16 + wx * 0.07) - 2, fy - h * 0.04 - 2,
                    fx + w * (0.16 + wx * 0.07) + 2, fy - h * 0.04 + 2],
                   fill=(30, 58, 95))


def sc_cricket(dr, x, y, w, h):
    """Wellington: green outfield, brown pitch, batsman, stumps, ball."""
    vgrad(dr, x, y, w, h, (120, 160, 100), (150, 185, 120))
    dr.rectangle([x, y + h * 0.78, x + w, y + h], fill=(90, 130, 76))
    # pitch strip
    px = x + w * 0.30
    dr.rectangle([px, y + h * 0.10, px + w * 0.40, y + h * 0.92],
                 fill=(198, 168, 118))
    dr.line([px, y + h * 0.10, px, y + h * 0.92], fill=(255, 255, 255), width=1)
    dr.line([px + w * 0.40, y + h * 0.10, px + w * 0.40, y + h * 0.92],
            fill=(255, 255, 255), width=1)
    # stumps
    sx = x + w * 0.46
    for k in range(3):
        dr.rectangle([sx + k * 6, y + h * 0.14, sx + k * 6 + 3, y + h * 0.30],
                     fill=(240, 200, 60))
    # batsman: head, body, legs, bat
    bx, by = x + w * 0.56, y + h * 0.52
    dr.ellipse([bx - 7, by - 26, bx + 7, by - 12], fill=(240, 220, 200))
    dr.ellipse([bx - 8, by - 27, bx + 8, by - 17], fill=(30, 58, 95))
    dr.rectangle([bx - 7, by - 12, bx + 7, by + 8], fill=(240, 240, 240))
    dr.rectangle([bx - 6, by + 8, bx - 1, by + 26], fill=(40, 40, 48))
    dr.rectangle([bx + 1, by + 8, bx + 6, by + 26], fill=(40, 40, 48))
    dr.line([bx + 4, by - 6, bx + 20, by + 22], fill=(160, 110, 60), width=5)
    # red ball in the air
    dr.ellipse([x + w * 0.82 - 5, y + h * 0.24 - 5, x + w * 0.82 + 5,
                y + h * 0.24 + 5], fill=RED)
    # crowd band
    for i, c in enumerate([(166, 43, 31), (30, 58, 95), (46, 110, 106),
                           (201, 154, 46), (90, 60, 120)]):
        dr.ellipse([x + w * (0.06 + i * 0.05) - 3, y + h * 0.05 - 3,
                    x + w * (0.06 + i * 0.05) + 3, y + h * 0.05 + 3], fill=c)


def sc_racecar(dr, x, y, w, h):
    """Las Vegas: neon night, strip glow, F1 car, chequered line."""
    vgrad(dr, x, y, w, h, (28, 18, 52), (72, 36, 96))
    rnd = random.Random(23)
    for _ in range(16):
        sx = x + rnd.random() * w
        sy = y + rnd.random() * h * 0.35
        dr.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(220, 200, 255))
    # neon strip glow
    for i, c in enumerate([(255, 80, 160), (80, 220, 255), (255, 200, 60)]):
        dr.rectangle([x, y + h * (0.30 + i * 0.06), x + w,
                      y + h * (0.34 + i * 0.06)], fill=c)
    base = y + h * 0.80
    dr.rectangle([x, base, x + w, y + h], fill=(20, 16, 30))
    # chequered start line
    for i in range(10):
        dr.rectangle([x + w * (0.05 + i * 0.04), base - 6,
                      x + w * (0.09 + i * 0.04), base],
                     fill=(255, 255, 255) if i % 2 == 0 else (20, 20, 24))
    # F1 car silhouette
    cx, cy = x + w * 0.50, base - h * 0.16
    dr.polygon([(cx - w * 0.34, cy), (cx - w * 0.10, cy - h * 0.10),
                (cx + w * 0.22, cy - h * 0.10), (cx + w * 0.36, cy)],
               fill=(200, 30, 40))
    dr.polygon([(cx + w * 0.26, cy - h * 0.10), (cx + w * 0.30, cy - h * 0.26),
                (cx + w * 0.36, cy - h * 0.26), (cx + w * 0.34, cy - h * 0.08)],
               fill=(160, 20, 30))
    dr.rectangle([cx - w * 0.38, cy - h * 0.16, cx - w * 0.34, cy + 2],
                 fill=(160, 20, 30))
    for wx in (-0.22, 0.24):
        dr.ellipse([cx + w * wx - 11, cy - 11, cx + w * wx + 11, cy + 11],
                   fill=(16, 16, 20), outline=(120, 120, 130), width=2)
        dr.ellipse([cx + w * wx - 4, cy - 4, cx + w * wx + 4, cy + 4],
                   fill=(200, 200, 210))


def sc_market(dr, x, y, w, h):
    """Markets: bank facade with columns, falling gold coins."""
    vgrad(dr, x, y, w, h, (96, 120, 140), (220, 200, 160))
    base = y + h * 0.80
    dr.rectangle([x + w * 0.18, y + h * 0.30, x + w * 0.82, base],
                 fill=(180, 168, 140))
    dr.polygon([(x + w * 0.12, y + h * 0.30), (x + w * 0.50, y + h * 0.10),
                (x + w * 0.88, y + h * 0.30)], fill=(150, 136, 108))
    for cx in (0.24, 0.40, 0.56, 0.70):
        dr.rectangle([x + w * cx, y + h * 0.38, x + w * (cx + 0.05), base],
                     fill=(140, 126, 98))
    dr.rectangle([x, base, x + w, y + h], fill=(110, 98, 76))
    for (cx, cy, r) in ((0.10, 0.30, 9), (0.88, 0.22, 8), (0.92, 0.55, 10),
                        (0.06, 0.62, 8)):
        dr.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                    y + h * cy + r], fill=GOLD, outline=(140, 100, 20), width=2)
        dr.text((x + w * cx - 3, y + h * cy - 5), "$", font=F(SANS_B, 10),
                fill=(120, 84, 16))


def sc_parliament(dr, x, y, w, h):
    """Canberra: domed parliament, flags, lawn."""
    vgrad(dr, x, y, w, h, (150, 170, 190), (235, 220, 190))
    base = y + h * 0.78
    dr.rectangle([x + w * 0.14, y + h * 0.42, x + w * 0.86, base],
                 fill=(170, 156, 128))
    dr.pieslice([x + w * 0.36, y + h * 0.08, x + w * 0.64, y + h * 0.52],
                start=180, end=360, fill=(140, 126, 100))
    dr.rectangle([x + w * 0.48, y + h * 0.02, x + w * 0.52, y + h * 0.10],
                 fill=(120, 106, 82))
    for cx in (0.20, 0.36, 0.52, 0.68):
        dr.rectangle([x + w * cx, y + h * 0.50, x + w * (cx + 0.06), base],
                     fill=(140, 126, 100))
    for i, c in enumerate([(166, 43, 31), (30, 58, 95), (46, 110, 106)]):
        fx = x + w * (0.30 + i * 0.20)
        dr.line([fx, base - h * 0.22, fx, base], fill=(60, 40, 24), width=2)
        dr.polygon([(fx, base - h * 0.22), (fx + w * 0.10, base - h * 0.18),
                    (fx, base - h * 0.14)], fill=c)
    dr.rectangle([x, base, x + w, y + h], fill=(120, 108, 88))


def sc_flags(dr, x, y, w, h):
    """Beijing-Tokyo: China flag and Japan flag side by side."""
    dr.rectangle([x, y, x + w, y + h], fill=(238, 228, 200))
    ex, ey, ew, eh = x + w * 0.06, y + h * 0.22, w * 0.40, h * 0.56
    dr.rectangle([ex, ey, ex + ew, ey + eh], fill=(200, 30, 30))
    dr.ellipse([ex + ew * 0.10 - 6, ey + eh * 0.12 - 6, ex + ew * 0.10 + 6,
                ey + eh * 0.12 + 6], fill=(240, 200, 60))
    for (sx, sy) in ((0.34, 0.10), (0.40, 0.24), (0.34, 0.38), (0.22, 0.30)):
        dr.ellipse([ex + ew * sx - 3, ey + eh * sy - 3, ex + ew * sx + 3,
                    ey + eh * sy + 3], fill=(240, 200, 60))
    ux, uy, uw, uh = x + w * 0.54, y + h * 0.22, w * 0.40, h * 0.56
    dr.rectangle([ux, uy, ux + uw, uy + uh], fill=(250, 250, 248))
    dr.ellipse([ux + uw / 2 - 10, uy + uh / 2 - 10, ux + uw / 2 + 10,
                uy + uh / 2 + 10], fill=(200, 30, 30))
    dr.arc([x + w * 0.30, y + h * 0.02, x + w * 0.70, y + h * 0.30],
           start=200, end=340, fill=RED, width=3)


def sc_atom(dr, x, y, w, h):
    """Tehran: atom orbits over a pale lab bench."""
    dr.rectangle([x, y, x + w, y + h], fill=(216, 228, 220))
    cx, cy = x + w * 0.50, y + h * 0.44
    for ang, col in ((0, TEAL), (60, NAVY), (120, RED)):
        a = math.radians(ang)
        rx, ry = w * 0.34, h * 0.16
        dr.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col, width=2)
        ex = cx + rx * math.cos(a)
        ey = cy + ry * math.sin(a)
        dr.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=col)
    dr.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=GOLD,
               outline=(140, 100, 20), width=2)
    dr.rectangle([x, y + h * 0.86, x + w, y + h], fill=(180, 190, 182))
    # small flask, bottom left
    fx, fy = x + w * 0.08, y + h * 0.62
    dr.rectangle([fx + 4, fy, fx + 12, fy + h * 0.10], fill=(200, 210, 215),
                 outline=(60, 70, 80), width=1)
    dr.polygon([(fx + 4, fy + h * 0.10), (fx + 12, fy + h * 0.10),
                (fx + 20, fy + h * 0.24), (fx - 4, fy + h * 0.24)],
               fill=(120, 180, 200), outline=(60, 70, 80))


def sc_tech(dr, x, y, w, h):
    """Washington: dark server room, chip, circuit traces."""
    dr.rectangle([x, y, x + w, y + h], fill=(18, 26, 40))
    for rx in (0.06, 0.72):
        dr.rectangle([x + w * rx, y + h * 0.14, x + w * (rx + 0.22),
                      y + h * 0.86], fill=(28, 42, 66))
        for k in range(4):
            yy = y + h * (0.22 + k * 0.16)
            dr.rectangle([x + w * (rx + 0.03), yy, x + w * (rx + 0.19),
                          yy + 5], fill=(60, 90, 140))
            dr.ellipse([x + w * (rx + 0.17) - 2, yy + 1, x + w * (rx + 0.17) + 2,
                        yy + 5], fill=(80, 220, 120))
    cx, cy, s = x + w * 0.50, y + h * 0.50, h * 0.22
    dr.rectangle([cx - s, cy - s, cx + s, cy + s], fill=NAVY,
                 outline=(90, 140, 200), width=2)
    dr.rectangle([cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.5],
                 fill=(70, 110, 180))
    for k in range(3):
        t = -s + (k + 0.5) * (2 * s / 3)
        dr.line([cx + t, cy - s - 7, cx + t, cy - s], fill=(90, 140, 200), width=2)
        dr.line([cx + t, cy + s, cx + t, cy + s + 7], fill=(90, 140, 200), width=2)


SCENES = {
    "climate": sc_climate, "missile": sc_missile, "quake": sc_quake,
    "bridge": sc_bridge, "drone": sc_drone, "plane": sc_plane,
    "cricket": sc_cricket, "racecar": sc_racecar, "market": sc_market,
    "parliament": sc_parliament, "flags": sc_flags, "atom": sc_atom,
    "tech": sc_tech,
}

# Feature coordinates (lon, lat) for the map pins, keyed by story number.
COORDS = {
    1: (30.7, 36.9), 2: (46.7, 24.7), 3: (-75.2, -11.2), 4: (30.5, 50.45),
    5: (56.5, 26.5), 6: (125.6, 7.07), 7: (174.8, -41.3), 8: (-115.1, 36.2),
    9: (-74.0, 40.7), 10: (149.1, -35.3), 11: (116.4, 39.9),
    12: (51.4, 35.7), 13: (-77.0, 38.9),
}

REGIONS = ["EUROPE", "ASIA", "MIDDLE EAST", "AFRICA", "AMERICAS",
           "OCEANIA", "GLOBAL"]

MX = 24
CW = W - 2 * MX


def paint_scene(img, name, x, y, w, h):
    """Render one scene on a scratch tile so painters cannot overflow."""
    tile = Image.new("RGB", (w, h), PAPER)
    td = ImageDraw.Draw(tile)
    SCENES[name](td, 0, 0, w, h)
    img.paste(tile, (x, y))


def build(out_path):
    heroes = DATA["heroes"]
    mids = DATA["mids"]
    tail = DATA["tail"]
    stats = DATA["stats"]
    total = len(heroes) + len(mids) + len(tail)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- kicker + masthead
    y = 10
    tracked(d, W // 2, y, "THE WORLD IN ONE DAY", F(SANS_B, 11), fill=INK, gap=4)
    y = 26
    d.text((W // 2, y), "Saturday 21 November 2026",
           font=F(PLAYFAIR, 48), fill=INK, anchor="ma")
    y = 88
    sub = " · ".join(h["headline"] for h in heroes)
    d.text((W // 2, y), sub, font=F(SERIF_I, 15), fill=RED, anchor="ma")
    y = 110
    d.line([MX, y, W - MX, y], fill=INK, width=2)
    d.line([MX, y + 4, W - MX, y + 4], fill=INK, width=1)

    # --- UTC strip: 6 slots, 1 event each
    y = 118
    d.rectangle([MX, y, W - MX, y + 32], outline=INK, width=1)
    d.text((MX + 8, y + 9), "THE DAY IN UTC", font=F(SANS_B, 10), fill=RED)
    slot_w = (CW - 118) // 6
    for i, slot in enumerate(DATA["utc_strip"]):
        sx = MX + 118 + i * slot_w
        d.text((sx, y + 3), slot["time"], font=F(SANS_B, 10), fill=RED)
        para(d, sx, y + 16, slot["event"], F(SANS, 8), slot_w - 8,
             fill=INK, leading=10, limit=2)
    y += 38

    # --- stat strip: 6 boxes, 6 different stories
    bw = CW // 6
    for i, st in enumerate(stats):
        bx = MX + i * bw
        d.rectangle([bx + 2, y, bx + bw - 2, y + 50], outline=INK, width=1)
        d.text((bx + bw / 2, y + 3), st["number"], font=F(SANS_B, 20),
               fill=RED, anchor="ma")
        para(d, bx + 8, y + 27, st["label"], F(SANS, 9), bw - 16,
             fill=INK, leading=11, limit=2)
    y += 56

    # --- region bar (counts sum to total)
    counts = {r: 0 for r in REGIONS}
    for s in heroes + mids:
        counts[s["region"]] += 1
    for t in tail:
        counts[t["region"]] += 1
    parts = [f"{r}  {counts[r]}" for r in REGIONS if counts[r] > 0]
    d.text((W // 2, y), "   ·   ".join(parts), font=F(SANS_B, 11),
           fill=INK, anchor="ma")
    y += 18

    # --- heroes: red label bar + scene + kicker + headline + standfirst
    hw = (CW - 2 * 12) // 3
    hh = 92
    for i, s in enumerate(heroes):
        hx = MX + i * (hw + 12)
        d.rectangle([hx, y, hx + hw, y + 18], fill=RED)
        d.text((hx + 6, y + 3), s["label"], font=F(SANS_B, 10),
               fill=(255, 255, 255))
        paint_scene(img, s["scene"], hx, y + 18, hw, hh)
        d.rectangle([hx, y + 18, hx + hw, y + 18 + hh], outline=INK, width=1)
        badge(d, hx + 4, y + 22, s["n"])
        tag(d, hx + hw - 4, y + 22, s["chip"])
        ky = y + 18 + hh + 6
        d.text((hx, ky), s["kicker"], font=F(SANS_B, 9), fill=RED)
        hy = ky + 13
        para(d, hx, hy, s["headline"], F(SERIF_B, 19), hw, fill=INK,
             leading=21, limit=2)
        sy = hy + 43
        para(d, hx, sy, s["standfirst"], F(SANS, 11), hw, fill=SOFT,
             leading=13, limit=2)
    y += 18 + hh + 6 + 13 + 43 + 27

    # --- MORE FROM THE DAY band
    d.rectangle([MX, y, W - MX, y + 20], fill=RED)
    d.text((MX + 8, y + 4), "MORE FROM THE DAY", font=F(SANS_B, 12),
           fill=(255, 255, 255))
    y += 26

    # --- mid grid: 5 cols x 2 rows
    mw = (CW - 4 * 10) // 5
    mh = 58
    for row in range(2):
        for col in range(5):
            s = mids[row * 5 + col]
            mx = MX + col * (mw + 10)
            my = y
            paint_scene(img, s["scene"], mx, my, mw, mh)
            d.rectangle([mx, my, mx + mw, my + mh], outline=INK, width=1)
            badge(d, mx + 3, my + 3, s["n"])
            tag(d, mx + mw - 3, my + 3, s["chip"])
            ky = my + mh + 4
            d.text((mx, ky), s["kicker"], font=F(SANS_B, 8), fill=RED)
            hy = ky + 11
            para(d, mx, hy, s["headline"], F(SERIF_B, 13), mw, fill=INK,
                 leading=14, limit=2)
            sy = hy + 29
            para(d, mx, sy, s["standfirst"], F(SANS, 9), mw, fill=SOFT,
                 leading=11, limit=2)
        y += mh + 4 + 11 + 29 + 25
    # --- map + legend
    d.text((MX, y), "WHERE IT HAPPENED", font=F(SANS_B, 12), fill=RED)
    d.text((W - MX, y + 2),
           "Red numbers mark stories 1–13. Positions are approximate.",
           font=F(SANS, 9), fill=MUTED, anchor="ra")
    y += 18
    map_x, map_y, map_w, map_h = MX, y, 600, 100
    nudge = {1: (3, -2), 2: (-6, 3), 4: (-4, 2), 5: (5, 3), 9: (4, -4),
             11: (-4, 2), 12: (4, 1)}
    pins = []
    for s in heroes + mids:
        lon, lat = COORDS[s["n"]]
        dlon, dlat = nudge.get(s["n"], (0, 0))
        pins.append((lon + dlon, lat + dlat, s["n"]))
    dotted_map(d, map_x, map_y, map_w, map_h, pins)
    # legend, right of map: 2 short columns, nothing truncated
    lx = MX + 620
    col_w = 178
    for j, label in enumerate(DATA["legend"]):
        col, r = divmod(j, 7)
        tx = lx + col * col_w
        ty = map_y + r * 14
        d.text((tx, ty), str(j + 1), font=F(SANS_B, 10), fill=RED)
        d.text((tx + 16, ty), label, font=F(SANS, 10), fill=INK)
    y = map_y + map_h + 8

    # --- tail #14-33, 4 columns x 5 rows
    d.text((MX, y), "ALSO ON SATURDAY 21 NOVEMBER", font=F(SANS_B, 12),
           fill=RED)
    y += 16
    cols, rows = 4, 5
    col_w = CW // cols
    start_n = 14
    for j, t in enumerate(tail):
        col, r = divmod(j, rows)
        tx = MX + col * col_w
        ty = y + r * 14
        d.text((tx, ty), str(start_n + j), font=F(SANS_B, 10), fill=RED)
        d.text((tx + 20, ty), f"{t['place']} — {t['brief']}",
               font=F(SANS, 10), fill=INK)
    y += rows * 14 + 6

    # --- DATE CHECK box: 8 left-out items + 1 not-yet note
    dc_items = DATA["date_check"]
    dc_body = "   ".join("• " + item for item in dc_items)
    dc_body += "   NOT YET: " + DATA["date_check_not_yet"]
    dc_lines = wrap(d, dc_body, F(SANS, 9), CW - 20)
    box_h = 22 + len(dc_lines) * 12 + 6
    d.rectangle([MX, y, W - MX, y + box_h], fill=DEEPRED)
    d.text((MX + 10, y + 5),
           "DATE CHECK — Every story above happened or was first reported "
           "on Saturday 21 November 2026.",
           font=F(SANS_B, 11), fill=(255, 255, 255))
    para(d, MX + 10, y + 21, dc_body, F(SANS, 9), CW - 20,
         fill=(255, 235, 220), leading=12)
    y += box_h + 6

    # --- footer: date discipline + sources
    d.line([MX, y, W - MX, y], fill=INK, width=1)
    d.text((MX, y + 4),
           "Every story here happened or was first reported on Saturday "
           "21 November 2026. " + DATA["sources"],
           font=F(SANS, 8), fill=MUTED)
    y += 16

    print(f"render done: bottom y={y} (limit 1024), total stories={total}, "
          f"DATE CHECK lines={len(dc_lines)}")
    assert y <= 1024, f"OVERFLOW: bottom y={y}"
    img.save(out_path, optimize=True, compress_level=9)
    return y


if __name__ == "__main__":
    out = os.path.join(HERE, "entry-final-v2.png")
    build(out)
    print("saved", out)
