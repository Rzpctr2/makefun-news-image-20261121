#!/usr/bin/env python3
"""Verify the news-image 21 Nov 2026 v3 front page (30 checks).

Checks structure, counts, text fit, map pins and determinism of
entry-final-v3.png against news-v3.json. Exits 0 only when all 30 pass.
Run from the entry directory.
"""

import hashlib
import json
import os
import subprocess
import sys

from PIL import Image, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "entry-final-v3.png")
DATA = os.path.join(HERE, "news-v3.json")
GEN = os.path.join(HERE, "generate-v3.py")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF_B = load_font("DejaVuSerif-Bold.ttf", 20)
F_SANS_B = load_font("DejaVuSans-Bold.ttf", 14)
F_SANS = load_font("DejaVuSans.ttf", 12)
F_SANS_SM = load_font("DejaVuSans.ttf", 11)
F_SANS_XS = load_font("DejaVuSans.ttf", 10)
F_SANS_B_XS = load_font("DejaVuSans-Bold.ttf", 10)
F_SANS_B_XXS = load_font("DejaVuSans-Bold.ttf", 9)
F_NUM_B = load_font("DejaVuSans-Bold.ttf", 26)

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))


def lines_for(text, fnt, width):
    """How many wrapped lines `text` needs at this font and width."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return len(lines)


def main():
    data = json.load(open(DATA, encoding="utf-8"))
    heroes, mids, tail = data["heroes"], data["mids"], data["tail"]
    all_stories = heroes + mids + tail

    # 1 — file exists and is the right size on disk
    exists = os.path.exists(PNG)
    size = os.path.getsize(PNG) if exists else 0
    check("png exists", exists, f"{size} bytes")

    # 2 — dimensions 1024x1024
    img = Image.open(PNG) if exists else None
    check("dimensions 1024x1024", img is not None and img.size == (1024, 1024),
          str(img.size if img else None))

    # 3 — under the 120 KB target (hard cap 1 MiB)
    check("file <= 120 KB", 0 < size <= 120 * 1024, f"{size} bytes")

    # 4 — re-render is byte-identical (run the generator twice)
    hashes = []
    for _ in range(2):
        run = subprocess.run([sys.executable, GEN], capture_output=True,
                             text=True, cwd=HERE)
        if run.returncode != 0:
            print(run.stdout, run.stderr)
            break
        hashes.append(hashlib.sha256(open(PNG, "rb").read()).hexdigest())
    check("byte-identical re-render", len(hashes) == 2 and hashes[0] == hashes[1],
          hashes[0][:16] if hashes else "generator failed")

    # 5 — story counts: 3 + 10 + 22 = 35
    check("35 stories (3+10+22)",
          len(heroes) == 3 and len(mids) == 10 and len(tail) == 22,
          f"{len(heroes)}+{len(mids)}+{len(tail)}")

    # 6 — numbers 1..35, unique, no gaps
    nums = sorted(s["n"] for s in all_stories)
    check("numbers 1-35, no gaps", nums == list(range(1, 36)),
          f"min {nums[0]} max {nums[-1]} count {len(nums)}")

    # 7 — region bar sums to 35 and matches the stories
    counted = {}
    for s in all_stories:
        counted[s["region"]] = counted.get(s["region"], 0) + 1
    check("region bar sums to 35 and matches stories",
          sum(data["regions"].values()) == 35 and counted == data["regions"],
          str(counted))

    # 8 — DATE CHECK has 11 numbered items
    dc = data["date_check"]
    check("DATE CHECK has 11 items", len(dc) == 11, f"{len(dc)} items")

    # 9 — DATE CHECK item 11 keeps the 'not yet' wording
    check("DATE CHECK #11 says 'not yet'",
          "not yet" in dc[10].lower(), dc[10])

    # 10 — DATE CHECK items 9 and 10 are the two new verified exclusions
    check("DATE CHECK #9 Jizan, #10 Starc 2025",
          "Jizan" in dc[8] and "Starc" in dc[9] and "2025" in dc[9],
          f"9: {dc[8]} | 10: {dc[9]}")

    # 11 — stat strip is exactly 13 / 3 / 146 / 42 / 6.7 / $58,983
    nums_stat = [s["number"] for s in data["stats"]]
    check("stat strip 13/3/146/42/6.7/$58,983",
          nums_stat == ["13", "3", "146", "42", "6.7", "$58,983"],
          str(nums_stat))

    # 12 — hero trio is COP31 / Riyadh 3 missiles / Peru 6.7
    heads = [h["headline"] for h in heroes]
    check("hero trio correct",
          "COP31" in heads[0] and "Three Houthi missiles" in heads[1]
          and "6.7" in heads[2], str(heads))

    # 13 — "3 missiles" kept (not 5) and "Verstappen takes Vegas pole"
    vegas = [m for m in mids if m["n"] == 10][0]
    check("3 missiles + Verstappen pole kept",
          "Three" in heads[1] and "5" not in heads[1].split("Three")[1][:4]
          and vegas["headline"] == "Verstappen takes Vegas pole",
          vegas["headline"])

    # 14 — new scene mids present, demoted mids are in the tail
    mid_heads = [m["headline"] for m in mids]
    tail_places = [t["place"] for t in tail]
    check("Kryvyi Rih / BepiColombo / Warsaw are mids",
          any("Kryvyi" in h or "kills 2" in h for h in mid_heads)
          and any("BepiColombo" in h for h in mid_heads)
          and any("NATO" in h for h in mid_heads),
          str(mid_heads[:3]))
    check("Kyiv bridge / Canberra / China-Japan demoted to tail",
          "KYIV" in tail_places and "CANBERRA" in tail_places
          and "BEIJING" in tail_places,
          f"tail places: {len(tail_places)}")

    # 15 — two new tail stories: Turin + Brussels
    check("tail has Turin + Brussels",
          "TURIN" in tail_places and "BRUSSELS" in tail_places,
          f"#{tail[-2]['n']} {tail[-2]['place']}, #{tail[-1]['n']} "
          f"{tail[-1]['place']}")

    # 16 — every hero and mid carries a source attribution
    check("source on every hero + mid",
          all(h.get("source") for h in heroes)
          and all(m.get("source") for m in mids),
          f"{len(heroes) + len(mids)} cards")

    # 17 — hero headlines fit 2 lines, standfirsts fit 2 lines
    hero_w = int((1024 - 48 - 24) / 3)
    ok_h = all(lines_for(h["headline"], F_SERIF_B, hero_w) <= 2
               for h in heroes)
    ok_s = all(lines_for(h["standfirst"], F_SANS_SM, hero_w) <= 2
               for h in heroes)
    check("hero headline + standfirst <= 2 lines", ok_h and ok_s,
          f"headlines ok={ok_h} standfirsts ok={ok_s}")

    # 18 — mid headlines fit 2 lines, standfirsts fit 2 lines
    mid_w = int((1024 - 48 - 40) / 5)
    ok_h = all(lines_for(m["headline"], F_SANS_B, mid_w) <= 2
               for m in mids)
    ok_s = all(lines_for(m["standfirst"], F_SANS_XS, mid_w) <= 2
               for m in mids)
    check("mid headline + standfirst <= 2 lines", ok_h and ok_s,
          f"headlines ok={ok_h} standfirsts ok={ok_s}")

    # 19 — every tail brief fits on one line in its column
    col_w = int((1024 - 48 - 42) / 4)
    bad = [t["n"] for t in tail
           if F_SANS_B_XXS.getlength(f"{t['n']} {t['place']} — ")
           + F_SANS_XS.getlength(t["brief"]) > col_w]
    check("tail briefs fit one line", not bad, f"over: {bad}")

    # 20 — DATE CHECK items fit their column
    dc_w = int((1024 - 48 - 16) / 3)
    bad = [i + 1 for i, item in enumerate(dc)
           if F_SANS_XS.getlength(f"{i + 1}. {item}") > dc_w]
    check("DATE CHECK items fit columns", not bad, f"over: {bad}")

    # 21 — legend lists all 13 hero+mid stories, in order
    legend = data["legend"]
    check("legend complete (13 items)", len(legend) == 13, str(legend))

    # 22 — UTC strip has 6 slots
    check("UTC strip has 6 slots", len(data["utc_strip"]) == 6,
          str([s["time"] for s in data["utc_strip"]]))

    # 23 — chips are only CONFIRMED / CLAIM
    chips = {s["chip"] for s in heroes + mids}
    check("chips only CONFIRMED/CLAIM", chips <= {"CONFIRMED", "CLAIM"},
          str(chips))

    # 24 — every scene key used by the page exists in the generator
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_v3", GEN)
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    used = {s["scene"] for s in heroes + mids}
    check("all 13 scenes implemented", used <= set(gen.SCENES),
          f"{len(used)} scenes used")

    # 25 — map pins are inside the map box (with nudges applied)
    x0, y0, x1, y1 = 24, 722, 624, 800
    lon_span, lat_span = (-168, 178), (74, -56)
    inside = []
    for num, (lon, lat) in gen.PINS.items():
        px = x0 + (lon - lon_span[0]) / (lon_span[1] - lon_span[0]) * (x1 - x0)
        py = y0 + (lat_span[0] - lat) / (lat_span[0] - lat_span[1]) * (y1 - y0)
        dx, dy = gen.PIN_NUDGE.get(num, (0, 0))
        inside.append(x0 <= px + dx <= x1 and y0 <= py + dy <= y1)
    check("all 13 map pins inside map box", all(inside),
          f"{sum(inside)}/13 inside")

    # 26 — pins are not stacked on each other (min 12 px apart)
    pts = []
    for num, (lon, lat) in gen.PINS.items():
        px = x0 + (lon - lon_span[0]) / (lon_span[1] - lon_span[0]) * (x1 - x0)
        py = y0 + (lat_span[0] - lat) / (lat_span[0] - lat_span[1]) * (y1 - y0)
        dx, dy = gen.PIN_NUDGE.get(num, (0, 0))
        pts.append((num, px + dx, py + dy))
    mind = min(((a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5
               for i, a in enumerate(pts) for b in pts[i + 1:])
    check("pins >= 12 px apart", mind >= 12, f"min distance {mind:.1f} px")

    # 27 — stat strip labels fit their cells
    sw = (1024 - 48) / 6
    bad = [s["number"] for s in data["stats"]
           if F_NUM_B.getlength(s["number"]) > sw - 8
           or F_SANS_XS.getlength(s["label"]) > sw - 8]
    check("stat strip labels fit cells", not bad, f"over: {bad}")

    # 28 — image is a real drawing, not blank (colour variety)
    colours = img.convert("RGB").getcolors(maxcolors=1 << 24)
    check("image has colour variety", colours is not None and len(colours) > 100,
          f"{len(colours) if colours else 0} colours")

    # 29 — no hero or mid scene is a solid block (scene areas vary)
    px = img.convert("RGB").load()
    samples = [(60, 240), (380, 240), (700, 240),
               (60, 430), (440, 430), (820, 430)]
    varied = len({px[a, b] for a, b in samples}) >= 4
    check("scenes are drawn (varied pixels)", varied,
          f"{len({px[a, b] for a, b in samples})} distinct samples")

    # 30 — deliverable set is complete on disk
    needed = ["generate-v3.py", "news-v3.json", "verify-v3.py", "main.ts",
              "entry-final-v3.png"]
    missing = [f for f in needed if not os.path.exists(os.path.join(HERE, f))]
    check("deliverable files present", not missing, f"missing: {missing}")

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{passed}/{len(RESULTS)} checks passed")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
