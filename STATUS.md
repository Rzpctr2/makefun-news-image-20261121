# news-image-20261121 — STATUS (v1)

Competition: news-image-20261121, $100 total, closes 23 Nov 2026 07:00 WIB
(2026-11-23T00:00:00Z). Entry fee $0.
Kit: ~/workspace/makefun/kit-news-image-20261121/news-image-20261121-kit/
(fresh download 21 Nov 17:37 WIB, no level warning).

## Quota (checked 21 Nov 17:37 WIB, kit CLI)
- entries made 0 (kept 0), left today 6/6, hard limit 40/40, can_submit YES.

## v1 — BUILT 21 Nov ~17:47 WIB (this session, NOT submitted)
- PNG: entry-final-v1.png — 1024×1024, 171,238 B
- sha256: b52514d22e73c15129c05c66d5214361c958ccfbaa9be1e598b96aebde839cab
- Verifier: verify-v1.py — 28 PASS, 0 FAIL (incl. byte-identical re-render)
- main.ts: copies entry.png to output, verified byte-identical
- Generator: generate-v1.py (fresh, PIL) — 33 stories: 3 heroes + 10 mids
  + 20 tail briefs. Story record: news-v1.json.

## Heroes
1. COP31 deadlocked as fossil fuels vanish from draft (ANTALYA · CLIMATE)
2. Zelensky: Putin is a killer (UKRAINE · WAR)
3. Bitcoin sinks below $56,000 (MARKETS · CRYPTO)

## DATE CHECK (6 items)
Kyiv bridges barrage 19–20 Nov · ICJ Myanmar ruling 19 Nov · AI sell-off
S&P −3.7% Fri 20 Nov · Trump–Xi–Putin summit Thu 19 Nov · GTA VI $3.79bn
announced 20 Nov, launch 19 Nov · UK–EU deal signed Fri 20 Nov.

## Open decisions before prep/submit
- BepiColombo orbit burn 18:24 UTC 21 Nov — re-check outcome; swap #8 if fail/slip.
- Bitcoin Saturday level — re-verify (intraday range $55.5k–$57.9k).
- Possible v2 refresh 22 Nov for late US-afternoon 21 Nov news (quota allows).
- Prep: repo + README live badges + About + bundle + makefun check green.
  NOT done here — no repo created, no bundle, no submit (per task).

## v1 — SUBMITTED 21 Nov 18:07 WIB (intake, HTTP 202)
- Submission: 01a1fdca-79af-7354-bf05-a5e0e383e677, round 1
- Claim: AF-XZSS7-FCHDE-WRG26-X4EPG
- Commit submitted: 7c4f6362593ad3200e4870db724d794c314ea6b1 ("Add entry.png"; text at c160e8e7)
- Bundle: news-image-20261121-bundle-v2.tar.gz (sha 7ed05ce1…)
- Post-upload replica check GREEN (ok:true, failed:[], thinking_reproduces 83.3% authored 981/1177, unwritten 16.4%)
- Quota at submit: can_submit YES, day 6/6 left, hard 40/40
- Status right after submit: stage "submitted", outcome null — validity checks server still running (intake ≠ final, cf. Palma Verde round 1). Poll status; score appears on leaderboard once graded.
- Result due: 7 Dec 2026 15:00 WIB (2026-12-07T08:00:00Z). Entries close 23 Nov 07:00 WIB.

## v2 — RESUBMIT (prep 21 Nov ~20:07 WIB)
- PNG: entry-final-v2.png — 1024×1024 RGB, 176,659 B
- sha256: 478c89eac14cd7ebe2d25854ead2a133c3da0506792a6b23c24caf8b9763ca33
- Verifier: verify-v2.py — 30 PASS, 0 FAIL (28 checks + legend-fit + footer-fit, incl. byte-identical re-render)
- Generator: generate-v2.py (fresh, PIL) — 33 stories: 3 consensus heroes (COP31 overtime / Riyadh 3 missiles down / Peru quake 6.7) + 10 mids + 20 tail briefs. Story record: news-v2.json.
- CONTENT FIX (prep, deliberate deviation from story-gap §6): tail #31 swapped — OUT "Perth — Starc takes 7/58 as Ashes opens" (winner #4's DATE CHECK flags 7/58 as the 2025 Ashes, a year old — a stale story on a date-checked front page), IN "Virginia — First US measles death of 2026" (genuine 21 Nov story, winner #7 mid). Slot #31 kept, 33-story count kept, region bar still sums to 33 (OCEANIA 3→2, AMERICAS 4→5). Re-rendered + re-verified 30/30 after the swap.
- Kit: re-downloaded 21 Nov ~20:09 WIB — still level 33, site at level 34 (downloaded tarball unchanged; kit-level warning persists, flagged to parent). Quota at prep: can_submit YES, 1 made / 1 kept, 5/6 day left, 39/40 hard.
- Repo: README 3 live badges verified (competition + rank + reward, owner/repo filled) + bounty link. About topic `makefun` confirmed via connector search; website field NOT visible in repo-page extract or search record (API record fetch denied 403) — UNVERIFIED, parent to confirm/fix via browser.
- main.ts rewritten fresh in prep session (copies entry.png to output, byte-identical, tested twice); NOT byte-identical to kit starter.
- Text push (Step 3): commit TBD — see below.
- Bundle: TBD — see below.
- Check: TBD — see below (commit = text-push sha; repo entry.png is still v1's until parent uploads v2 PNG via browser — check validates text tree + bundle only; parent re-runs check on post-upload tree before submit, as in v1).
- NOT submitted by prep agent. Gibran's words for the resubmit: "coba biar top 50 seenggaknya, kita belajar dulu" + "ok gaskan".
