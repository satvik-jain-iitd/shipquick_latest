#!/usr/bin/env python3
"""Build the design audit report. Usage: audit_report.py <qa_home> [run] [title]
Reads design-audit.jsonl (one run), journey.json (row order), boards/<screen>.png (any width; boxes are in 390 px space).
Writes <qa_home>/report/index.html and report/img/*.jpg with numbered highlight boxes."""
import json, sys, os, html, collections
from PIL import Image, ImageDraw, ImageFont

SEV = {'Blocker': 0, 'Major': 1, 'Nit': 2}
COL = {'Blocker': (179, 38, 30), 'Major': (196, 120, 0), 'Nit': (60, 110, 150), 'good': (46, 125, 50)}
IMP = {'high': 0, 'medium': 1, 'low': 2}
e = html.escape

def bucket(f):
    if f.get('bucket') in ('now', 'next', 'later'): return f['bucket']
    if f['impact'] == 'high': return 'now' if f['effort'] == 'S' else 'next'
    if f['impact'] == 'medium' and f['effort'] == 'S': return 'next'
    return 'later'

def annotate(src, dst, items, width=600):
    im = Image.open(src).convert('RGB')
    k = im.width / 390
    d = ImageDraw.Draw(im)
    try: font = ImageFont.load_default(size=int(15 * k))   # Pillow 10.1+; no font file on any one OS
    except TypeError: font = ImageFont.load_default()
    for label, f in items:
        b = f.get('box')
        if not b or len(b) != 4: continue
        x, y, w, h = [v * k for v in b]
        c = COL['good'] if f['kind'] == 'good' else COL[f['severity']]
        d.rectangle([x, y, x + w, y + h], outline=c, width=max(2, int(2.5 * k)))
        tw = d.textlength(label, font=font)
        tx, ty = max(0, x - 2), max(0, y - 20 * k)
        d.rectangle([tx, ty, tx + tw + 10 * k, ty + 19 * k], fill=c)
        d.text((tx + 5 * k, ty + 1 * k), label, fill='white', font=font)
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    im.save(dst, quality=78, optimize=True)

def build(home, run=None, title='Design Audit'):
    rows = [json.loads(l) for l in open(os.path.join(home, 'design-audit.jsonl')) if l.strip()]
    run = run or max(r['run'] for r in rows)
    fs = [r for r in rows if r['run'] == run]
    for f in fs: f['bucket'] = bucket(f)
    journey = json.load(open(os.path.join(home, 'journey.json')))
    out = os.path.join(home, 'report'); os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    by = collections.defaultdict(list)
    for f in fs: by[f['screen']].append(f)
    labels = {}
    for s, items in by.items():
        iss = sorted([f for f in items if f['kind'] == 'issue'], key=lambda f: (SEV[f['severity']], IMP[f['impact']]))
        good = [f for f in items if f['kind'] == 'good']
        lab = [(str(i + 1), f) for i, f in enumerate(iss)] + [('G' + str(i + 1), f) for i, f in enumerate(good)]
        labels[s] = lab
        for l, f in lab: f['label'] = l
        src = os.path.join(home, 'boards', s + '.png')
        if os.path.exists(src): annotate(src, os.path.join(out, 'img', s + '.jpg'), lab)
    issues = [f for f in fs if f['kind'] == 'issue']
    sev = collections.Counter(f['severity'] for f in issues)
    screens = len(by)
    def roadmap(b):
        xs = sorted([f for f in issues if f['bucket'] == b], key=lambda f: (SEV[f['severity']], IMP[f['impact']]))
        lis = ''.join(f'<li><a href="#s-{e(f["screen"])}"><span class="chip {f["severity"].lower()}">{e(f["severity"])}</span> '
                      f'<b>{e(f["screen"])} #{e(f["label"])}</b></a> {e(f["fix"] or f["see"])} <span class="lens">{e(f["lens"])}</span></li>' for f in xs[:40])
        more = f'<p class="more">and {len(xs) - 40} more in the screens below</p>' if len(xs) > 40 else ''
        return f'<section class="lane"><h3>{b.title()} <span>{len(xs)}</span></h3><ol>{lis}</ol>{more}</section>'
    def card(s):
        lab = labels.get(s, [])
        img = f'<img src="img/{e(s)}.jpg" alt="{e(s)} with numbered highlights" loading="lazy">' if os.path.exists(os.path.join(out, 'img', s + '.jpg')) else '<div class="noimg">No image</div>'
        lis = ''
        for l, f in lab:
            cls = 'good' if f['kind'] == 'good' else f['severity'].lower()
            who = f.get('persona') or f.get('pass', '')
            feel = f' Feels: <i>{e(f["feel"])}</i>.' if f.get('feel') else ''
            fix = f'<div class="fix">Improve: {e(f["fix"])}</div>' if f.get('fix') else ''
            lis += (f'<li class="f {cls}" data-sev="{cls}" data-lens="{e(f["lens"][:1])}"><span class="n">{e(l)}</span><div>'
                    f'<div class="meta">{e(f["lens"])} · {e(who)} · {e(f.get("impact",""))} impact · effort {e(f.get("effort",""))} · {e(f["bucket"])}</div>'
                    f'<div>{e(f["see"])}{feel}</div><div class="why">{e(f["why"])} <span class="ref">{e(f.get("ref",""))}</span></div>{fix}</div></li>')
        return f'<article class="screen" id="s-{e(s)}"><h4>{e(s)}</h4><div class="pair">{img}<ol class="fl">{lis or "<li>No findings.</li>"}</ol></div></article>'
    secs = ''
    for r in journey:
        cards = ''.join(card(s) for s in r['screens'] if s in by)
        jn = [f for f in fs if f['screen'] == '_row:' + r['row'][:40]]
        if cards: secs += f'<section class="row"><h2>{e(r["row"])}</h2><div class="cards">{cards}</div></section>'
    journey_notes = [f for f in fs if f['screen'].startswith('_journey')]
    jl = ''.join(f'<li class="f {"good" if f["kind"]=="good" else f["severity"].lower()}"><span class="n">{e(f["lens"])}</span><div><div>{e(f["see"])}</div><div class="why">{e(f["why"])}</div>'
                 + (f'<div class="fix">Improve: {e(f["fix"])}</div>' if f.get("fix") else '') + '</div></li>' for f in journey_notes)
    goods = [f for f in fs if f['kind'] == 'good']
    page = TEMPLATE.format(title=e(title), run=run, date=e(fs[0].get('date', '')), screens=screens, n=len(issues),
        blocker=sev['Blocker'], major=sev['Major'], nit=sev['Nit'], good=len(goods),
        lanes=roadmap('now') + roadmap('next') + roadmap('later'), journey=jl or '<li>No journey notes yet.</li>', rows=secs)
    open(os.path.join(out, 'index.html'), 'w').write(page)
    print(os.path.join(out, 'index.html'), screens, 'screens', len(issues), 'issues', len(goods), 'good')

TEMPLATE = '''<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Layout: a field report: summary, roadmap lanes, then the journey row by row. Neutral colours; a project restyles its own copy. */
:root {{ --paper:#F6F6F3; --card:#FFFFFF; --ink:#1F2421; --muted:#5A5F5B; --line:#D6D6D0; --sage:#CFCFCA;
  --blocker:#B3261E; --major:#9A5B00; --nit:#3C6E96; --good:#2E7D32;
  --display:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif; --body:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif; --mono:ui-monospace,Menlo,Consolas,monospace; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --paper:#161817; --card:#202321; --ink:#E8EAE8; --muted:#A6ABA7; --line:#383C39; --sage:#42474A;
  --blocker:#F2867E; --major:#E8B04F; --nit:#8FB8DA; --good:#7CC47F; color-scheme:dark }} }}
:root[data-theme="dark"] {{ --paper:#161817; --card:#202321; --ink:#E8EAE8; --muted:#A6ABA7; --line:#383C39; --sage:#42474A;
  --blocker:#F2867E; --major:#E8B04F; --nit:#8FB8DA; --good:#7CC47F; color-scheme:dark }}
body {{ background:var(--paper); color:var(--ink); font:16px/1.5 var(--body); padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); padding-block:24px 64px; }}
main {{ max-width:1180px; margin:0 auto; display:flex; flex-direction:column; gap:40px; }}
h1,h2,h3,h4 {{ font-family:var(--display); text-wrap:balance; margin:0; }}
h1 {{ font-size:clamp(32px,5vw,52px); font-weight:800; letter-spacing:-0.02em; }}
h2 {{ font-size:24px; font-weight:800; }} h3 {{ font-size:18px; }} h4 {{ font-size:17px; font-family:var(--mono); font-weight:500; }}
.eyebrow {{ font-family:var(--mono); font-size:12px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }}
.lede {{ max-width:68ch; color:var(--muted); margin:8px 0 0; }}
.stats {{ display:flex; flex-wrap:wrap; gap:8px 24px; font-family:var(--mono); font-size:14px; margin-top:16px; }}
.stats b {{ font-size:22px; font-family:var(--display); font-variant-numeric:tabular-nums; }}
.method {{ border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:16px 0; display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; }}
.method p {{ margin:4px 0 0; color:var(--muted); font-size:15px; }}
.lanes {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px; }}
.lane {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; min-width:0; }}
.lane h3 span {{ font-family:var(--mono); font-size:13px; color:var(--muted); }}
.lane ol {{ padding-left:20px; margin:12px 0 0; display:flex; flex-direction:column; gap:8px; font-size:15px; }}
.lane a {{ color:inherit; text-decoration:none; }} .lane a:hover b {{ text-decoration:underline; }}
.more {{ font-size:13px; color:var(--muted); }}
.chip {{ font-family:var(--mono); font-size:11px; padding:1px 6px; border-radius:4px; color:var(--card); vertical-align:1px; }}
.chip.blocker {{ background:var(--blocker); }} .chip.major {{ background:var(--major); }} .chip.nit {{ background:var(--nit); }}
.lens {{ font-family:var(--mono); font-size:12px; color:var(--muted); }}
.filters {{ position:sticky; top:env(safe-area-inset-top,0px); z-index:5; background:var(--paper); padding:10px 0; display:flex; flex-wrap:wrap; gap:8px; border-bottom:1px solid var(--line); }}
.filters button {{ font:500 13px var(--mono); border:1px solid var(--line); background:var(--card); color:var(--ink); border-radius:999px; padding:6px 12px; cursor:pointer; }}
.filters button[aria-pressed="true"] {{ background:var(--ink); color:var(--paper); }}
.filters button:focus-visible {{ outline:2px solid var(--nit); outline-offset:2px; }}
.row {{ display:flex; flex-direction:column; gap:16px; }}
.cards {{ display:flex; flex-direction:column; gap:16px; }}
.screen {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px; display:flex; flex-direction:column; gap:12px; }}
.pair {{ display:grid; grid-template-columns:minmax(0,300px) minmax(0,1fr); gap:20px; align-items:start; }}
.pair img {{ width:100%; border-radius:8px; border:1px solid var(--line); }}
.noimg {{ aspect-ratio:390/844; border:1px dashed var(--line); border-radius:8px; display:grid; place-items:center; color:var(--muted); }}
@media (max-width:720px) {{ .pair {{ grid-template-columns:1fr; }} .pair img {{ max-width:320px; }} }}
.fl {{ list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:12px; min-width:0; }}
.f {{ display:grid; grid-template-columns:34px minmax(0,1fr); gap:10px; font-size:15px; }}
.f .n {{ font:600 12px var(--mono); color:var(--card); border-radius:5px; height:22px; display:grid; place-items:center; }}
.f.blocker .n {{ background:var(--blocker); }} .f.major .n {{ background:var(--major); }} .f.nit .n {{ background:var(--nit); }} .f.good .n {{ background:var(--good); }}
.meta {{ font-family:var(--mono); font-size:12px; color:var(--muted); }}
.why {{ color:var(--muted); font-size:14px; }} .ref {{ font-family:var(--mono); font-size:12px; }}
.fix {{ font-weight:500; margin-top:2px; }}
.journey ol {{ list-style:none; padding:0; display:flex; flex-direction:column; gap:12px; }}
.journey .n {{ width:auto; padding:0 6px; }} .journey .f {{ grid-template-columns:auto minmax(0,1fr); }}
@media (prefers-reduced-motion: no-preference) {{ html {{ scroll-behavior:smooth; }} }}
</style>
<main>
<header>
  <div class="eyebrow">Design audit · run {run} · {date}</div>
  <h1>{title}</h1>
  <p class="lede">Every screen on the design canvas, read three ways: a goldfish who opens it cold, a critic with the design standard, and an elephant who holds the whole journey. This is the roadmap for what to improve next. It is not the bug list: bugs go to GitHub stories.</p>
  <div class="stats"><span><b>{screens}</b> screens</span><span><b>{n}</b> issues</span><span><b>{blocker}</b> blocker</span><span><b>{major}</b> major</span><span><b>{nit}</b> nit</span><span><b>{good}</b> things that work</span></div>
</header>
<section class="method">
  <div><h3>Goldfish</h3><p>A fresh reviewer with no history sees one screen image and says what it is, what to tap and how it feels.</p></div>
  <div><h3>Critic</h3><p>The same reviewer then applies the standard: Nielsen's heuristics, Rams, Gestalt, WCAG, platform rules, plain words.</p></div>
  <div><h3>Elephant</h3><p>Holds every screen in journey order and judges fit: steps, consistency, promises kept, the peak and the end.</p></div>
  <div><h3>Read a box</h3><p>Numbers on a screen match the list beside it. Red is blocker, amber major, blue nit, green works well.</p></div>
</section>
<section><h2>Roadmap</h2><p class="lede">Now: high impact, small effort. Next: high impact, bigger effort. Later: the rest.</p><div class="lanes">{lanes}</div></section>
<section class="journey"><h2>Journey notes (elephant)</h2><ol>{journey}</ol></section>
<nav class="filters" aria-label="Filter findings">
  <button type="button" data-f="all" aria-pressed="true">All</button><button type="button" data-f="blocker" aria-pressed="false">Blocker</button>
  <button type="button" data-f="major" aria-pressed="false">Major</button><button type="button" data-f="nit" aria-pressed="false">Nit</button><button type="button" data-f="good" aria-pressed="false">Works well</button>
</nav>
{rows}
</main>
<script>
document.querySelectorAll('.filters button').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('.filters button').forEach(x => x.setAttribute('aria-pressed', x === b));
  const f = b.dataset.f;
  document.querySelectorAll('.fl .f').forEach(li => {{ li.hidden = !(f === 'all' || li.dataset.sev === f); }});
}}));
</script>
'''

if __name__ == '__main__':
    a = sys.argv[1:]
    build(a[0], int(a[1]) if len(a) > 1 and a[1] else None, a[2] if len(a) > 2 else 'Design Audit')
