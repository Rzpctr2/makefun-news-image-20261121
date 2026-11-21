#!/usr/bin/env python3
"""Render the news-image 21 Nov 2026 v3 front page (1024x1024 PNG).

One-day broadsheet: 35 stories (3 heroes + 10 mids + 22 tail), a dotted
world map with numbered pins, a UTC strip, a six-number stat strip, a
region bar that sums to 35, and an 11-item DATE CHECK box modelled on the
18 Nov playoff winner ("LEFT OUT AS OLDER NEWS").

Everything here is drawn with PIL primitives from the story record in
news-v3.json. Output is deterministic: same input bytes give the same
output bytes, which verify-v3.py checks by rendering twice.
"""

import hashlib
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "news-v3.json")
OUT_PATH = os.path.join(HERE, "entry-final-v3.png")
W, H = 1024, 1024
MARGIN = 24
CONTENT_W = W - 2 * MARGIN

# --- palette: warm paper, deep navy ink, signal red -------------------------
PAPER = (247, 241, 227)
PAPER_DARK = (238, 230, 210)
INK = (27, 39, 64)
INK_SOFT = (74, 70, 60)
RED = (168, 35, 43)
RED_DARK = (142, 29, 36)
GOLD = (233, 161, 59)
GOLD_SOFT = (240, 196, 110)
TEAL = (46, 125, 123)
TEAL_DARK = (28, 84, 96)
GREEN = (47, 122, 61)
AMBER = (217, 142, 31)
CREAM = (250, 246, 236)
NIGHT = (16, 28, 52)
NIGHT_SOFT = (28, 44, 78)
SKY = (140, 178, 205)
WHITE = (255, 255, 255)
GREY = (107, 98, 87)
LINE = (180, 168, 142)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_TITLE = font("DejaVuSerif-Bold.ttf", 50)
F_SERIF_B = font("DejaVuSerif-Bold.ttf", 20)
F_SERIF = font("DejaVuSerif.ttf", 14)
F_SANS_B = font("DejaVuSans-Bold.ttf", 14)
F_SANS = font("DejaVuSans.ttf", 12)
F_SANS_SM = font("DejaVuSans.ttf", 11)
F_SANS_XS = font("DejaVuSans.ttf", 10)
F_SANS_XXS = font("DejaVuSans.ttf", 9)
F_SANS_B_SM = font("DejaVuSans-Bold.ttf", 11)
F_SANS_B_XS = font("DejaVuSans-Bold.ttf", 10)
F_SANS_B_XXS = font("DejaVuSans-Bold.ttf", 9)
F_SANS_B_TINY = font("DejaVuSans-Bold.ttf", 8)
F_NUM_B = font("DejaVuSans-Bold.ttf", 26)
F_NUM_BIG = font("DejaVuSans-Bold.ttf", 30)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = fnt.size + 3
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tracked(draw, x, y, text, fnt, fill, gap=2):
    """Draw caps text with manual letter spacing; returns width used."""
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=fnt, fill=fill)
        cx += draw.textlength(ch, font=fnt) + gap
    return cx - x


def badge(draw, x, y, num, size=17):
    """Red square with a white story number."""
    draw.rectangle([x, y, x + size, y + size], fill=RED)
    label = str(num)
    fnt = F_SANS_B_XS if num < 10 else F_SANS_B_XXS
    tw = draw.textlength(label, font=fnt)
    th = fnt.size
    draw.text((x + (size - tw) / 2, y + (size - th) / 2 - 1),
              label, font=fnt, fill=WHITE)


def chip(draw, x_right, y, text):
    """Small CONFIRMED (green) / CLAIM (amber) pill, right-aligned."""
    fnt = F_SANS_B_TINY
    pad = 6
    tw = draw.textlength(text, font=fnt)
    wbox = tw + pad * 2
    hbox = 13
    x0 = x_right - wbox
    bg = GREEN if text == "CONFIRMED" else AMBER
    fg = WHITE if text == "CONFIRMED" else INK
    draw.rounded_rectangle([x0, y, x_right, y + hbox], radius=6, fill=bg)
    draw.text((x0 + pad, y + 2), text, font=fnt, fill=fg)
    return x0

# --- scenes ------------------------------------------------------------------
# Each scene draws inside its own box (x, y, w, h) and returns nothing.
# All shapes are flat and simple on purpose: the palette quantiser that
# shrinks the file later needs flat colour fields, not gradients.

def scene_climate_clock(d, x, y, w, h):
    """COP31: globe + thermometer + a clock face for the missed deadline."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    d.ellipse([x + 8, y + h - 58, x + 66, y + h], fill=GOLD)
    d.ellipse([x + w // 2 - 26, y + 8, x + w // 2 + 26, y + 60],
              fill=(58, 110, 168))
    d.ellipse([x + w // 2 - 12, y + 16, x + w // 2 + 2, y + 30],
              fill=(86, 160, 96))
    d.ellipse([x + w // 2 + 6, y + 34, x + w // 2 + 20, y + 50],
              fill=(86, 160, 96))
    d.rectangle([x + w - 30, y + 10, x + w - 18, y + h - 22],
                fill=(240, 240, 235))
    d.rectangle([x + w - 28, y + h - 30, x + w - 20, y + h - 12],
                fill=RED)
    d.ellipse([x + w - 34, y + h - 24, x + w - 14, y + h - 4], fill=RED)
    cx, cy, r = x + 52, y + h - 26, 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CREAM,
              outline=INK, width=2)
    d.line([cx, cy, cx, cy - r + 5], fill=INK, width=2)
    d.line([cx, cy, cx + r - 8, cy + 5], fill=RED, width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=INK)


def scene_missile(d, x, y, w, h):
    """Riyadh: night skyline, two intercept trails, burst flashes."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    for sx, sy in [(14, 8), (60, 16), (110, 6), (170, 14), (230, 8),
                   (280, 18), (40, 26), (200, 24)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(10, 18, 36))
    for bx, bw, bh in [(6, 34, 22), (48, 26, 30), (82, 40, 18),
                       (130, 30, 34), (168, 36, 22), (212, 28, 28),
                       (248, 34, 20), (290, 24, 26)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(8, 14, 28))
        for wy in range(y + h - bh + 4, y + h - 4, 8):
            d.rectangle([x + bx + 5, wy, x + bx + 9, wy + 4], fill=GOLD_SOFT)
    d.line([x + 150, y + h - 30, x + 235, y + 12], fill=GOLD, width=2)
    d.line([x + 90, y + h - 30, x + 165, y + 20], fill=GOLD_SOFT, width=2)
    for bx, by in [(238, 10), (168, 18)]:
        d.ellipse([x + bx - 7, y + by - 7, x + bx + 7, y + by + 7],
                  fill=GOLD)
        d.ellipse([x + bx - 3, y + by - 3, x + bx + 3, y + by + 3],
                  fill=WHITE)


def scene_quake(d, x, y, w, h):
    """Peru: seismograph band on top, a house on cracked ground."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 205, 165))
    d.rectangle([x, y, x + w, y + 26], fill=CREAM)
    pts = [(x + 4, y + 13)]
    zig = [0, -8, 4, -4, 12, 6, -10, 3, 8, -6, 2, 0, -3, 5, -9, 4]
    cx = x + 8
    for step in zig:
        cx += 18
        pts.append((cx, y + 13 + step))
    d.line(pts, fill=RED, width=2)
    hx, hy = x + w // 2 - 34, y + h - 46
    d.rectangle([hx, hy + 14, hx + 68, hy + 40], fill=(150, 92, 58))
    d.polygon([(hx - 6, hy + 15), (hx + 34, hy - 8), (hx + 74, hy + 15)],
              fill=(120, 62, 40))
    d.rectangle([hx + 28, hy + 24, hx + 40, hy + 40], fill=(60, 40, 26))
    d.line([x + 20, y + h - 6, x + 90, y + h - 14, x + 150, y + h - 6,
            x + 220, y + h - 12, x + 290, y + h - 5], fill=(90, 60, 34),
           width=2)
    d.line([x + 120, y + h - 2, x + 130, y + h - 12, x + 142, y + h - 4],
           fill=(90, 60, 34), width=2)


def scene_nightstrike(d, x, y, w, h):
    """Kryvyi Rih: night strike — explosion bloom over dark rooftops."""
    d.rectangle([x, y, x + w, y + h], fill=(12, 14, 26))
    for sx, sy in [(10, 6), (40, 12), (150, 6), (176, 14), (60, 20)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
    d.rectangle([x, y + h - 18, x + w, y + h], fill=(8, 10, 20))
    for bx, bw, bh in [(4, 30, 16), (40, 24, 22), (120, 34, 14),
                       (160, 26, 20)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h],
                    fill=(6, 8, 16))
    ex, ey = x + w // 2 + 18, y + 26
    for r, col in [(20, (217, 110, 31)), (13, GOLD), (7, (255, 230, 150))]:
        d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col)
    for dx, dy in [(-26, 6), (26, -4), (-16, -12), (20, 12), (0, -20)]:
        d.ellipse([ex + dx - 5, ey + dy - 4, ex + dx + 5, ey + dy + 4],
                  fill=(120, 120, 130))
    d.polygon([(ex - 26, ey + 16), (ex - 8, ey + 4), (ex - 4, ey + 22)],
              fill=(217, 110, 31))
    d.polygon([(ex + 24, ey + 14), (ex + 8, ey + 4), (ex + 4, ey + 20)],
              fill=(217, 110, 31))


def scene_spacecraft(d, x, y, w, h):
    """BepiColombo: crescent Mercury and a small probe with panels."""
    d.rectangle([x, y, x + w, y + h], fill=(8, 10, 22))
    for sx, sy in [(8, 8), (30, 18), (70, 6), (120, 12), (160, 8),
                   (180, 20), (100, 22), (50, 30)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
    mx, my, mr = x + 34, y + h // 2 + 4, 22
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(168, 160, 148))
    d.ellipse([mx - mr + 12, my - mr - 4, mx + mr + 12, my + mr - 4],
              fill=(8, 10, 22))
    px, py = x + w - 78, y + 16
    d.rectangle([px, py + 8, px + 44, py + 16], fill=(40, 90, 160))
    d.rectangle([px + 50, py + 8, px + 58, py + 16], fill=GOLD)
    d.rectangle([px + 64, py + 8, px + 108, py + 16], fill=(40, 90, 160))
    d.polygon([(px + 50, py + 8), (px + 58, py + 2), (px + 58, py + 22),
               (px + 50, py + 16)], fill=(200, 200, 200))
    d.line([px + 108, py + 12, px + 118, py + 12], fill=GOLD, width=2)
    d.ellipse([px + 116, py + 9, px + 122, py + 15], fill=GOLD)


def scene_natostar(d, x, y, w, h):
    """Warsaw: a big four-point NATO compass star on deep blue."""
    d.rectangle([x, y, x + w, y + h], fill=(18, 48, 96))
    cx, cy = x + w // 2, y + h // 2 - 4
    d.polygon([(cx, cy - 24), (cx + 6, cy - 6), (cx + 24, cy),
               (cx + 6, cy + 6), (cx, cy + 24), (cx - 6, cy + 6),
               (cx - 24, cy), (cx - 6, cy - 6)], fill=WHITE)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(18, 48, 96))
    for sx, sy in [(12, 8), (w - 18, 10), (16, h - 22), (w - 22, h - 26)]:
        d.polygon([(x + sx, y + sy - 5), (x + sx + 2, y + sy - 2),
                   (x + sx + 5, y + sy), (x + sx + 2, y + sy + 2),
                   (x + sx, y + sy + 5), (x + sx - 2, y + sy + 2),
                   (x + sx - 5, y + sy), (x + sx - 2, y + sy - 2)],
                  fill=GOLD)
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(10, 26, 56))


def scene_drone(d, x, y, w, h):
    """Hormuz: a drone silhouette over a strait at sunset."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 132, 62))
    d.ellipse([x + w - 46, y + 6, x + w - 10, y + 42], fill=GOLD_SOFT)
    d.rectangle([x, y + h // 2 + 6, x + w, y + h], fill=(28, 84, 96))
    for wy in (h // 2 + 16, h // 2 + 26, h - 8):
        d.line([x + 8, y + wy, x + 60, y + wy, x + 110, y + wy + 3,
                x + w - 8, y + wy], fill=(120, 190, 200), width=2)
    dx, dy = x + w // 2 - 6, y + 12
    d.ellipse([dx - 12, dy, dx + 12, dy + 8], fill=(24, 24, 30))
    d.line([dx - 26, dy + 4, dx + 26, dy + 4], fill=(24, 24, 30), width=3)
    d.line([dx, dy + 4, dx, dy + 12], fill=(24, 24, 30), width=3)
    d.ellipse([dx + 18, dy + 2, dx + 22, dy + 6], fill=RED)


def scene_plane(d, x, y, w, h):
    """Davao: a jet on final approach above its runway lights."""
    d.rectangle([x, y, x + w, y + h], fill=(168, 198, 220))
    d.ellipse([x + 10, y + 8, x + 34, y + 26], fill=WHITE)
    d.ellipse([x + 60, y + 16, x + 78, y + 30], fill=WHITE)
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(60, 66, 72))
    for lx in range(10, w - 6, 26):
        d.ellipse([x + lx, y + h - 9, x + lx + 5, y + h - 4],
                  fill=GOLD)
    px, py = x + 30, y + 12
    d.polygon([(px, py + 12), (px + 108, py + 8), (px + 122, py + 14),
               (px + 108, py + 20), (px, py + 18)], fill=WHITE)
    d.polygon([(px + 96, py + 8), (px + 108, py - 6), (px + 116, py + 8)],
              fill=WHITE)
    d.polygon([(px + 52, py + 18), (px + 66, py + 30), (px + 74, py + 18)],
              fill=WHITE)
    d.ellipse([px + 108, py + 10, px + 118, py + 18], fill=(200, 60, 50))
    d.rectangle([px + 20, py + 13, px + 60, py + 16], fill=SKY)


def scene_cricket(d, x, y, w, h):
    """Wellington: a batsman, stumps and a red ball on a green pitch."""
    d.rectangle([x, y, x + w, y + h], fill=(46, 110, 62))
    d.rectangle([x + w // 2 - 40, y, x + w // 2 + 40, y + h],
                fill=(120, 150, 90))
    bx, by = x + w // 2 - 8, y + 8
    d.ellipse([bx - 6, by, bx + 6, by + 12], fill=(240, 220, 190))
    d.rectangle([bx - 8, by + 13, bx + 8, by + 30], fill=WHITE)
    d.rectangle([bx - 8, by + 30, bx - 2, by + 44], fill=(40, 40, 44))
    d.rectangle([bx + 2, by + 30, bx + 8, by + 44], fill=(40, 40, 44))
    d.line([bx + 6, by + 16, bx + 22, by + 40], fill=(150, 110, 60),
           width=4)
    for sx in (-16, -12, -8):
        d.line([x + w // 2 + sx, y + h - 20, x + w // 2 + sx, y + h - 6],
               fill=GOLD, width=2)
    d.ellipse([x + w // 2 + 26, y + h - 14, x + w // 2 + 34, y + h - 6],
              fill=RED)


def scene_racecar(d, x, y, w, h):
    """Las Vegas: a red F1 car under neon strips, chequered edge."""
    d.rectangle([x, y, x + w, y + h], fill=(22, 16, 40))
    d.rectangle([x, y + 6, x + w, y + 10], fill=(230, 60, 140))
    d.rectangle([x, y + 12, x + w, y + 15], fill=(60, 220, 220))
    for i in range(8):
        col = WHITE if i % 2 == 0 else INK
        d.rectangle([x + w - 16 + (i % 2) * 8, y + 20 + (i // 2) * 8,
                     x + w - 8 + (i % 2) * 8, y + 28 + (i // 2) * 8],
                    fill=col)
    cx, cy = x + 26, y + h - 22
    d.polygon([(cx, cy), (cx + 84, cy - 4), (cx + 108, cy + 2),
               (cx + 100, cy + 8), (cx + 8, cy + 8)], fill=(200, 40, 40))
    d.polygon([(cx + 40, cy - 2), (cx + 52, cy - 12), (cx + 70, cy - 10),
               (cx + 66, cy - 2)], fill=(30, 30, 36))
    for wx in (cx + 18, cx + 88):
        d.ellipse([wx - 8, cy + 2, wx + 8, cy + 16], fill=(12, 12, 14),
                  outline=GREY, width=1)
    d.line([x, y + h - 4, x + w, y + h - 4], fill=GOLD, width=2)


def scene_market(d, x, y, w, h):
    """Bitcoin: a gold coin with a falling red chart line."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    cx, cy, r = x + 52, y + h // 2 + 2, 24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
              outline=(180, 120, 30), width=2)
    d.text((cx - 8, cy - 13), "₿", font=font("DejaVuSans-Bold.ttf", 24),
           fill=(120, 70, 10))
    d.line([x + w - 78, y + 10, x + w - 56, y + 18, x + w - 38, y + 14,
            x + w - 18, y + 30, x + w - 6, y + 40], fill=RED, width=3)
    d.polygon([(x + w - 6, y + 40), (x + w - 12, y + 34),
               (x + w - 12, y + 42)], fill=RED)


def scene_atom(d, x, y, w, h):
    """Tehran: an atom — nucleus with three tilted orbits."""
    d.rectangle([x, y, x + w, y + h], fill=TEAL_DARK)
    cx, cy = x + w // 2, y + h // 2
    for (rx, ry), col in [((52, 18), (140, 220, 210)),
                          ((44, 26), (220, 180, 110)),
                          ((58, 10), (240, 240, 240))]:
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col,
                  width=2)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=GOLD)
    d.ellipse([cx + 44, cy - 8, cx + 50, cy - 2], fill=WHITE)
    d.ellipse([cx - 30, cy + 12, cx - 24, cy + 18], fill=WHITE)


def scene_tech(d, x, y, w, h):
    """Washington: server racks and a chip."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 30, 44))
    for rx in (8, 62, 116):
        d.rectangle([x + rx, y + 6, x + rx + 44, y + h - 6],
                    fill=(40, 50, 68), outline=(90, 100, 120), width=1)
        for ry in range(10, h - 8, 10):
            col = (90, 220, 120) if (rx + ry) % 20 == 0 else (200, 60, 60)
            d.ellipse([x + rx + 6, y + ry, x + rx + 10, y + ry + 4],
                      fill=col)
    cx, cy = x + w - 34, y + h // 2
    d.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], fill=GOLD)
    d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=INK)
    for k in range(-1, 2):
        d.line([cx - 16, cy + k * 8, cx - 12, cy + k * 8], fill=GOLD,
               width=2)
        d.line([cx + 12, cy + k * 8, cx + 16, cy + k * 8], fill=GOLD,
               width=2)


SCENES = {
    "climate-clock": scene_climate_clock,
    "missile": scene_missile,
    "quake": scene_quake,
    "nightstrike": scene_nightstrike,
    "spacecraft": scene_spacecraft,
    "natostar": scene_natostar,
    "drone": scene_drone,
    "plane": scene_plane,
    "cricket": scene_cricket,
    "racecar": scene_racecar,
    "market": scene_market,
    "atom": scene_atom,
    "tech": scene_tech,
}

# --- dotted world map ----------------------------------------------------------
# Rough continent outlines in lon/lat, drawn as dots. Positions are
# approximate, which the legend says outright.

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 73), (-65, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 26),
     (-85, 30), (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
     (-125, 48), (-135, 60), (-155, 58), (-165, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-58, -38), (-65, -45), (-70, -55), (-73, -40),
     (-73, -20), (-80, -5)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (51, 10), (48, 0), (40, -10), (35, -20),
     (30, -30), (20, -35), (15, -28), (12, -18), (8, -2), (9, 4), (-8, 5)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 70), (40, 68),
     (45, 68), (40, 60), (35, 55), (30, 50), (28, 45), (23, 40),
     (19, 42), (12, 44), (8, 44), (3, 42), (0, 39), (-2, 37), (-9, 37)],
    # Asia
    [(30, 70), (45, 68), (60, 70), (75, 73), (90, 75), (110, 77),
     (130, 72), (150, 70), (162, 60), (158, 52), (142, 50), (140, 40),
     (130, 35), (127, 33), (122, 30), (115, 22), (108, 18), (105, 10),
     (100, 8), (98, 15), (95, 16), (90, 22), (85, 20), (80, 13),
     (77, 8), (72, 20), (66, 25), (60, 25), (55, 26), (50, 29), (48, 30),
     (43, 28), (40, 32), (35, 36), (30, 36)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32),
     (135, -35), (140, -38), (147, -39), (150, -37), (153, -27),
     (146, -19), (142, -11), (136, -12), (132, -11), (126, -14),
     (122, -17), (118, -20)],
]

# story number -> (lon, lat) for the map pin
PINS = {
    1: (36.9, 36.9),    # Antalya
    2: (46.7, 24.6),    # Riyadh
    3: (-75.2, -11.1),  # Junin, Peru
    4: (33.4, 47.9),    # Kryvyi Rih
    5: (8.7, 49.9),     # Darmstadt (ESOC, BepiColombo control)
    6: (21.0, 52.2),    # Warsaw
    7: (56.5, 26.5),    # Hormuz
    8: (125.6, 7.1),    # Davao
    9: (174.8, -41.3),  # Wellington
    10: (-115.1, 36.2),  # Las Vegas
    11: (-87.6, 41.9),  # Chicago (markets)
    12: (51.4, 35.7),   # Tehran
    13: (-77.0, 38.9),  # Washington DC
}


def inside_polygon(lon, lat, poly):
    """Ray-casting point-in-polygon test."""
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            cross = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < cross:
                inside = not inside
        j = i
    return inside


def on_land(lon, lat):
    return any(inside_polygon(lon, lat, c) for c in CONTINENTS)


# Small manual nudges (px) so the dense Europe / Gulf pin cluster stays
# readable; positions remain approximate, as the legend states.
PIN_NUDGE = {
    1: (-6, 4), 2: (-16, 10), 4: (12, -6), 5: (-9, -7), 6: (0, -11),
    7: (7, 5), 12: (10, -6),
}


def draw_map(d, x0, y0, x1, y1):
    """Dot the continents, then drop numbered red pins for stories 1-13."""
    lon_span = (-168, 178)
    lat_span = (74, -56)
    step = 6
    px = x0
    while px < x1:
        py = y0
        while py < y1:
            lon = lon_span[0] + (px - x0) / (x1 - x0) * (lon_span[1] - lon_span[0])
            lat = lat_span[0] - (py - y0) / (y1 - y0) * (lat_span[0] - lat_span[1])
            if on_land(lon, lat):
                d.ellipse([px, py, px + 2, py + 2], fill=(150, 132, 100))
            py += step
        px += step
    for num, (lon, lat) in PINS.items():
        px = x0 + (lon - lon_span[0]) / (lon_span[1] - lon_span[0]) * (x1 - x0)
        py = y0 + (lat_span[0] - lat) / (lat_span[0] - lat_span[1]) * (y1 - y0)
        dx, dy = PIN_NUDGE.get(num, (0, 0))
        px, py = px + dx, py + dy
        r = 6
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=WHITE, width=1)
        label = str(num)
        fnt = F_SANS_B_XXS if num >= 10 else F_SANS_B_XS
        tw = d.textlength(label, font=fnt)
        d.text((px - tw / 2, py - 5), label, font=fnt, fill=WHITE)


# --- page ----------------------------------------------------------------------

def build(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    heroes = data["heroes"]
    mids = data["mids"]
    tail = data["tail"]

    # --- masthead ---
    tracked(d, MARGIN, 10, "THE WORLD IN ONE DAY", F_SANS_B_SM, INK, gap=3)
    d.text((MARGIN, 26), "Saturday 21 November 2026", font=F_TITLE,
           fill=INK)
    sub = ("COP31 runs into overtime with no deal · Three Houthi missiles "
           "shot down over Riyadh · Magnitude 6.7 quake shakes central Peru")
    d.text((MARGIN, 84), sub, font=font("DejaVuSerif.ttf", 13), fill=RED)
    d.line([MARGIN, 100, W - MARGIN, 100], fill=INK, width=2)

    # --- UTC strip ---
    utc = data["utc_strip"]
    slot_x0 = MARGIN + 92
    cell_w = (W - MARGIN - slot_x0) / len(utc)
    d.text((MARGIN, 106), "THE DAY IN UTC", font=F_SANS_B_XS, fill=RED)
    for i, slot in enumerate(utc):
        cx = slot_x0 + i * cell_w
        d.text((cx, 106), slot["time"], font=F_SANS_B_XS, fill=RED)
        d.text((cx, 118), slot["event"], font=F_SANS_XS, fill=INK_SOFT)
    d.line([MARGIN, 132, W - MARGIN, 132], fill=LINE, width=1)

    # --- stat strip: six numbers, six different stories ---
    stats = data["stats"]
    sw = CONTENT_W / len(stats)
    for i, s in enumerate(stats):
        x = MARGIN + i * sw
        if i:
            d.line([x, 136, x, 164], fill=LINE, width=1)
        d.text((x + 8, 134), s["number"], font=F_NUM_B, fill=RED)
        d.text((x + 8, 160), s["label"], font=F_SANS_XS, fill=INK_SOFT)
    d.line([MARGIN, 174, W - MARGIN, 174], fill=INK, width=1)

    # --- region bar (must sum to 35) ---
    regions = data["regions"]
    order = ["EUROPE", "ASIA", "MIDDLE EAST", "AFRICA", "AMERICAS",
             "OCEANIA", "GLOBAL"]
    bar = "  ·  ".join(f"{name} {regions[name]}" for name in order)
    tw = d.textlength(bar, font=F_SANS_B_SM)
    d.text(((W - tw) / 2, 180), bar, font=F_SANS_B_SM, fill=INK)

    # --- heroes ---
    hw = int((CONTENT_W - 2 * 12) / 3)
    for i, hero in enumerate(heroes):
        x = MARGIN + i * (hw + 12)
        d.rectangle([x, 196, x + hw, 212], fill=RED)
        d.text((x + 8, 199), hero["label"], font=F_SANS_B_XS, fill=WHITE)
        d.rectangle([x, 214, x + hw, 278], fill=NIGHT)
        SCENES[hero["scene"]](d, x, 214, hw, 64)
        badge(d, x + 4, 218, hero["n"])
        chip(d, x + hw - 4, 218, hero["chip"])
        y = 284
        d.text((x, y), hero["kicker"], font=F_SANS_B_XS, fill=RED)
        y = draw_wrapped(d, x, y + 13, hero["headline"], F_SERIF_B,
                         hw, INK, leading=22)
        y = draw_wrapped(d, x, y + 3, hero["standfirst"], F_SANS_SM,
                         hw, INK_SOFT, leading=14)
        d.text((x, y + 2), f"({hero['source']})",
               font=font("DejaVuSans.ttf", 9), fill=GREY)

    # --- mid grid header ---
    d.rectangle([MARGIN, 388, W - MARGIN, 404], fill=RED)
    d.text((MARGIN + 8, 391), "MORE FROM THE DAY", font=F_SANS_B_SM,
           fill=WHITE)

    # --- mid grid: 5 columns x 2 rows ---
    mw = int((CONTENT_W - 4 * 10) / 5)
    for row in range(2):
        for col in range(5):
            mid = mids[row * 5 + col]
            x = MARGIN + col * (mw + 10)
            sy = 410 + row * 146
            d.rectangle([x, sy, x + mw, sy + 50], fill=NIGHT)
            SCENES[mid["scene"]](d, x, sy, mw, 50)
            badge(d, x + 3, sy + 3, mid["n"], size=15)
            chip(d, x + mw - 3, sy + 3, mid["chip"])
            y = sy + 56
            d.text((x, y), mid["kicker"], font=F_SANS_B_XXS, fill=RED)
            y = draw_wrapped(d, x, y + 11, mid["headline"], F_SANS_B,
                             mw, INK, leading=16)
            y = draw_wrapped(d, x, y + 2, mid["standfirst"], F_SANS_XS,
                             mw, INK_SOFT, leading=12)
            d.text((x, y + 1), f"({mid['source']})",
                   font=font("DejaVuSans.ttf", 8), fill=GREY)

    # --- map + legend ---
    d.text((MARGIN, 706), "WHERE IT HAPPENED", font=F_SANS_B_SM, fill=RED)
    note = "Red numbers mark stories 1–13. Positions are approximate."
    d.text((W - MARGIN - d.textlength(note, font=F_SANS_XS), 706), note,
           font=F_SANS_XS, fill=GREY)
    draw_map(d, MARGIN, 722, MARGIN + 600, 800)
    legend = data["legend"]
    lx = MARGIN + 616
    for i, item in enumerate(legend):
        col = i // 7
        row = i % 7
        lx2 = lx + col * 172
        ly = 722 + row * 12
        d.text((lx2, ly), f"{i + 1}", font=F_SANS_B_XS, fill=RED)
        d.text((lx2 + 16, ly), item, font=F_SANS_XS, fill=INK)

    # --- tail: 22 briefs, 4 columns ---
    d.text((MARGIN, 810), "ALSO ON SATURDAY 21 NOVEMBER",
           font=F_SANS_B_SM, fill=RED)
    tw_col = int((CONTENT_W - 3 * 14) / 4)
    for i, item in enumerate(tail):
        col = i % 4
        row = i // 4
        x = MARGIN + col * (tw_col + 14)
        y = 828 + row * 13
        head = f"{item['n']} {item['place']} — "
        d.text((x, y), head, font=F_SANS_B_XXS, fill=INK)
        hw2 = d.textlength(head, font=F_SANS_B_XXS)
        d.text((x + hw2, y), item["brief"], font=F_SANS_XS, fill=INK_SOFT)

    # --- DATE CHECK: 11 numbered items, 3 columns ---
    dc = data["date_check"]
    d.rectangle([MARGIN, 906, W - MARGIN, 984], outline=RED, width=2)
    d.text((MARGIN + 8, 912), "LEFT OUT AS OLDER NEWS",
           font=F_SANS_B_SM, fill=RED)
    d.text((MARGIN + 8, 928),
           "Every story above happened or was first reported on Saturday "
           "21 November 2026.",
           font=F_SANS_XS, fill=INK_SOFT)
    dc_w = int((CONTENT_W - 16) / 3)
    for i, item in enumerate(dc):
        col = i // 4
        row = i % 4
        x = MARGIN + 8 + col * dc_w
        y = 944 + row * 10
        d.text((x, y), f"{i + 1}. {item}", font=F_SANS_XS, fill=INK)

    # --- footer ---
    d.text((MARGIN, 990), data["sources"], font=F_SANS_XS, fill=GREY)
    d.text((MARGIN, 1002),
           "CLAIM = one side's account, not independently confirmed.",
           font=F_SANS_XS, fill=GREY)
    return img


def save_small(img, path, colors=256):
    """Quantise to a flat palette so the file stays small without banding
    on the flat colour fields this page is built from."""
    pal = img.convert("P", palette=Image.ADAPTIVE, colors=colors)
    pal.save(path, optimize=True)
    return os.path.getsize(path)


def main():
    with open(DATA_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    img = build(data)
    img.save(OUT_PATH)
    size = save_small(img, OUT_PATH)
    digest = hashlib.sha256(open(OUT_PATH, "rb").read()).hexdigest()
    print(f"wrote {OUT_PATH}  {size} bytes  sha256 {digest}")
    if size > 120 * 1024:
        print("WARNING: over the 120 KB target", file=sys.stderr)


if __name__ == "__main__":
    main()
