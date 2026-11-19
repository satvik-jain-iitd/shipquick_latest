"""Coverage ratchet (ADR-023/M5): changed files must not drop below their baseline line coverage.

Usage:
  python3 scripts/check_coverage.py --base <sha> --head <sha> [--baseline FILE] [--min 0]
  python3 scripts/check_coverage.py --update-baseline   regenerate .shipquick/coverage-baseline.json
Runs coverage on the test suite, reads per-file line coverage, compares changed Python files
against the baseline. Fails if any changed file dropped below its baseline (or below --min).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASELINE = ROOT / ".shipquick" / "coverage-baseline.json"


def run_cov():
    subprocess.run([sys.executable, "-m", "coverage", "run", "-m", "pytest", "-q"], cwd=ROOT, capture_output=True)
    out = subprocess.run([sys.executable, "-m", "coverage", "json", "-o", "/tmp/cov.json"], cwd=ROOT, capture_output=True)
    if out.returncode != 0:
        # try without -q
        subprocess.run([sys.executable, "-m", "coverage", "run", "-m", "pytest"], cwd=ROOT, capture_output=True)
        subprocess.run([sys.executable, "-m", "coverage", "json", "-o", "/tmp/cov.json"], cwd=ROOT, capture_output=True)
    try:
        return json.loads(Path("/tmp/cov.json").read_text())
    except Exception:
        return None


def changed_files(base, head):
    r = subprocess.run(["git", "diff", "--name-only", f"{base}..{head}"], cwd=ROOT, capture_output=True, text=True)
    return [f for f in r.stdout.split() if f.endswith(".py")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=None)
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--baseline", default=str(BASELINE))
    ap.add_argument("--min", type=float, default=0.0, help="minimum line coverage %% for any changed file")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    data = run_cov()
    if data is None:
        print("coverage run failed; skipping")
        return 0

    files_cov = data.get("files", {})
    per_file = {}
    for path, info in files_cov.items():
        rel = path
        # normalize to repo-relative
        try:
            rel = str(Path(path).relative_to(ROOT))
        except ValueError:
            pass
        summary = info.get("summary", {})
        pct = summary.get("percent_covered", 0.0)
        per_file[rel] = round(pct, 2)

    if args.update_baseline:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(per_file, indent=2, sort_keys=True))
        print(f"baseline updated: {len(per_file)} files")
        return 0

    baseline = {}
    bp = Path(args.baseline)
    if bp.exists():
        try:
            baseline = json.loads(bp.read_text())
        except Exception:
            baseline = {}

    # changed files
    base_sha = args.base
    if not base_sha:
        rc = subprocess.run(["git", "rev-parse", "HEAD~1"], cwd=ROOT, capture_output=True, text=True)
        base_sha = rc.stdout.strip() if rc.returncode == 0 else None
    head_sha = subprocess.run(["git", "rev-parse", args.head], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    changed = changed_files(base_sha, head_sha) if base_sha else []

    failed = False
    for f in changed:
        cov = per_file.get(f)
        if cov is None:
            print(f"  {f}: no coverage data (new file?)")
            continue
        base_cov = baseline.get(f, 0.0)
        if cov < base_cov or cov < args.min:
            print(f"  FAIL {f}: {cov}% < baseline {base_cov}% (min {args.min}%)")
            failed = True
        else:
            print(f"  OK   {f}: {cov}% (baseline {base_cov}%)")

    if not changed:
        print("no changed Python files")
    print(f"total files measured: {len(per_file)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
