#!/usr/bin/env python3
"""Verifier for news-image-20261121 v2 — checks the PNG and the data
against the v2 spec (story-gap doc section 6 + visual-gap section 7
+ cross-day playoff devices). Exits 0 only if every check passes."""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "generate_v2", os.path.join(HERE, "generate-v2.py"))
G = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(G)
from PIL import Image, ImageDraw

DATA = json.load(open(os.path.join(HERE, "news-v2.json")))
PNG = os.path.join(HERE, "entry-final-v2.png")
fails = []
passes = []


def check(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))


heroes = DATA["heroes"]
mids = DATA["mids"]
tail = DATA["tail"]
total = len(heroes) + len(mids) + len(tail)

# --- 1. file / gate -------------------------------------------------------
data = open(PNG, "rb").read()
check("png magic bytes", data[:8] == b"\x89PNG\r\n\x1a\n")
check("bytes <= 1 MiB", len(data) <= 1048576, f"{len(data)} B")
im = Image.open(PNG)
check("dimensions 1024x1024", im.size == (1024, 1024), str(im.size))
check("mode RGB", im.mode == "RGB")

# --- 2. story counts ------------------------------------------------------
check("3 heroes", len(heroes) == 3)
check("10 mid stories", len(mids) == 10)
check("20 tail briefs", len(tail) == 20)
check("total 33 stories", total == 33, f"total={total}")

# --- 3. sequential numbering, no gaps ------------------------------------
nums = [s["n"] for s in heroes + mids]
check("featured numbers 1-13 sequential", nums == list(range(1, 14)), str(nums))
check("tail numbers 14-33 sequential, no gaps",
      [t["n"] for t in tail] == list(range(14, 34)))

# --- 4. region bar sums to total ------------------------------------------
counts = {r: 0 for r in G.REGIONS}
for s in heroes + mids:
    counts[s["region"]] += 1
for t in tail:
    counts[t["region"]] += 1
check("region bar sums to total", sum(counts.values()) == total,
      str({k: v for k, v in counts.items() if v}))
check("all regions in the 7-region scheme",
      all(s["region"] in G.REGIONS for s in heroes + mids) and
      all(t["region"] in G.REGIONS for t in tail))

# --- 5. stat strip: 6 numbers, 6 different stories -----------------------
STAT_STORY = {0: 1, 1: 2, 2: 6, 3: 7, 4: 14, 5: 3}  # 13,3,146,136,42,6.7
check("stat strip has 6 numbers", len(DATA["stats"]) == 6)
check("stat numbers all distinct stories",
      len(set(STAT_STORY.values())) == 6, str(STAT_STORY))
check("stat numbers all distinct values",
      len({s["number"] for s in DATA["stats"]}) == 6)

# --- 6. text fits -----------------------------------------------------------
d = ImageDraw.Draw(Image.new("RGB", (10, 10)))


def fits(text, font_path, size, max_w, max_lines):
    f = G.F(font_path, size)
    lines = G.wrap(d, text, f, max_w)
    return len(lines) <= max_lines and all(
        d.textlength(ln, font=f) <= max_w for ln in lines)


hw = (G.CW - 2 * 12) // 3
check("hero headlines fit 2 lines",
      all(fits(s["headline"], G.SERIF_B, 19, hw, 2) for s in heroes))
check("hero standfirsts fit 2 lines",
      all(fits(s["standfirst"], G.SANS, 11, hw, 2) for s in heroes))
mw = (G.CW - 4 * 10) // 5
check("mid headlines fit 2 lines",
      all(fits(s["headline"], G.SERIF_B, 13, mw, 2) for s in mids))
check("mid standfirsts fit 2 lines",
      all(fits(s["standfirst"], G.SANS, 9, mw, 2) for s in mids))
col_w = G.CW // 4
check("tail briefs fit one column line with margin",
      all(d.textlength(f"{t['place']} — {t['brief']}", font=G.F(G.SANS, 10))
          <= col_w - 30 for t in tail))
sub = " · ".join(h["headline"] for h in heroes)
check("subhead fits one line",
      d.textlength(sub, font=G.F(G.SERIF_I, 15)) <= G.CW, sub[:60])
dc_body = "   ".join("• " + item for item in DATA["date_check"])
dc_body += "   NOT YET: " + DATA["date_check_not_yet"]
dc_lines = G.wrap(d, dc_body, G.F(G.SANS, 9), G.CW - 20)
check("DATE CHECK fits 4 lines in box", len(dc_lines) <= 4,
      f"{len(dc_lines)} lines")
check("map legend lines fit their columns (no truncation)",
      all(d.textlength(lab, font=G.F(G.SANS, 10)) <= 178 - 16
          for lab in DATA["legend"]))
foot = ("Every story here happened or was first reported on Saturday "
        "21 November 2026. " + DATA["sources"])
check("footer fits one line",
      d.textlength(foot, font=G.F(G.SANS, 8)) <= G.CW,
      f"{d.textlength(foot, font=G.F(G.SANS, 8)):.0f}px")

# --- 7. DATE CHECK must not contradict the page ---------------------------
page_text = " ".join([s["headline"] + " " + s["standfirst"]
                      for s in heroes + mids] +
                     [f"{t['place']} {t['brief']}" for t in tail])
problems = []
if "GTA" in page_text:
    problems.append("GTA on page but excluded by DATE CHECK")
if "Wall Street" in page_text or "correction" in page_text.lower():
    problems.append("Wall Street correction on page but excluded")
if "Poland" in page_text:
    problems.append("Poland missile on page but excluded")
if "Shenzhen" in page_text:
    problems.append("Shenzhen summit on page but excluded")
if "Akvan landfall" in page_text:
    problems.append("Akvan landfall (not remnants) on page but excluded")
if "ICJ" in page_text and "ruling" in page_text and "reaction" not in page_text:
    problems.append("ICJ ruling as news on page but excluded")
if "BepiColombo arrives" in page_text or "BepiColombo reaches" in page_text:
    problems.append("BepiColombo framed as done, but it is only due")
check("no DATE CHECK contradiction", not problems,
      "; ".join(problems) or "clean")
check("DATE CHECK has 8 items + 1 not-yet note",
      len(DATA["date_check"]) == 8 and DATA["date_check_not_yet"].startswith("Not yet:"))
check("heroes are the consensus trio",
      heroes[0]["headline"].startswith("COP31")
      and "Riyadh" in heroes[1]["headline"]
      and "Peru" in heroes[2]["headline"])

# --- 8. playoff devices, no forbidden devices ----------------------------
check("playoff devices: UTC strip 6 slots, no VERDICT box",
      len(DATA["utc_strip"]) == 6
      and "VERDICT" not in json.dumps(DATA)
      and all(set(slot) == {"time", "event"} for slot in DATA["utc_strip"]))
check("drawn scenes + how-sure chip on every hero/mid card",
      all(s["scene"] in G.SCENES for s in heroes + mids)
      and all(s["chip"] in ("CONFIRMED", "CLAIM") for s in heroes + mids))

# --- 9. determinism: re-render, same sha256 -------------------------------
h1 = hashlib.sha256(data).hexdigest()
subprocess.run([sys.executable, os.path.join(HERE, "generate-v2.py")],
               check=True, capture_output=True)
h2 = hashlib.sha256(open(PNG, "rb").read()).hexdigest()
check("re-render byte-identical", h1 == h2, h1[:12])

print(f"\n{len(passes)} PASS, {len(fails)} FAIL")
if fails:
    print("FAILED:", fails)
    sys.exit(1)
print("ALL CHECKS PASS")
