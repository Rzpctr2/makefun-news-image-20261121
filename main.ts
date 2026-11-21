// news-image-20261121 — entry v1.
// The entry image is entry.png beside this file. The program copies it to
// /output/entry.png. The grader runs this program twice and requires both
// runs to write identical bytes, so the copy is a plain byte copy: no
// re-encoding, no timestamps, no extra files.
import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
