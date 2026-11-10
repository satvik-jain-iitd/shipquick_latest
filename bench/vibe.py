#!/usr/bin/env python3
"""ShipQuick vibe tests (story #189, S11, rule 38). Ten fixed screen prompts per platform; the score is the share
of generated screens with no raw UI.

  python3 bench/vibe.py --selftest                 score the good and bad fixture screens per platform. Zero model calls.
  python3 bench/vibe.py --run --smoke [--out DIR]  2 prompts (android and ios sign_in) x 2 arms on haiku = 4 calls.
  python3 bench/vibe.py --run --full  [--out DIR]  10 screens x 3 platforms x 2 arms = 60 calls. Costs money.

Arms (from bench/run.py): `no-kit` gets the prompt alone; `kit` also gets the agent block that `astryx init`
writes (ui/integration/astryx.integration.mjs, agentDocs.append). Scenario 2 of the story: the block must raise
the score. The cell runner is bench/run.py's `call_claude` (one headless `claude -p` per cell, Bash disallowed, a
temp run folder outside any git tree). The prompt battery shape (same task text on every platform, nothing in the
prompt names the expected component) is borrowed from Meta Astryx internal/vibe-tests/README.md (idea only, no code).
"""
import argparse
import json
import re
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import run as bench  # noqa: E402  bench/run.py: call_claude, inside_git, MODELS, ARMS

PROMPTS = HERE / "vibe_prompts.json"
AGENT_BLOCK = ROOT / "ui" / "integration" / "astryx.integration.mjs"
SMOKE = (("android", "sign_in"), ("ios", "sign_in"))
FIXTURES = ROOT / "tests" / "fixtures"
FIXTURE_DIRS = {"android": ("android/src/good", "android/src/bad"), "ios": ("ios/Good", "ios/Bad"),
                "web": ("web/good", "web/bad")}

# Raw UI, one table. Each row: (rule, regex, path regex that exempts a file or None). The Android rows are the
# Konsist tests and detekt imports in ui/android/lint/, the iOS rows are the custom_rules in ui/ios/lint/swiftlint.yml,
# the web rows are what @astryxdesign/core makes needless (raw elements, hex and rgb colours, inline style, px).
# shortcut: a regex copy of the lint rules; the real linters (detekt, Konsist, SwiftLint, astryx doctor) replace
# this table when they run on CI (story S9, #187). Upgrade when the run folder can be linted there.
THEME = r"/theme/|Theme\.kt$|Color\.kt$"
TOKENS = r"Tokens\.swift$"
WEB_TOKENS = r"tokens\.(css|ts|js)$"
RAW = {
    "android": [
        ("no_canvas", r"\bCanvas\s*\(", None),
        ("no_draw_modifiers", r"\b(drawBehind|drawWithContent|drawWithCache)\b", None),
        ("no_raw_color", r"\bColor\s*\(|\bColor\.[A-Z]", THEME),
        ("no_gesture_input", r"\b(pointerInput|detectTapGestures|detectDragGestures|draggable|transformable)\b", None),
        ("no_fake_button", r"\b(Box|Row|Column|Spacer|Text|Icon|Image)\((?:[^()]|\([^()]*\))*?\.(clickable|combinedClickable)\b", None),
        ("no_android_view", r"\bAndroidView\b", None),
        ("no_hand_made_shape", r"\b(GenericShape|RoundedCornerShape)\b", None),
        ("no_custom_shape", r"\b(class|object)\s+\w+\s*(\([^)]*\))?\s*:\s*Shape\b", None),
        ("no_m2_or_view_import", r"^\s*import\s+(androidx\.compose\.material\.(?!icons\.)|com\.google\.android\.material\.|android\.widget\.)", None),
        ("no_wildcard_draw_import", r"^\s*import\s+androidx\.compose\.(foundation|foundation\.shape|foundation\.gestures|ui\.draw|ui\.graphics|ui\.input\.pointer|ui\.viewinterop)\.\*", None),
    ],
    "ios": [
        ("no_raw_color", r"\b(?:UI|NS)?Color(?:\.init)?\s*\([^)]*\b(?:red|hue|white)\s*:|\.init\(\s*(?:\.\w+\s*,\s*)?(?:red|hue|white)\s*:", TOKENS),
        ("no_fixed_font_size", r"\.system\(\s*size:", TOKENS),
        ("no_custom_font", r"\bFont\.custom\s*\(", TOKENS),
        ("no_import_outside_allowlist", r"^\s*(?:@\w+\s+)?import\s+(?!(?:SwiftUI|Foundation|ShipQuickUI|Charts|Observation|SwiftData|Testing)\b)\w", None),
        ("no_custom_shape_or_style", r"\b(?:struct|class|enum|extension)\s+[\w.]+(?:<[^>{]*>)?\s*:\s*(?:[\w.]+(?:<[^>{]*>)?\s*[,&]\s*)*(?:Shape|InsettableShape|ButtonStyle|PrimitiveButtonStyle|ToggleStyle|LabelStyle)\b", None),
        ("no_path", r"\bPath\s*[({]", None),
        ("no_canvas", r"\bCanvas\s*[({]", None),
        ("no_gesture", r"\.(?:gesture|simultaneousGesture|highPriorityGesture|onTapGesture|onLongPressGesture)\s*[({]|\b(?:DragGesture|TapGesture|LongPressGesture|MagnificationGesture|RotationGesture|SpatialTapGesture)\b", None),
        ("no_uikit_view", r"\bclass\s+\w+\s*:[^{]*\bUIView\b|\bUIView(?:Controller)?Representable\b", None),
        ("no_number_in_layout_modifier", r"\.(?:padding|frame|cornerRadius|offset|position|lineSpacing|shadow|blur|tracking|kerning)\([^)]*?(?<![\w.])\d", TOKENS),
        ("no_number_in_spacing", r"\bspacing:\s*\d", TOKENS),
    ],
    "web": [
        # a hex colour sits in quotes or after a CSS colon; a bare #189 in a comment is an issue number, not a colour
        ("no_hex_colour", r"(?<=['\"])#[0-9a-fA-F]{3,8}\b|:\s*#[0-9a-fA-F]{3,8}\b", WEB_TOKENS),
        ("no_rgb_colour", r"\b(?:rgba?|hsla?)\s*\(", WEB_TOKENS),
        ("no_inline_style", r"\bstyle=(\{\{|\")", None),
        ("no_raw_element", r"<(button|input|select|textarea|canvas|svg|dialog)\b", None),
        ("no_px", r"\b\d+px\b", WEB_TOKENS),
        ("no_other_ui_kit", r"from\s+['\"](@mui/|antd|@chakra-ui/|react-bootstrap|@radix-ui/|@headlessui/|bootstrap)", None),
    ],
}


def prompts() -> dict:
    """{platform: [{id, task, prompt, file}, ...]}: the same ten tasks on every platform, each with its lead."""
    data = json.loads(PROMPTS.read_text(encoding="utf-8"))
    out = {}
    for platform, p in data["platforms"].items():
        out[platform] = [{"id": s["id"], "task": s["task"], "file": p["file"],
                          "prompt": f"{p['lead']}\n\n## Task\n{s['task']}\n\n## Output\n{data['output'].format(file=p['file'])}"}
                         for s in data["screens"]]
    return out


def exts(platform) -> tuple:
    return tuple(json.loads(PROMPTS.read_text(encoding="utf-8"))["platforms"][platform]["ext"])


def score_dir(platform: str, work: Path) -> dict:
    """clean=1 when every screen file under work has no raw UI hit; clean=0 with the hits, or when no file exists."""
    files = sorted(p for p in Path(work).rglob("*") if p.is_file() and p.suffix in exts(platform))
    if not files:
        return {"clean": 0, "files": 0, "hits": [], "reason": "no screen file written"}
    hits = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        rel = str(f.relative_to(work))
        for rule, rx, exempt in RAW[platform]:
            if exempt and re.search(exempt, rel):
                continue
            if re.search(rx, text, re.M):
                hits.append(f"{rel}:{rule}")
    return {"clean": int(not hits), "files": len(files), "hits": hits,
            "reason": "clean" if not hits else "raw UI: " + ", ".join(hits)}


def agent_block(path: Path = AGENT_BLOCK) -> str:
    """The lines `astryx init` appends to the managed agent block (agentDocs.append in the integration file)."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"append:\s*\[(.*?)\n\s*\]", text, re.S)
    lines = re.findall(r"^\s*'(.*)',\s*$", m.group(1) if m else "", re.M)
    if not lines:
        raise SystemExit(f"no agentDocs.append lines in {path}")
    return "\n".join(lines)


def selftest() -> int:
    """Each platform's good fixture must be clean and its bad fixture caught. Zero model calls. Returns failures."""
    failed = 0
    for platform, (good, bad) in FIXTURE_DIRS.items():
        g, b = score_dir(platform, FIXTURES / good), score_dir(platform, FIXTURES / bad)
        ok = g["clean"] == 1 and b["clean"] == 0
        failed += int(not ok)
        print(f"{'ok ' if ok else 'XX '} {platform:8} good={g['clean']} ({g['reason']})  bad={b['clean']} ({len(b['hits'])} hits)")
    print(f"selftest {len(FIXTURE_DIRS) - failed}/{len(FIXTURE_DIRS)} platforms pass")
    return failed


def run_one(platform, item, arm, model, out: Path, claude, timeout, rules) -> dict:
    name = f"{platform}__{item['id']}__{arm}__{model}"
    cell = out / name
    facts = bench.call_claude(item["prompt"], model, cell, claude, timeout, rules if arm == "kit" else None)
    meta = {"name": name, "platform": platform, "screen": item["id"], "arm": arm, "model": model, **facts}
    (cell / "cell.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return {**meta, **score_dir(platform, cell / "work")}


def run_all(cells, arms, models, workers, timeout, out: Path, rules: str) -> dict:
    claude = shutil.which("claude")
    if not claude:
        raise SystemExit("claude CLI not found on PATH")
    out.mkdir(parents=True, exist_ok=True)
    jobs = [(p, item, a, m) for (p, item) in cells for a in arms for m in models]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = [f.result() for f in [pool.submit(run_one, p, i, a, m, out, claude, timeout, rules) for (p, i, a, m) in jobs]]
    score = {a: {"clean": sum(r["clean"] for r in results if r["arm"] == a),
                 "screens": sum(1 for r in results if r["arm"] == a)} for a in arms}
    (out / "results.json").write_text(json.dumps({"results": results, "score": score}, indent=2), encoding="utf-8")
    for r in results:
        print(f"{'ok ' if r['clean'] else '   '}{r['name']:40} {'killed ' if r.get('killed') else ''}{r['reason']}")
    for a, s in score.items():
        print(f"{a:7} {s['clean']}/{s['screens']} screens clean")
    return score


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="ShipQuick vibe tests (story #189)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="2 prompts x 2 arms = 4 calls")
    ap.add_argument("--full", action="store_true", help="every prompt: 10 x 3 x 2 arms = 60 calls")
    ap.add_argument("--arms", default="no-kit,kit")
    ap.add_argument("--models", default="haiku")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=bench.CELL_TIMEOUT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--kit-rules", default=str(AGENT_BLOCK), help="the .mjs integration file, or any text file")
    a = ap.parse_args(argv)
    if a.selftest:
        return 1 if selftest() else 0
    if not a.run:
        ap.error("pick one: --selftest or --run")
    if a.smoke == a.full:
        ap.error("--run needs exactly one of --smoke (4 calls) or --full (60 calls)")
    arms = [x.strip() for x in a.arms.split(",")]
    models = [x.strip() for x in a.models.split(",")]
    for x in arms:
        if x not in bench.ARMS:
            ap.error(f"unknown arm {x}; arms are {', '.join(bench.ARMS)}")
    for m in models:
        if m not in bench.MODELS:
            ap.error(f"unknown model {m}; models are {', '.join(bench.MODELS)}")
    out = Path(a.out).resolve() if a.out else Path(tempfile.mkdtemp(prefix="shipquick-vibe-"))
    if bench.inside_git(out):
        ap.error(f"--out {out} is inside a git work tree: the project settings there would load into every arm. "
                 "Use a folder outside any repo, or leave --out off for a temp folder")
    table = prompts()
    cells = ([(p, next(i for i in table[p] if i["id"] == sid)) for p, sid in SMOKE] if a.smoke
             else [(p, i) for p in table for i in table[p]])
    rules_path = Path(a.kit_rules)
    rules = agent_block(rules_path) if rules_path.suffix == ".mjs" else rules_path.read_text(encoding="utf-8")
    run_all(cells, arms, models, a.workers, a.timeout, out, rules)
    print(f"run folder: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
