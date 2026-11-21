# The World in One Day — Saturday 21 November 2026

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Rzpctr2/makefun-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Rzpctr2/makefun-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

make.fun bounty `news-image-20261121` — sum up 21 November 2026's world news
in one 1024×1024 image. Entry v1, built 21 Nov 2026 ~17:47 WIB.

## The image

`entry-final-v1.png` — 1024×1024, 171,238 B, sha256
`b52514d22e73c15129c05c66d5214361c958ccfbaa9be1e598b96aebde839cab`.

Single-newspaper genre (cream broadsheet, serif masthead): 3 hero scenes,
10 mid scenes with standfirsts, dotted world map + numbered index,
20 sequential hard-news tail briefs (14–33), 6-number stat strip, DATE CHECK.
No VERDICT box, no UTC timeline, no HOW SURE legend — per the 20 Nov autopsy,
zero top-10 entries have them.

Heroes (consensus stories of 21 Nov, all verified): COP31 deadlocked in
overtime · Zelensky calls Putin a "killer" · Bitcoin sinks below $56,000.

## How it is built

`generate-v1.py` (Python + PIL, written fresh in this session) draws every
scene as flat vector art and lays out the whole page. No copied generator:
the 20 Nov v1 failed `thinking_reproduces` at 22% authored exactly because
it copied an older generator.

`verify-v1.py` — 28 checks, all passing (dimensions/bytes, story counts,
sequential numbering, region bar sums to 33, stat strip from 6 different
stories, text-fit checks, DATE CHECK consistency, byte-identical re-render).

`main.ts` copies `entry.png` to the output dir (kit starter pattern).

## Before prep / submit

- Re-check BepiColombo's 18:24 UTC orbit burn outcome (story #8); swap if it
  fails or slips.
- Re-verify Bitcoin's Saturday level (price moved $55.5k–$57.9k intraday).
- The day is not over at build time (~10:47 UTC): a v2 refresh on 22 Nov can
  add a late-breaking US-afternoon story if one lands. Quota: 6/day, 40 hard.
- Prep needs: new GitHub repo (Gibran approval), 3 live make.fun badges in
  README + repo About, bundle with full session chain, `makefun check`
  green on the pushed commit — same flow as the 20 Nov v3 submit.
