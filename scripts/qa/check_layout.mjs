// Layout gate for flow_map pages. Fails (exit 1) when any two boxes overlap or sit closer than the minimum gap,
// when text does not fit its box, or when an arrow passes through a box that is not its start or end.
// Usage: node check_layout.mjs <page.html> <node_modules_dir> [min_gap_px=12]
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
const [, , page, nm, gapArg] = process.argv;
const GAP = Number(gapArg || 12);
const { chromium } = createRequire(path.resolve(nm, 'x.js'))('playwright');
const tmp = path.resolve(page).replace(/\.html$/, '.gate.html');
fs.writeFileSync(tmp, '<!doctype html><html><head><meta charset="utf-8"></head><body>' + fs.readFileSync(page, 'utf8') + '</body></html>');
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 900 } });
await p.goto('file://' + tmp); await p.waitForTimeout(800);
const r = await p.evaluate((GAP) => {
  document.getElementById('map').style.transform = 'none';
  const sel = '.bhead, .board img, .lab, .note, .ghost';
  const els = [...document.querySelectorAll('#map ' + sel)];
  const box = e => { const q = e.getBoundingClientRect(); return { x: q.x, y: q.y, w: q.width, h: q.height, n: e.className || e.tagName, t: (e.textContent || e.alt || '').trim().slice(0, 30) }; };
  const B = els.map(box); const bad = [];
  for (let i = 0; i < B.length; i++) for (let j = i + 1; j < B.length; j++) {
    const a = B[i], c = B[j];
    const sep = a.x + a.w + GAP <= c.x || c.x + c.w + GAP <= a.x || a.y + a.h + GAP <= c.y || c.y + c.h + GAP <= a.y;
    if (!sep) bad.push(`overlap or closer than ${GAP}px: [${a.n} ${a.t}] and [${c.n} ${c.t}]`);
  }
  els.forEach((e, i) => { if (e.tagName !== 'IMG' && (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1)) bad.push(`text does not fit: [${B[i].n} ${B[i].t}]`); });
  const inside = (pt, q, pad) => pt.x > q.x + pad && pt.x < q.x + q.w - pad && pt.y > q.y + pad && pt.y < q.y + q.h - pad;
  const svg = document.querySelector('#map svg'); const m = svg.getScreenCTM();
  [...svg.querySelectorAll('path[data-e]')].forEach(path => {
    const L = path.getTotalLength(); const pts = [];
    for (let s = 0; s <= L; s += 5) { const q = path.getPointAtLength(s); pts.push({ x: q.x * m.a + m.e, y: q.y * m.d + m.f }); }
    const ends = B.filter(q => inside(pts[0], q, -3) || inside(pts[pts.length - 1], q, -3));
    for (const q of B) { if (ends.includes(q)) continue; if (pts.some(pt => inside(pt, q, 1))) { bad.push(`arrow ${path.dataset.e} passes through [${q.n} ${q.t}]`); break; } }
  });
  return { boxes: B.length, arrows: svg.querySelectorAll('path[data-e]').length, bad };
}, GAP);
await b.close(); fs.rmSync(tmp);
console.log(`layout gate: ${r.boxes} boxes, ${r.arrows} arrows, ${r.bad.length} problems`);
r.bad.slice(0, 40).forEach(x => console.log('  ' + x));
process.exit(r.bad.length ? 1 : 0);
