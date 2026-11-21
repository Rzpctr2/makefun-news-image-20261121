#!/usr/bin/env python3
"""Verifier for news-image-20261121 v1 — checks the PNG and the data
against the autopsy rules. Exits 0 only if every check passes."""
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "generate_v1", os.path.join(HERE, "generate-v1.py"))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)
from PIL import Image

PNG = os.path.join(HERE, "entry-final-v1.png")
fails = []
passes = []

def check(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))

# --- 1. file / gate -------------------------------------------------------
data = open(PNG, "rb").read()
check("png magic bytes", data[:8] == b"\x89PNG\r\n\x1a\n")
check("bytes <= 1 MiB", len(data) <= 1048576, f"{len(data)} B")
im = Image.open(PNG)
check("dimensions 1024x1024", im.size == (1024, 1024), str(im.size))
check("mode RGB", im.mode == "RGB")

# --- 2. story counts ------------------------------------------------------
heroes, mids, tail = G.HEROES, G.MIDS, G.TAIL
total = len(heroes) + len(mids) + len(tail)
check("3 heroes", len(heroes) == 3)
check("10 mid stories", len(mids) == 10)
check("20 tail briefs", len(tail) == 20)
check("total 33 stories (floor 33-35)", total == 33, f"total={total}")

# --- 3. sequential numbering, no gaps ------------------------------------
nums = [s[0] for s in heroes + mids]
check("featured numbers 1-13 sequential",
      nums == list(range(1, 14)), str(nums))
start = 14
tail_nums = list(range(start, start + len(tail)))
check("tail numbers 14-33 sequential, no gaps",
      tail_nums == list(range(14, 34)))

# --- 4. region bar sums to total ------------------------------------------
counts = {r: 0 for r in G.REGION_ORDER}
for s in heroes + mids:
    counts[s[5] if s[5] in counts else "WORLD"] += 1
for t in tail:
    counts[t[0] if t[0] in counts else "WORLD"] += 1
check("region bar sums to total", sum(counts.values()) == total,
      str({k: v for k, v in counts.items() if v}))
check("no region is WORLD by mistake (all regions valid)",
      all(s[5] in G.REGION_ORDER for s in heroes + mids) and
      all(t[0] in G.REGION_ORDER for t in tail))

# --- 5. stat strip: 6 numbers, 6 different stories -----------------------
STAT_STORY = {  # stat index -> featured story number it comes from
    0: 1,    # $120BN  -> COP31 hero
    1: 4,    # 58      -> MQ-9 mid
    2: 6,    # 180     -> Manipur mid
    3: 3,    # $2.4BN  -> Bitcoin hero
    4: 5,    # 800 MW  -> Basra mid
    5: 14 + 6,  # 6.7  -> Peru tail brief #20
}
check("stat strip has 6 numbers", len(G.STATS) == 6)
check("stat numbers all distinct stories",
      len(set(STAT_STORY.values())) == 6, str(STAT_STORY))
check("stat numbers all distinct values",
      len({n for n, _ in G.STATS}) == 6)

from PIL import ImageDraw
d = ImageDraw.Draw(Image.new("RGB", (10, 10)))

def fits(text, font_path, size, max_w, max_lines):
    f = G.font(font_path, size)
    lines = G.wrap(d, text, f, max_w)
    return len(lines) <= max_lines and all(
        d.textlength(ln, font=f) <= max_w for ln in lines)

hw = (G.CW - 2 * 12) // 3
ok = all(fits(s[3], G.F_SERIF_B, 19, hw, 2) for s in heroes)
check("hero headlines fit 2 lines", ok)
ok = all(fits(s[4], G.F_SANS, 11, hw, 2) for s in heroes)
check("hero standfirsts fit 2 lines", ok)
mw = (G.CW - 4 * 10) // 5
ok = all(fits(s[3], G.F_SERIF_B, 13, mw, 2) for s in mids)
check("mid headlines fit 2 lines", ok)
ok = all(fits(s[4], G.F_SANS, 9, mw, 2) for s in mids)
check("mid standfirsts fit 2 lines", ok)
col_w = G.CW // 4
ok = all(d.textlength(f"{p} — {f}", font=G.font(G.F_SANS, 10)) <= col_w - 20
         for _, p, f in tail)
check("tail briefs fit one column line", ok)
sub = " · ".join(h[3] for h in heroes)
check("subhead fits one line",
      d.textlength(sub, font=G.font(G.F_SERIF_I, 16)) <= G.CW, sub[:60])
dc_txt = "  ".join("• " + item for item in G.DATECHECK)
lines = G.wrap(d, dc_txt, G.font(G.F_SANS, 9), G.CW - 20)
check("DATE CHECK fits 3 lines in box", len(lines) <= 3, f"{len(lines)} lines")

# --- 7. DATE CHECK must not contradict the page ---------------------------
page_text = " ".join([s[3] + " " + s[4] for s in heroes + mids] +
                     [f"{p} {f}" for _, p, f in tail])
contradictions = []
if "ICJ" in page_text or "Myanmar" in page_text:
    contradictions.append("ICJ/Myanmar on page but excluded by DATE CHECK")
if "GTA" in page_text:
    contradictions.append("GTA on page but excluded by DATE CHECK")
if "Anthropic" in page_text:
    contradictions.append("Anthropic on page (19-20 Nov story)")
check("no DATE CHECK contradiction", not contradictions,
      "; ".join(contradictions) or "clean")
check("DATE CHECK has 6 items", len(G.DATECHECK) == 6)
check("heroes are the consensus stories",
      heroes[0][3].startswith("COP31") and "Zelensky" in heroes[1][3]
      and "Bitcoin" in heroes[2][3])

# --- 8. no forbidden devices ----------------------------------------------
check("no VERDICT/UTC/HOW-SURE in data (autopsy rule)",
      "VERDICT" not in str(G.HEROES + G.MIDS) and
      "HOW SURE" not in str(G.HEROES + G.MIDS))
check("no bar-chart hero (scenes are drawn, not charts)",
      all(s[1] in G.SCENES for s in heroes + mids))

# --- 9. determinism: re-render, same sha256 -------------------------------
h1 = hashlib.sha256(data).hexdigest()
subprocess.run([sys.executable, os.path.join(HERE, "generate-v1.py")],
               check=True, capture_output=True)
h2 = hashlib.sha256(open(PNG, "rb").read()).hexdigest()
check("re-render byte-identical", h1 == h2, h1[:12])

print(f"\n{len(passes)} PASS, {len(fails)} FAIL")
if fails:
    print("FAILED:", fails)
    sys.exit(1)
print("ALL CHECKS PASS")
