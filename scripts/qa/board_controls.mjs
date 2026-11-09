// List every control on each board: text, tag, link target, box (in the board's frame), for flow_map.py (story #162).
// Usage: node board_controls.mjs <canvas_dir> <out.json> <node_modules_dir> [board ...]
// The board frame is the first element with data-theme. Links to "<name>.dc.html" become "to": "<name>".
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { prepare, boards, VIEWPORT } from './board_html.mjs';
const [, , dir, out, nm, ...names] = process.argv;
const { chromium } = createRequire(path.resolve(nm, 'x.js'))('playwright');
const tmp = fs.mkdtempSync(path.join(path.dirname(path.resolve(out)), '.ctl-'));
const b = await chromium.launch();
const p = await b.newPage({ viewport: VIEWPORT });
const res = {};
for (const n of boards(dir, names)) {
  const t = path.join(tmp, n + '.html'); fs.writeFileSync(t, prepare(dir, n));
  await p.goto('file://' + t); await p.waitForTimeout(300);
  res[n] = await p.evaluate(() => {
    const f = (document.querySelector('[data-theme]') || document.body).getBoundingClientRect();
    const sel = 'a, button, input, textarea, select, [role=button], [role=switch], [role=tab]';
    return [...document.querySelectorAll(sel)].map(e => {
      const r = e.getBoundingClientRect();
      if (r.width < 4 || r.height < 4 || r.y - f.y > f.height || r.y < f.y - 2) return null;
      const href = e.getAttribute('href') || '';
      const m = href.match(/([A-Za-z0-9-]+)\.dc\.html/);
      const text = (e.getAttribute('aria-label') || e.innerText || e.placeholder || e.value || '').trim().replace(/\s+/g, ' ').slice(0, 60);
      return { text, tag: e.tagName.toLowerCase(), to: m ? m[1] : null,
               box: [Math.round(r.x - f.x), Math.round(r.y - f.y), Math.round(r.width), Math.round(r.height)] };
    }).filter(Boolean);
  });
}
await b.close(); fs.rmSync(tmp, { recursive: true });
fs.writeFileSync(out, JSON.stringify(res, null, 1));
console.log(Object.keys(res).length, 'boards,', Object.values(res).flat().length, 'controls,', Object.values(res).flat().filter(c => c.to).length, 'linked');
