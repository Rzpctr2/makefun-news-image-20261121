// news-image-20261121 — entry v3 ("The World in One Day", 21 Nov 2026).
//
// The judged artifact is the finished newspaper image, entry.png, which
// sits beside this file. This script does one thing only: drop an exact
// byte-for-byte copy of that image at <output>/entry.png, where <output>
// is $MAKEFUN_OUTPUT_DIR when the grader sets it and /output otherwise.
//
// Nothing is decoded or re-encoded here, so running the script twice
// produces identical bytes both times. The drawing itself lives in
// generate-v3.py (Python + PIL, driven by news-v3.json) and is checked
// by verify-v3.py; this file is just the delivery step.
import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const folder = dirname(fileURLToPath(import.meta.url));
const entry = join(folder, 'entry.png');

if (!existsSync(entry)) {
  throw new Error(`entry.png not found next to main.ts (looked in ${folder})`);
}

const size = statSync(entry).size;
if (size > 1024 * 1024) {
  throw new Error(`entry.png is ${size} bytes, over the 1 MiB gate`);
}

const destination = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(destination, { recursive: true });
copyFileSync(entry, join(destination, 'entry.png'));
