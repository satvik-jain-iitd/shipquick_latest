#!/usr/bin/env python3
"""Lay out a Design canvas (the claude.ai Design artifact type) by stage, from a manifest.

The manifest (design/canvas-stages.json) names sections, rows and the boards in each row, and the project's own
colours (tints, ink, paper) and font. The tool places every board and story note, draws one background artboard
per section (an artboard, listed first in `order`, so it sits under the screens; a note never can), sized from what
is inside it, paints the section title, its purpose and every row title ON that board (ink on the fill, 4.5:1 or
the run stops), and prefixes every board's name with its state. Nothing is deleted: a board the manifest does not
name goes to an Unsorted row; the only notes the tool removes are the ones named in `remove_notes` and its own
(`cs-` prefix). The run fails, and writes nothing, when two boxes overlap or a box sits outside its section's board,
or (story #125) a board in the section whose id is "production" has no provenance: there, a `boards` entry must be
{"board": "<name>", "pr": "<the PR that changed it>", "approved": "<its approval date>"}, not a plain filename —
provenance, not recency, decides a Production board; with no approved board behind a change, the app is the drift.

Use:  canvas_stage.py --manifest design/canvas-stages.json --canvas <folder holding project/> --check
      canvas_stage.py --manifest design/canvas-stages.json --canvas <folder holding project/> --apply
Standard library only. No project value lives in this file: every colour and the font come from the manifest.
"""
import argparse, json, re, sys
from pathlib import Path

PITCH_X, ROW_PITCH, SECTION_GAP, PAD = 470, 1150, 600, 140
TITLE_GAP = 230            # a row title sits this far above its row (the editor wants at least 223)
TITLE_H, ROW_TITLE_H = 90, 50
BAND_H = 300               # the band at the top of a section's first tile: its title and purpose
MAX_SIDE = 8000            # an artboard's side is capped by the editor
PREFIXES = ("LIVE", "ON STAGING", "DESIGN", "IN TALK", "REJECTED", "OLD", "UNSORTED")
MINE = re.compile(r"^cs-")     # the one prefix reserved for notes this tool writes; a user's note is never touched
DEFAULT_PAPER, DEFAULT_FONT = "#ffffff", "system-ui, sans-serif"


def clean_title(t: str) -> str:
    return re.sub(r"^(" + "|".join(PREFIXES) + r") · ", "", t)


def box(x, y, w, h, name):
    return {"x": x, "y": y, "w": w, "h": h, "name": name}


def board_name(entry):
    """A row's `boards` entry is a plain filename, or (Production only, story #125) {"board", "pr", "approved"}."""
    return entry if isinstance(entry, str) else entry.get("board")


PR_RE = re.compile(r"^#\d+$|^https?://\S+/pulls?/\d+/?$")


def valid_pr(pr, approved, provenance_since):
    """A Production entry's "pr": "#<n>", a PR URL, or (story #125 review blocker) "baseline" — but
    only when the manifest's "provenance_since" is set and this board's "approved" date is on or
    before it, so a GoServe-style migration cannot fake provenance for a board approved afterwards."""
    if pr == "baseline":
        return bool(provenance_since) and approved <= provenance_since
    return bool(PR_RE.match(pr or ""))


def overlaps(a, b):
    return a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]


def inside(a, outer, pad):
    return a["x"] >= outer["x"] + pad and a["y"] >= outer["y"] + pad and a["x"] + a["w"] <= outer["x"] + outer["w"] - pad and a["y"] + a["h"] <= outer["y"] + outer["h"] - pad


def mix(hex_a, hex_b, a_share):
    """color-mix in sRGB, as the page paints it: a_share of hex_a over hex_b."""
    ra, ga, ba = (int(hex_a[i:i + 2], 16) for i in (1, 3, 5)); rb, gb, bb = (int(hex_b[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(round(x * a_share + y * (1 - a_share)) for x, y in ((ra, rb), (ga, gb), (ba, bb)))


def contrast(hex_fg, hex_bg):
    def lum(h):
        def ch(c):
            c /= 255; return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (ch(int(h[i:i + 2], 16)) for i in (1, 3, 5)); return 0.2126 * r + 0.7152 * g + 0.0722 * b
    a, b = lum(hex_fg), lum(hex_bg); a, b = max(a, b), min(a, b); return (a + 0.05) / (b + 0.05)


def tile_fill(tint, paper=DEFAULT_PAPER): return mix(tint, paper, 0.28)


def theme(manifest: dict):
    """The project's colours and font, from the manifest only. Returns (theme dict, problems)."""
    problems = []
    tints = manifest.get("tints") or {}
    hexes = [v for v in list(tints.values()) + [manifest.get("ink"), manifest.get("paper", DEFAULT_PAPER)] if v is not None]
    if not tints: problems.append("manifest has no tints: add \"tints\": {\"<name>\": \"#rrggbb\", ...} from the project's tokens")
    if not manifest.get("ink"): problems.append("manifest has no ink: add \"ink\": \"#rrggbb\" (the text colour painted on the boards)")
    for h in hexes:
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", str(h)): problems.append(f"{h} is not a #rrggbb colour")
    th = {"tints": tints, "ink": manifest.get("ink", "#000000"), "paper": manifest.get("paper", DEFAULT_PAPER), "font": manifest.get("font", DEFAULT_FONT)}
    for name, tint in tints.items():   # every word on a board is ink on the board's fill: 4.5:1 or the run stops
        if not problems and contrast(th["ink"], tile_fill(tint, th["paper"])) < 4.5: problems.append(f"tint {name}: ink on its fill is under 4.5:1")
    return th, problems


def esc(t): return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def bg_html(title, purpose, tint, w, h, th, row_titles=(), band=True):
    """A background board: the fill, a band with the section title and purpose (first tile only: a continued tile has no band,
    so a row title can never sit on it), and every row title drawn ON the board (ink on the light fill, 4.5:1 checked by the tool),
    so no text ever depends on the editor's own note colours."""
    ink, fill = th["ink"], tile_fill(tint, th["paper"])
    rows = "\n".join(f'  <h2 style="position: absolute; left: {x}px; top: {y}px; margin: 0; font-size: 36px; line-height: 1.1; font-weight: 700; white-space: nowrap;">{esc(t)}</h2>' for x, y, t in row_titles)
    head = f"""  <div style="display: flex; flex-direction: column; gap: 12px; max-width: 1400px; padding: 40px 48px;">
    <h1 style="margin: 0; font-size: 56px; line-height: 1.05; font-weight: 800;">{esc(title)}</h1>
    <p style="margin: 0; font-size: 22px; line-height: 1.4;">{esc(purpose)}</p>
  </div>""" if band else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<style>
body{{margin:0}}
</style>
</helmet>
<div style="position: relative; width: {w}px; height: {h}px; box-sizing: border-box; overflow: hidden; background: {fill}; border: 2px solid {mix(tint, ink, 0.6)}; font-family: {th['font']}; color: {ink};">
{head}
{rows}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
"""


def text_height(text: str, width_px=1400, size=22):
    """A rough height for a paragraph painted in the band: enough lines at this size, never too few."""
    per_line = max(1, int(width_px / (size * 0.52)))
    return (len(text) // per_line + 1) * int(size * 1.4)


def layout(canvas: dict, manifest: dict):
    """Return (new canvas dict, background files {path: html}, problems list). Nothing is written here."""
    c = json.loads(json.dumps(canvas))
    boards, notes = c["boards"], c.setdefault("notes", {})
    th, problems = theme(manifest)
    sections = json.loads(json.dumps(manifest.get("sections") or []))
    if not sections:
        problems.append("manifest has no sections"); return c, {}, problems
    # 1. every board exactly once; unknown boards go to an Unsorted row
    named = {}
    for s in sections:
        for r in s["rows"]:
            for entry in r["boards"]:
                b = board_name(entry)
                if b in named: problems.append(f"{b} is in two rows: {named[b]} and {r['id']}")
                named[b] = r["id"]
                if b not in boards: problems.append(f"{b} is in the manifest but not on the canvas (row {r['id']})")
                if s.get("id") == "production":
                    prov = entry if isinstance(entry, dict) else {}
                    pr, approved = prov.get("pr"), prov.get("approved")
                    if not pr or not approved:
                        problems.append(f"{b} (row {r['id']}) moves into or stays in Production with no PR and approved date cited — "
                                         "the manifest entry must be {\"board\": ..., \"pr\": ..., \"approved\": ...} (story #125); "
                                         "with no approved board behind it, the app is the drift and the board stands")
                    elif not valid_pr(pr, approved, manifest.get("provenance_since")):
                        since = manifest.get("provenance_since")
                        if pr == "baseline":
                            problems.append(f"{b} (row {r['id']}): pr \"baseline\" needs manifest \"provenance_since\" set and approved "
                                             f"({approved}) on or before it (provenance_since: {since or 'not set'}) — otherwise cite the real PR")
                        else:
                            problems.append(f"{b} (row {r['id']}): pr {pr!r} is not \"baseline\", \"#<n>\" or a PR URL")
    for k in [k for k in boards if k.startswith("bg/")]: boards.pop(k)
    unsorted = [k for k in boards if k not in named]
    if unsorted:
        host = sections[min(2, len(sections) - 1)]
        host["rows"].append({"id": "unsorted", "title": "Unsorted · on the canvas, not yet in the manifest: place each one", "prefix": "UNSORTED", "boards": sorted(unsorted), "notes": []})
    # 2. drop the tool's own notes from earlier runs, and the ones the manifest names; keep every other note
    for k in [k for k in notes if MINE.match(k) or k in manifest.get("remove_notes", [])]: notes.pop(k)
    # 3. place everything
    y = 0; boxes = []; bg_files = {}; bg_entries = []; section_boxes = []
    tint_of = lambda name: th["tints"].get(name) or (next(iter(th["tints"].values())) if th["tints"] else DEFAULT_PAPER)
    sh = manifest.get("start_here")
    if sh:
        # the start note is painted on its own small board, so its colour is measured like every other word
        h = 40 * 2 + 60 + 12 + text_height(sh)
        sb = [box(0, y, 1400 + 96, h, "start-band")]
        boxes += sb
        x0, y0, x1, y1 = -PAD, y - PAD, 1400 + 96 + PAD, y + h + PAD
        bg_entries.append(("bg/start.dc.html", {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0, "title": "Start here (background)"}))
        bg_files["project/bg/start.dc.html"] = bg_html(manifest.get("start_title", "Design canvas · start here"), sh, tint_of(manifest.get("start_tint", "")), x1 - x0, y1 - y0, th)
        section_boxes.append((0, box(x0, y0, x1 - x0, y1 - y0, "start"), sb))
        y = y1 + SECTION_GAP
    for n, s in enumerate(sections, 1):
        top = y; sboxes = []; row_titles = []
        # the section title and purpose are painted on the board's band (see bg_html); this box reserves the band's space
        sboxes.append(box(0, top, 3600, BAND_H - 40, f"band {n}"))
        ry = top + BAND_H + TITLE_GAP   # the first row starts under the band
        row_tops = []
        for r in s["rows"]:
            rid = "r-" + r["id"]; prefix = r.get("prefix", s.get("prefix", "DESIGN"))
            if prefix not in PREFIXES: problems.append(f"row {r['id']}: prefix {prefix} is not one of {PREFIXES}")
            row_titles.append((0, ry - TITLE_GAP, r["title"]))   # painted on the board, ink on the fill
            sboxes.append(box(0, ry - TITLE_GAP, 3600, ROW_TITLE_H, rid)); row_tops.append(ry - TITLE_GAP - 20)
            x = 0; tallest = 0
            for entry in r["boards"]:
                b = board_name(entry)
                if b not in boards: continue
                e = boards[b]; e["x"], e["y"] = x, ry; e["title"] = f"{prefix} · " + clean_title(e.get("title", b))
                sboxes.append(box(x, ry, e["w"], e["h"], b)); x += e["w"] + 80; tallest = max(tallest, e["h"])
            for nid in r.get("notes", []):
                if nid not in notes: problems.append(f"note {nid} (row {r['id']}) is not on the canvas"); continue
                nt = notes[nid]; nt["x"], nt["y"] = x, ry; w = nt.get("w", 360)
                sboxes.append(box(x, ry, w, w * 4 // 3, nid)); x += w + 80; tallest = max(tallest, w * 4 // 3)
            ry += max(ROW_PITCH, tallest + TITLE_GAP + 76)   # a tall note pushes the next row down, so nothing ever overlaps
        # 4. the section's background: around everything inside it, then split into tiles of at most 8000
        x0 = min(b["x"] for b in sboxes) - PAD; y0 = min(b["y"] for b in sboxes) - PAD
        x1 = max(b["x"] + b["w"] for b in sboxes) + PAD; y1 = max(b["y"] + b["h"] for b in sboxes) + PAD
        if x1 - x0 > MAX_SIDE: problems.append(f"section {n} is {x1 - x0} px wide; the cap is {MAX_SIDE}: split a row")
        cuts = [y0]; cur = y0
        for rt in row_tops:
            if rt - cur > MAX_SIDE: problems.append(f"section {n}: a row block is taller than {MAX_SIDE}")
            if rt - cuts[-1] > MAX_SIDE - ROW_PITCH: cuts.append(cur)
            cur = rt
        if y1 - cuts[-1] > MAX_SIDE: cuts.append(cur)
        cuts.append(y1)
        for t in range(len(cuts) - 1):
            path = f"bg/section-{n}-{t + 1}.dc.html"; w, h = x1 - x0, cuts[t + 1] - cuts[t]
            bg_entries.append((path, {"x": x0, "y": cuts[t], "w": w, "h": h, "title": f"{s['title']} (background {t + 1} of {len(cuts) - 1})"}))
            mine = [(rx - x0, ryy - cuts[t], txt) for rx, ryy, txt in row_titles if cuts[t] <= ryy < cuts[t + 1]]   # the row titles this tile holds
            if t == 0:   # text painted on a tile must never meet other text painted on it: the band is a box too
                band_box = box(x0, cuts[0], 1400 + 96, BAND_H - 40, f"band of section {n}")
                for rx, ryy, txt in mine:
                    if overlaps(band_box, box(rx + x0, ryy + cuts[0], 3600, ROW_TITLE_H, txt)): problems.append(f"row title '{txt}' sits on the band of section {n}")
            bg_files["project/" + path] = bg_html(s["title"], s.get("purpose", "") if t == 0 else "", tint_of(s.get("tint", "")), w, h, th, mine, band=(t == 0))
        section_boxes.append((n, box(x0, y0, x1 - x0, y1 - y0, f"section {n}"), sboxes))
        boxes += sboxes; y = y1 + SECTION_GAP
    # 5. checks
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if overlaps(a, b): problems.append(f"{a['name']} overlaps {b['name']}")
    for n, outer, sboxes in section_boxes:
        for b in sboxes:
            if not inside(b, outer, PAD - 1): problems.append(f"{b['name']} is outside the board of section {n}")
    for path, e in bg_entries:
        boards[path] = e
    c["order"] = [p for p, _ in bg_entries] + [k for k in c.get("order", []) if k in boards and not k.startswith("bg/")] + [k for k in boards if k not in c.get("order", []) and not k.startswith("bg/")]
    c["noteOrder"] = list(notes)
    return c, bg_files, problems


def check_existing(canvas: dict):
    """Overlap on a canvas as it is now (boards and sticky notes), before any relayout. `--check` prints these first."""
    bs = [box(e["x"], e["y"], e["w"], e["h"], k) for k, e in canvas["boards"].items() if not k.startswith("bg/")]
    ns = [box(n["x"], n["y"], n.get("maxW", n.get("w", 360)), TITLE_H if n.get("kind") == "title1" else n.get("w", 360) * 4 // 3, k) for k, n in canvas.get("notes", {}).items() if n.get("kind") in (None, "title1")]
    out = []
    allb = bs + ns
    for i, a in enumerate(allb):
        for b in allb[i + 1:]:
            if overlaps(a, b): out.append(f"{a['name']} overlaps {b['name']}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--manifest", required=True); ap.add_argument("--canvas", required=True, help="the folder that holds project/canvas.json")
    g = ap.add_mutually_exclusive_group(required=True); g.add_argument("--check", action="store_true"); g.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.canvas); cj = root / "project" / "canvas.json"
    canvas = json.loads(cj.read_text()); manifest = json.loads(Path(a.manifest).read_text())
    if a.check:
        for p in check_existing(canvas): print("NOW " + p)   # what overlaps on the canvas as it is, before any relayout
    new, bg_files, problems = layout(canvas, manifest)
    if problems:
        print("\n".join("PROBLEM " + p for p in problems)); return 1
    if a.check:
        same = json.dumps({k: (v["x"], v["y"]) for k, v in new["boards"].items()}, sort_keys=True) == json.dumps({k: (v.get("x"), v.get("y")) for k, v in canvas["boards"].items()}, sort_keys=True)
        print("ok, no problem;", "the canvas already matches the manifest" if same else "positions differ from the manifest: run --apply"); return 0
    cj.write_text(json.dumps(new, indent=1, ensure_ascii=False))
    for p, html in bg_files.items():
        f = root / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(html)
    print(f"wrote {cj} and {len(bg_files)} background boards: {', '.join(bg_files)}"); return 0


if __name__ == "__main__":
    sys.exit(main())
