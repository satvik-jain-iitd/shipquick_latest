// Render design-canvas boards (*.dc.html) to PNG at the board's frame size (story #162).
// Usage: node render_boards.mjs <canvas_dir> <out_dir> <node_modules_dir> [board ...]
// No board names = every *.dc.html. Needs playwright in <node_modules_dir> (the project's own install).
// $QA_VIEWPORT (WxH, default 390x844) and $QA_THEME (default light): see board_html.mjs.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { prepare, boards, VIEWPORT } from './board_html.mjs';
const [, , dir, out, nm, ...names] = process.argv;
const { chromium } = createRequire(path.resolve(nm, 'x.js'))('playwright');
fs.mkdirSync(out, { recursive: true });
const tmp = fs.mkdtempSync(path.join(out, '.src-'));
const b = await chromium.launch();
const p = await b.newPage({ viewport: VIEWPORT, deviceScaleFactor: 2 });
for (const n of boards(dir, names)) {
  if (!fs.existsSync(path.join(dir, n + '.dc.html'))) { console.log('missing', n); continue; }
  const t = path.join(tmp, n + '.html');
  fs.writeFileSync(t, prepare(dir, n));
  await p.goto('file://' + t);
  await p.waitForTimeout(500);
  await p.screenshot({ path: path.join(out, n + '.png') });
  console.log('shot', n);
}
await b.close();
fs.rmSync(tmp, { recursive: true });
