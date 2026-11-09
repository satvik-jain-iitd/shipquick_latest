#!/usr/bin/env python3
"""Flow map + clickable prototype from one interaction manifest.
Usage: flow_map.py <qa_home> <flows.json> <out_dir> [audit_run]
flows.json: {"name", "start", "boards": [...], "edges": [{"from", "control", "to", "status": "ok|wrong|untested",
  "note", "evidence", "issue", "back": false}], "auto_links": true}
Controls come from <qa_home>/controls.json (board_controls.mjs). With auto_links, every board link between two listed
boards is added as an untested edge unless an edge for that control already exists.
Images: <qa_home>/boards-1x/<board>.png (390 x 844). Issue boxes: <qa_home>/design-audit.jsonl (Blocker and Major)."""
import json, sys, os, html, collections
from PIL import Image
e = html.escape
# ponytail: boards are assumed to be 390 x 844 phone frames (board_controls.mjs default); make the frame a
# flows.json field when a project's boards are another size.
S = 0.5                      # board scale on the map
BW, BH = int(390 * S), int(844 * S)
GAPX, GAPY, TOP = 300, 150, 60

def js(o):
    """JSON for inside <script>: an escaped '</' can never close the block."""
    return json.dumps(o).replace('</', '<\\/')


def main(home, flows_path, out, audit_run=None):
    F = json.load(open(flows_path)); C = json.load(open(os.path.join(home, 'controls.json')))
    boards = F['boards']; bs = set(boards)
    edges = []
    for x in F['edges']:
        if x['from'] not in bs: continue   # the screen is not added yet; its edges wait for it
        ctl = next((c for c in C.get(x['from'], []) if c['text'].lower().startswith(x['control'].lower())), None)
        if not ctl: sys.exit(f"no control '{x['control']}' on {x['from']}")
        edges.append({**x, 'box': ctl['box']})
    if F.get('auto_links', True):
        have = {(x['from'], x['control'].lower()) for x in F['edges']}
        for b in boards:
            for c in C.get(b, []):
                if c['to'] in bs and not any(c['text'].lower().startswith(k) for (f, k) in have if f == b):
                    edges.append({'from': b, 'control': c['text'], 'to': c['to'], 'status': 'untested', 'box': c['box'], 'evidence': 'drawn on the board'})
    if F.get('auto_links', True):   # links to boards not added yet become ghost targets ("next, not reviewed yet")
        for b in boards:
            for c in C.get(b, []):
                if c['to'] and c['to'] not in bs and not any(x['from'] == b and x['control'] == c['text'] for x in edges):
                    edges.append({'from': b, 'control': c['text'], 'to': c['to'], 'status': 'untested', 'box': c['box'], 'evidence': 'drawn on the board'})
    ghosts = [x for x in edges if x.get('to') and x['to'] not in bs]
    for x in ghosts: x['ghost'] = x.pop('to')
    # ---- layout: nothing may overlap (check_layout.mjs is the gate). Infinite canvas, generous space. ----
    # Each board owns a block: a header, the board image, and to its right an annotation lane where its labels,
    # sticky notes and "next" cards stack top to bottom with a fixed gap. Arrows run only in the corridors between
    # blocks, in the band above every row (long forward links) or the band below everything (links back).
    LANE, GAP, HEAD, ROWGAP, LANEPAD = 300, 20, 44, 140, 36
    adj = collections.defaultdict(list)
    for x in edges:
        if x.get('to'): adj[x['from']].append(x['to'])
    layer = {F['start']: 0} if F['start'] in bs else {}
    q = list(layer)
    while q:
        n = q.pop(0)
        for t2 in adj[n]:
            if t2 not in layer: layer[t2] = layer[n] + 1; q.append(t2)
    nxt = (max(layer.values()) + 1) if layer else 0
    for b in boards:
        if b not in layer: layer[b] = nxt
    # group edges by control: one label per control, notes and next-cards under it
    groups = collections.OrderedDict()
    for x in sorted(edges, key=lambda x: (boards.index(x['from']), x['box'][1], x['box'][0])):
        groups.setdefault((x['from'], tuple(x['box'])), []).append(x)
    def lines(s, w): return max(1, -(-len(s) // w))
    lane_items = collections.defaultdict(list)   # board -> [(kind, group, edge, h)]
    for (b, box), xs in groups.items():
        lab = ', '.join(str(i) for i in [0]) # placeholder, numbers set below
        lane_items[b].append(['label', xs, None, 0])
        for x in xs:
            if x.get('note'): lane_items[b].append(['note', xs, x, 0])
            if x.get('ghost'): lane_items[b].append(['ghost', xs, x, 0])
    n = 0
    for (b, box), xs in groups.items():
        for x in xs: n += 1; x['n'] = n
    def item_h(kind, xs, x):
        if kind == 'label': return 22 + 18 * lines(', '.join(str(y['n']) for y in xs) + ' ' + xs[0]['control'], 30)
        if kind == 'note': return 20 + 18 * lines(x['note'] + (f" #{x['issue']}" if x.get('issue') else ''), 30)
        return 20 + 18 * 2
    # stack lane items (relative to the board top), each at the control's height or below the previous one
    rel = {}
    for b in boards:
        y = HEAD
        for it in lane_items[b]:
            kind, xs, x, _ = it
            want = HEAD + xs[0]['box'][1] * S + xs[0]['box'][3] * S / 2 - 14 if kind == 'label' else y
            it[3] = item_h(kind, xs, x)
            top = max(want, y); it.append(top); y = top + it[3] + GAP
        rel[b] = max(HEAD + BH, y)
    # long forward links and back links need tracks in the bands; count them first
    def fwd_long(x): return x.get('to') and layer[x['to']] > layer[x['from']] + 1
    def back(x): return x.get('to') and layer[x['to']] <= layer[x['from']]
    n_long = sum(1 for x in edges if fwd_long(x)); n_back = sum(1 for x in edges if back(x))
    TOPBAND = 100 + 26 * n_long
    # corridor width per column: one vertical track per arrow that turns in it
    turns = collections.Counter()
    for x in edges:
        if x.get('to'):
            turns[layer[x['from']]] += 1
            turns[layer[x['to']] - 1] += 1
    cols = collections.defaultdict(list)
    for b in boards: cols[layer[b]].append(b)
    colx, xcur = {}, 60
    for L in range(max(cols) + 1 if cols else 0):
        colx[L] = xcur
        xcur += BW + LANEPAD + LANE + max(240, 80 + 16 * turns[L])
    pos = {}
    for L in sorted(cols):
        def bary(b):
            ps = [pos[x['from']][1] for x in edges if x.get('to') == b and x['from'] in pos]
            return (sum(ps) / len(ps)) if ps else 1e9
        y = TOPBAND
        for b in sorted(cols[L], key=lambda b: (bary(b), boards.index(b))):
            pos[b] = (colx[L], y); y += rel[b] + ROWGAP
    W = xcur + 60
    maxy = max(pos[b][1] + rel[b] for b in boards) if boards else TOPBAND
    BOTBAND = maxy + 80
    H = BOTBAND + 26 * n_back + 120
    os.makedirs(os.path.join(out, 'img'), exist_ok=True)
    for b in boards:
        Image.open(os.path.join(home, 'boards-1x', b + '.png')).convert('RGB').save(os.path.join(out, 'img', b + '.jpg'), quality=82)
    progress = json.load(open(os.path.join(home, 'progress.json'))) if os.path.exists(os.path.join(home, 'progress.json')) else {}
    prog = progress.get('screens', {})
    issues = collections.defaultdict(list); finds = collections.defaultdict(list)
    ap = os.path.join(home, 'design-audit.jsonl')
    if os.path.exists(ap):
        rows = [json.loads(l) for l in open(ap) if l.strip()]
        run = audit_run or (max(r['run'] for r in rows) if rows else None)
        for r in rows:
            if r['run'] == run and r['screen'] in bs: finds[r['screen']].append(r)
        for b in finds:   # a one-screen review replaces batch notes for the same screen
            if any(r.get('mode') == 'one-screen' for r in finds[b]): finds[b] = [r for r in finds[b] if r.get('mode') == 'one-screen']
            sev = {'Blocker': 0, 'Major': 1, 'Nit': 2}
            finds[b].sort(key=lambda r: (r['kind'] != 'issue', sev.get(r['severity'], 3)))
            issues[b] = [r for r in finds[b] if r['kind'] == 'issue' and r['severity'] in ('Blocker', 'Major') and r.get('box')]
    COL = {'ok': '#2E6B3F', 'wrong': '#B3261E', 'untested': '#706F70'}
    rank = {'wrong': 0, 'untested': 1, 'ok': 2}
    svg, labels, notes = [], [], []
    def rpath(pts):   # orthogonal path with small rounded corners
        d = f"M{pts[0][0]:.0f},{pts[0][1]:.0f}"
        for (x1, y1) in pts[1:]: d += f" L{x1:.0f},{y1:.0f}"
        return d
    # entry points: spread incoming arrows down the left edge of each target, sorted by where they come from
    incoming = collections.defaultdict(list)
    for x in edges:
        if x.get('to'): incoming[x['to']].append(x)
    entry = {}
    for tb, xs in incoming.items():
        tx, ty = pos[tb]
        xs.sort(key=lambda x: (pos[x['from']][1], x['n']))
        for i, x in enumerate(xs): entry[x['n']] = (tx, ty + HEAD + 30 + (BH - 60) * (i + 1) / (len(xs) + 1))
    ctrack = collections.Counter(); ltrack = 0; btrack = 0
    for (b, box), xs in groups.items():
        fx, fy = pos[b]
        laneX = fx + BW + LANEPAD
        its = [it for it in lane_items[b] if it[1] is xs]
        lab = its[0]; ly = fy + lab[4]; lh = lab[3]
        worst = min(xs, key=lambda x: rank[x['status']])['status']
        # leader from the control on the board to its label
        cx, cy = fx + (box[0] + box[2]) * S, fy + HEAD + (box[1] + box[3] / 2) * S
        svg.append(f'<path d="{rpath([(cx, cy), (fx + BW + 14, cy), (fx + BW + 14, ly + lh / 2), (laneX - 4, ly + lh / 2)])}" fill="none" stroke="{COL[worst]}" stroke-width="2"/>')
        nums = ', '.join(str(x['n']) for x in xs)
        labels.append(f'<div class="lab {worst}" style="left:{laneX:.0f}px;top:{ly:.0f}px;width:{LANE - 40}px;height:{lh}px" title="{e(" / ".join(x.get("evidence", "") for x in xs))}"><b>{nums}</b> {e(xs[0]["control"])}</div>')
        for it in its[1:]:
            kind, _, x, h, top = it
            ny = fy + top
            if kind == 'note':
                iss = f' <b>#{e(str(x["issue"]))}</b>' if x.get('issue') else ''
                notes.append(f'<div class="note" style="left:{laneX:.0f}px;top:{ny:.0f}px;width:{LANE - 40}px;height:{h}px"><b>{x["n"]}</b> {e(x["note"])}{iss}</div>')
                svg.append(f'<path d="{rpath([(laneX + 12, ly + lh), (laneX + 12, ny - 2)])}" fill="none" stroke="#B3261E" stroke-width="2.5" marker-end="url(#a-wrong)"/>')
            else:
                notes.append(f'<div class="ghost" style="left:{laneX:.0f}px;top:{ny:.0f}px;width:{LANE - 40}px;height:{h}px"><b>{x["n"]}</b> Next: <b>{e(x["ghost"])}</b>, not reviewed yet</div>')
                svg.append(f'<path d="{rpath([(laneX + 12, ly + lh), (laneX + 12, ny - 2)])}" fill="none" stroke="#706F70" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#a-untested)"/>')
        # arrows to target boards, from the right edge of the label
        sx, sy = laneX + LANE - 40, ly + lh / 2
        for x in xs:
            if not x.get('to'): continue
            c = COL[x['status']]; dash = ' stroke-dasharray="7 6"' if x['status'] == 'untested' else ''
            ex, ey = entry[x['n']]
            L = layer[b]; ctrack[L] += 1
            vx = sx + 30 + 16 * ctrack[L]                        # own vertical track in this corridor
            if back(x):
                btrack += 1; by = BOTBAND + 26 * btrack
                tL = layer[x['to']] - 1; ctrack[tL] += 1
                vx2 = (colx[tL] + BW + LANEPAD + LANE - 40 + 30 + 16 * ctrack[tL]) if tL >= 0 else ex - 30 - 12 * btrack
                pts = [(sx, sy), (vx, sy), (vx, by), (vx2, by), (vx2, ey), (ex - 4, ey)]
                dash = ' stroke-dasharray="3 5"'
            elif fwd_long(x):
                ltrack += 1; ty2 = TOPBAND - 40 - 26 * ltrack
                tL = layer[x['to']] - 1; ctrack[tL] += 1
                vx2 = colx[tL] + BW + LANEPAD + LANE - 40 + 30 + 16 * ctrack[tL]
                pts = [(sx, sy), (vx, sy), (vx, ty2), (vx2, ty2), (vx2, ey), (ex - 4, ey)]
            else:
                pts = [(sx, sy), (vx, sy), (vx, ey), (ex - 4, ey)]
            svg.append(f'<path d="{rpath(pts)}" fill="none" stroke="{c}" stroke-width="2.5"{dash} marker-end="url(#a-{x["status"]})" data-e="{x["n"]}"/>')
    cards = []
    for b in boards:
        x0, y0 = pos[b]
        boxes = ''.join(f'<i class="iss" style="left:{r["box"][0] * S}px;top:{r["box"][1] * S}px;width:{r["box"][2] * S}px;height:{r["box"][3] * S}px" title="{e(r["see"])}"><b>{i + 1}</b></i>' for i, r in enumerate(issues[b]))
        st = prog.get(b, {}).get('state', '')
        st_html = f' <span class="state {e(st)}">{e(st)}</span>' if st else ''
        cards.append(f'<figure class="board" style="left:{x0}px;top:{y0}px" data-b="{e(b)}"><figcaption class="bhead">{e(b)}{st_html}</figcaption><div class="shot"><img src="img/{e(b)}.jpg" alt="{e(b)}" width="{BW}" height="{BH}">{boxes}</div></figure>')
    proto = {}   # one hotspot per control; it follows the first edge with a target, and shows every note of that control
    rank = {'wrong': 0, 'untested': 1, 'ok': 2}
    for b in boards:
        hs = {}
        for x in [x for x in edges if x['from'] == b]:
            h = hs.setdefault(tuple(x['box']), {'box': x['box'], 'control': x['control'], 'n': [], 'to': None, 'status': 'ok', 'notes': []})
            h['n'].append(x['n'])
            if x.get('to') and not h['to']: h['to'] = x['to']
            if rank[x['status']] < rank[h['status']]: h['status'] = x['status']
            if x.get('note'): h['notes'].append(x['note'] + (f" (#{x['issue']})" if x.get('issue') else ''))
            elif x['status'] == 'untested' and x.get('to'): h['notes'].append(f"Drawn: goes to {x['to']}. Not tested on dev yet.")
        proto[b] = list(hs.values())
    panel = {b: [{'k': r['kind'], 'sev': r['severity'], 'lens': r.get('lens', ''), 'see': r.get('see', ''), 'why': r.get('why', ''), 'fix': r.get('fix', ''), 'feel': r.get('feel', '')} for r in finds[b]] for b in boards}
    total = len(progress.get('order', [])) or len(boards)
    locked = sum(1 for v in prog.values() if v.get('state') == 'locked')
    head = f"Screen {len(boards)} of {total} added · {locked} locked by the owner"
    page = TEMPLATE.replace('%PANEL%', js(panel)).replace('%HEAD%', e(head)).replace('%TITLE%', e(F['name'])).replace('%W%', str(W)).replace('%H%', str(H)) \
        .replace('%SVG%', '\n'.join(svg)).replace('%BOARDS%', '\n'.join(cards)).replace('%LABELS%', '\n'.join(labels)) \
        .replace('%NOTES%', '\n'.join(notes)).replace('%PROTO%', js(proto)).replace('%START%', js(F['start'])) \
        .replace('%COUNTS%', ' · '.join(f'{v} {k}' for k, v in collections.Counter(x['status'] for x in edges).items())) \
        .replace('%ABOUT%', e(F.get('about', '')))
    open(os.path.join(out, 'index.html'), 'w').write(page)
    print(os.path.join(out, 'index.html'), len(boards), 'boards', len(edges), 'edges')

TEMPLATE = '''<title>%TITLE%</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
/* Layout: one deliberate light look (the boards are light): a toolbar, then a pannable map of boards and arrows. */
:root { --canvas:#E9E9E6; --paper:#FAFAF8; --ink:#1F2421; --ok:#2E6B3F; --wrong:#B3261E; --grey:#706F70; --note:#FFDE59; --line:#CFCFCA;
  --display:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif; --body:system-ui,-apple-system,'Segoe UI',Roboto,sans-serif; --mono:ui-monospace,Menlo,Consolas,monospace; color-scheme:light }
html,body { height:100% } body { margin:0; background:var(--canvas); color:var(--ink); font:15px/1.4 var(--body); display:flex; flex-direction:column }
header { padding-block:12px; padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); background:var(--paper); border-bottom:1px solid var(--line); display:flex; flex-wrap:wrap; gap:8px 20px; align-items:center }
h1 { font:800 22px var(--display); margin:0; letter-spacing:-0.01em }
.sub { font:13px var(--mono); color:var(--grey); flex-basis:100% } .sub:empty { display:none }
.legend { display:flex; flex-wrap:wrap; gap:6px 14px; font:13px var(--mono) }
.legend span::before { content:""; display:inline-block; width:22px; height:0; border-top:3px solid; vertical-align:middle; margin-right:6px }
.legend .ok::before { border-color:var(--ok) } .legend .wrong::before { border-color:var(--wrong) } .legend .untested::before { border-color:var(--grey); border-top-style:dashed }
.legend .back::before { border-color:var(--grey); border-top-style:dotted } .legend .nt::before { width:14px; height:12px; border:0; background:var(--note) } .legend .is::before { width:12px; height:12px; border:2px solid var(--wrong) }
.tools { display:flex; gap:6px; margin-left:auto }
button, label.t { font:500 13px var(--mono); border:1px solid var(--ink); background:var(--paper); color:var(--ink); border-radius:999px; padding:6px 12px; cursor:pointer }
button.primary { background:var(--ink); color:var(--paper) } button:focus-visible { outline:2px solid var(--wrong); outline-offset:2px }
#view { flex:1; overflow:hidden; position:relative; touch-action:none; cursor:grab }
#map { position:absolute; left:0; top:0; width:%W%px; height:%H%px; transform-origin:0 0 }
#map svg { position:absolute; inset:0; overflow:visible; pointer-events:none }
.board { position:absolute; margin:0; width:195px }
.bhead { position:absolute; left:0; top:0; width:491px; height:30px; box-sizing:border-box; display:flex; align-items:center; gap:8px; font:500 13px var(--mono); color:var(--ink); white-space:nowrap }
.shot { position:absolute; left:0; top:44px; width:195px; height:422px }
.shot img { display:block; width:195px; height:422px; box-sizing:border-box; border:1px solid var(--line) }
.iss { position:absolute; border:2px solid var(--wrong); box-sizing:border-box } body.noiss .iss { display:none }
.iss b { position:absolute; left:-2px; top:-2px; background:var(--wrong); color:#FFFFFF; font:600 10px var(--mono); padding:0 4px }
.state { font:500 11px var(--mono); padding:2px 6px; border-radius:4px; background:var(--line); color:var(--ink) } .state.locked { background:var(--ok); color:#FFFFFF }
.lab { position:absolute; box-sizing:border-box; font:500 12px/18px var(--mono); padding:9px 8px; border-radius:6px; background:var(--paper); border:2px solid; overflow:hidden; z-index:2 }
.lab.ok { border-color:var(--ok); color:var(--ok) } .lab.wrong { border-color:var(--wrong); color:var(--wrong) } .lab.untested { border-color:var(--grey); color:#4F4E4F }
.ghost { position:absolute; box-sizing:border-box; border:2px dashed var(--grey); color:#4F4E4F; background:var(--paper); font:12px/18px var(--mono); padding:8px 8px; overflow:hidden }
.board { cursor:pointer }
#drawer { position:fixed; right:0; top:0; bottom:0; width:min(420px,100vw); background:var(--paper); border-left:1px solid var(--line); overflow:auto; z-index:15; padding-block:16px; padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); box-sizing:border-box }
#drawer h2 { font:800 20px var(--display); margin:12px 0 8px } #drawer ol { padding-left:22px; display:flex; flex-direction:column; gap:12px }
#drawer li.good { list-style:'✓ '; color:var(--ok) } #drawer .m { font:12px var(--mono); color:#4F4E4F } #drawer .fx { font-weight:600 }
.prog { font:600 14px var(--mono); background:var(--ink); color:var(--paper); padding:4px 10px; border-radius:6px }
.note { position:absolute; box-sizing:border-box; background:var(--note); color:var(--ink); font:13px/18px var(--body); padding:10px 10px; overflow:hidden; z-index:3 }
#proto { position:fixed; inset:0; background:var(--canvas); display:flex; flex-direction:column; align-items:center; gap:10px; padding-block:12px; z-index:20 }
#proto[hidden] { display:none } #pbar { display:flex; gap:8px; align-items:center; font:13px var(--mono) }
#pstage { position:relative; height:min(844px, calc(100vh - 140px)); aspect-ratio:390/844 } #pstage img { width:100%; height:100%; display:block }
.hot { position:absolute; border:2px solid transparent; border-radius:6px; cursor:pointer; background:transparent }
.hot.ok:hover, body.showhot .hot.ok { border-color:var(--ok) } .hot.wrong:hover, body.showhot .hot.wrong { border-color:var(--wrong) } .hot.untested:hover, body.showhot .hot.untested { border-color:var(--grey) }
#toast { max-width:390px; background:var(--note); padding:8px 12px; font-size:14px } #toast:empty { display:none }
</style>
<header>
  <h1>%TITLE%</h1><span class="prog">%HEAD%</span>
  <div class="legend"><span class="ok">works on dev (tested)</span><span class="wrong">wrong</span><span class="untested">drawn, not tested yet</span><span class="back">goes back</span><span class="nt">what goes wrong</span><span class="is">design audit issue</span></div>
  <div class="tools"><button type="button" id="zo" aria-label="Zoom out">−</button><button type="button" id="zi" aria-label="Zoom in">+</button><button type="button" id="fit">Fit</button>
  <label class="t"><input type="checkbox" id="iss" checked> Issues</label><button type="button" class="primary" id="play">Click through</button></div>
  <p class="sub">%COUNTS% · drag to move, pinch or ctrl+scroll to zoom. %ABOUT%</p>
</header>
<div id="view"><div id="map"><svg width="%W%" height="%H%"><defs>
<marker id="a-ok" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#2E6B3F"/></marker>
<marker id="a-wrong" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#B3261E"/></marker>
<marker id="a-untested" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#706F70"/></marker>
</defs>%SVG%</svg>%BOARDS%%LABELS%%NOTES%</div></div>
<aside id="drawer" hidden aria-label="Findings for one screen"><button type="button" id="dclose">Close</button><h2 id="dname"></h2><ol id="dlist"></ol></aside>
<div id="proto" hidden><div id="pbar"><button type="button" id="pback">Back</button><span id="pname"></span><button type="button" id="phot">Show taps</button><button type="button" id="pmap">Map</button></div>
<div id="pstage"><img id="pimg" alt=""></div><div id="toast" role="status"></div></div>
<script>
const P = %PROTO%, START = %START%, PANEL = %PANEL%;
const drawer = document.getElementById('drawer');
document.getElementById('dclose').onclick = () => drawer.hidden = true;
let moved = 0;
document.querySelectorAll('.board').forEach(f => f.addEventListener('click', () => { if (moved > 6) return; const b = f.dataset.b;
  document.getElementById('dname').textContent = b; const ol = document.getElementById('dlist'); ol.textContent = ''; let i = 0;
  (PANEL[b] || []).forEach(r => { const li = document.createElement('li'); li.className = r.k === 'good' ? 'good' : '';
    li.innerHTML = '<div class="m"></div><div class="s"></div><div class="m w"></div><div class="fx"></div>';
    li.querySelector('.m').textContent = (r.k === 'good' ? 'works' : (r.sev + (r.sev !== 'Nit' ? ' · box ' + (++i) : ''))) + ' · ' + r.lens + (r.feel ? ' · feels ' + r.feel : '');
    li.querySelector('.s').textContent = r.see; li.querySelector('.w').textContent = r.why; li.querySelector('.fx').textContent = r.fix ? 'Improve: ' + r.fix : '';
    ol.appendChild(li); });
  if (!ol.children.length) ol.innerHTML = '<li>Not reviewed yet.</li>'; drawer.hidden = false; }));
const view = document.getElementById('view'), map = document.getElementById('map');
let s = 1, x = 0, y = 0;
const apply = () => map.style.transform = `translate(${x}px,${y}px) scale(${s})`;
const fit = () => { s = Math.min(view.clientWidth / map.offsetWidth, view.clientHeight / map.offsetHeight) * 0.98; x = 8; y = 8; apply(); };
const zoom = (k, cx = view.clientWidth / 2, cy = view.clientHeight / 2) => { const n = Math.min(3, Math.max(0.1, s * k)); x = cx - (cx - x) * n / s; y = cy - (cy - y) * n / s; s = n; apply(); };
document.getElementById('zi').onclick = () => zoom(1.25); document.getElementById('zo').onclick = () => zoom(0.8); document.getElementById('fit').onclick = fit;
view.addEventListener('wheel', ev => { if (ev.ctrlKey || ev.metaKey) { ev.preventDefault(); zoom(ev.deltaY < 0 ? 1.1 : 0.9, ev.offsetX, ev.offsetY); } else { ev.preventDefault(); x -= ev.deltaX; y -= ev.deltaY; apply(); } }, { passive: false });
const pts = new Map(); let last = null, pinch = null;
view.addEventListener('pointerdown', ev => { pts.set(ev.pointerId, ev); last = ev; moved = 0; });
view.addEventListener('pointermove', ev => { if (!pts.has(ev.pointerId)) return; pts.set(ev.pointerId, ev);
  if (pts.size === 2) { const [a, b] = [...pts.values()]; const d = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY); if (pinch) zoom(d / pinch); pinch = d; return; }
  if (last) { moved += Math.abs(ev.clientX - last.clientX) + Math.abs(ev.clientY - last.clientY); x += ev.clientX - last.clientX; y += ev.clientY - last.clientY; apply(); } last = ev; });
const up = ev => { pts.delete(ev.pointerId); pinch = null; last = null; }; view.addEventListener('pointerup', up); view.addEventListener('pointercancel', up);
document.getElementById('iss').onchange = ev => document.body.classList.toggle('noiss', !ev.target.checked);
const proto = document.getElementById('proto'), stage = document.getElementById('pstage'), img = document.getElementById('pimg'), toast = document.getElementById('toast');
let hist = [];
function show(b, push = true) {
  if (push && img.dataset.b) hist.push(img.dataset.b);
  img.src = 'img/' + b + '.jpg'; img.alt = b; img.dataset.b = b; document.getElementById('pname').textContent = b;
  stage.querySelectorAll('.hot').forEach(h => h.remove());
  (P[b] || []).forEach(h => { const d = document.createElement('button'); d.type = 'button'; d.className = 'hot ' + h.status;
    d.setAttribute('aria-label', h.control);
    Object.assign(d.style, { left: h.box[0] / 3.9 + '%', top: h.box[1] / 8.44 + '%', width: h.box[2] / 3.9 + '%', height: h.box[3] / 8.44 + '%' });
    d.title = h.n.join(', ') + ' ' + h.control;
    d.onclick = () => { if (h.to) show(h.to); toast.textContent = h.notes.join(' · '); };
    stage.appendChild(d); });
}
document.getElementById('play').onclick = () => { hist = []; img.dataset.b = ''; toast.textContent = ''; proto.hidden = false; show(START, false); };
document.getElementById('pback').onclick = () => { toast.textContent = ''; if (hist.length) show(hist.pop(), false); };
document.getElementById('pmap').onclick = () => { proto.hidden = true; };
document.getElementById('phot').onclick = () => document.body.classList.toggle('showhot');
window.addEventListener('load', fit); window.addEventListener('resize', fit);
</script>
'''
if __name__ == '__main__':
    a = sys.argv[1:]; main(a[0], a[1], a[2], int(a[3]) if len(a) > 3 else None)
