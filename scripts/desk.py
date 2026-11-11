"""ShipQuick Desk, Option B (epic #91): one stdlib server on 127.0.0.1 that asks gh on request.

Serves the page at / and the state at /api/state.json. The state is cached for 60 s.
Only read-only gh calls. Nothing is written to disk, no token is read.
Usage: python3 scripts/desk.py [--port 8765]
"""
import argparse
import csv
import fnmatch
import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import features  # noqa: E402  the one features reader (story #427); the Desk never parses the file itself
DEFAULT_PORT = 8765
TTL_SECONDS = 60
GH_TIMEOUT = 20
TRACE_ROWS = 10


class DeskError(Exception):
    pass


def gh_runner(repo_dir):
    def run(args):
        try:
            p = subprocess.run(["gh", *args], cwd=repo_dir, capture_output=True, text=True, timeout=GH_TIMEOUT)
        except FileNotFoundError:
            raise DeskError("gh is not installed")
        except subprocess.TimeoutExpired:
            raise DeskError("gh timed out after %d s" % GH_TIMEOUT)
        if p.returncode:
            raise DeskError("gh failed: " + (p.stderr.strip() or "exit %d" % p.returncode))
        return p.stdout
    return run


def checks_summary(rollup):
    results = [c.get("conclusion") or c.get("state") or "" for c in (rollup or [])]
    if any(r in ("FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED") for r in results):
        return "failing"
    if not results or any(r in ("", "PENDING", "EXPECTED", "QUEUED", "IN_PROGRESS") for r in results):
        return "pending"
    return "passing"


def read_trace(repo_dir):
    path = Path(repo_dir) / "docs" / "process-trace.md"
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set("".join(cells)) <= set("-: "):
            continue
        contact = cells[-1]
        if "asked" in contact.lower():
            continue
        rows.append({"text": " | ".join(c for c in cells[:-1] if c), "contact": contact})
    return list(reversed(rows[-TRACE_ROWS:]))


def read_switches(repo_dir):
    root = Path(repo_dir)
    mode = root / ".shipquick" / "mode"
    dev = "not set"
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        for line in claude_md.read_text(encoding="utf-8").splitlines():
            if line.startswith("Dev link:"):
                dev = line.split(":", 1)[1].strip() or "not set"
                break
    return {
        "mode": mode.read_text(encoding="utf-8").strip() if mode.exists() else "not set",
        "freeze": "On" if (root / ".shipquick" / "freeze").exists() else "Off",
        "dev_link": dev,
    }


def protected_globs(repo_dir):
    """The globs of scripts/protected_paths.txt, the one list review_merge.sh reads (the repo's own, else the kit's in a child)."""
    root = Path(repo_dir)
    for rel in ("scripts/protected_paths.txt", "knowledge/shipquick_latest/scripts/protected_paths.txt"):
        f = root / rel
        if f.is_file():
            lines = [l.split("#", 1)[0].strip() for l in f.read_text(encoding="utf-8").splitlines()]
            return [l for l in lines if l] + [".shipquick/*"]
    return [".shipquick/*"]


def owner_reason(p, globs, mode):
    """Why this open PR needs the owner, or None. Order: a protected path, an unticked UAT box, an approval in manual or semi."""
    for f in (x.get("path", "") for x in p.get("files") or []):
        if any(fnmatch.fnmatchcase(f, g) for g in globs):   # bash [[ == ]] glob: `*` crosses `/`, same as fnmatchcase
            return "protected path, your merge (%s)" % f
    if p.get("baseRefName") == "main" and p.get("headRefName") == "dev":
        uat, on = [], False
        for line in (p.get("body") or "").splitlines():
            if line.startswith("## "):
                on = line.startswith("## UAT on dev")
            elif on:
                uat.append(line)
        n = sum(1 for l in uat if re.match(r"\s*[-*] \[ \]", l))
        if n:
            return "release: %d unticked test box%s, you tick them on the dev link" % (n, "" if n == 1 else "es")
    if p.get("reviewDecision") == "APPROVED" and mode in ("manual", "semi", "not set"):
        return "approved, your merge (%s mode)" % mode
    return None


def read_features(repo_dir):
    """Every feature, in groups, from the one reader. A broken file is an error and an empty list, never a wrong list."""
    try:
        m = features.read(repo_dir)["features"]
    except features.FeaturesError as e:
        return {"error": str(e), "groups": []}
    groups = {}
    for fid, f in m.items():
        groups.setdefault(f["group"], []).append({
            "id": fid, "name": f["name"], "what": f["what"], "if_off": f["if_off"], "on": f["on"], "default": f["default"],
            "locked": bool(f.get("locked")), "changed": f["on"] != f["default"]})
    return {"error": None, "groups": [{"name": g, "items": items} for g, items in groups.items()]}


def default_band_path(repo_dir):
    # The Ponytail ledger for this project: one CSV per repo folder name, written on this Mac.
    # The writer's rule is ASCII only (JS \w), so re.ASCII. The config root follows XDG_CONFIG_HOME, like the writer.
    name = re.sub(r"[^\w.-]", "_", Path(repo_dir).name, flags=re.ASCII)
    root = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return root / "ponytail" / "band" / (name + ".csv")


def read_spend(path):
    """Cost per task from the Ponytail ledger (its band CSV). A missing file is an empty section, never an error.

    Columns read: name (fallback key), cost_usd, tokens_total, agent_minutes, reuse_pct (percent), tests (a label such as
    "3 passed", "1 failed", "stale" or "not run"). Header as the upstream writer prints it.
    """
    path = Path(path)
    if not path.exists():
        return {"rows": [], "note": "no ledger"}
    rows = []
    # shortcut: one bad number in any cell drops the whole Spend card (gather catches it); add a per-row skip when a real ledger has bad rows.
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "task": (r.get("name") or r.get("key") or "").strip(),
                "cost": float(r.get("cost_usd") or 0),
                "tokens": float(r.get("tokens_total") or 0),
                "agent_minutes": float(r.get("agent_minutes") or 0),
                "reuse": float(r.get("reuse_pct") or 0),
                "tests": (r.get("tests") or "").strip() or "not run",
            })
    totals = {k: sum(r[k] for r in rows) for k in ("cost", "tokens", "agent_minutes")}
    return {"rows": rows, "totals": totals}


def read_roadmap_link(run):
    """The live roadmap is ROADMAP.md on the `roadmap` branch (roadmap.yml). 404 on the branch is "no branch", not an error."""
    url = json.loads(run(["repo", "view", "--json", "url"]))["url"]
    try:
        run(["api", "repos/{owner}/{repo}/branches/roadmap", "--silent"])
    except DeskError as e:
        if "404" in str(e) or "Not Found" in str(e):
            return {"state": "no_branch"}
        raise
    return {"state": "link", "url": url + "/blob/roadmap/ROADMAP.md"}


def gather(run, repo_dir, now, band=None):
    errors, waiting, roadmap, roadmap_link = [], [], [], {"state": "unknown"}
    try:
        spend = read_spend(band or default_band_path(repo_dir))
    except (ValueError, OSError, csv.Error) as e:
        spend = {"rows": [], "note": "ledger unreadable: %s" % e}
    try:
        prs = json.loads(run(["pr", "list", "--state", "open", "--limit", "50",
                              "--json", "number,title,isDraft,url,statusCheckRollup,files,baseRefName,headRefName,body,reviewDecision"]))
        globs, mode = protected_globs(repo_dir), read_switches(repo_dir)["mode"]
        waiting = [{"number": p["number"], "title": p["title"], "draft": p["isDraft"], "url": p["url"],
                    "checks": checks_summary(p.get("statusCheckRollup")), "reason": why}
                   for p in prs for why in [owner_reason(p, globs, mode)] if why]
    except DeskError as e:
        errors.append(str(e))
    except (ValueError, KeyError):
        errors.append("gh returned bad JSON for pull requests")
    try:
        issues = json.loads(run(["issue", "list", "--state", "open", "--limit", "20", "--json", "number,title,labels"]))
        roadmap = [{"number": i["number"], "title": i["title"], "labels": [l["name"] for l in i.get("labels", [])]}
                   for i in issues]
    except DeskError as e:
        errors.append(str(e))
    except (ValueError, KeyError):
        errors.append("gh returned bad JSON for issues")
    feats = read_features(repo_dir)
    roadmap_on = next((i["on"] for g in feats["groups"] for i in g["items"] if i["id"] == "roadmap"), True)
    try:
        roadmap_link = read_roadmap_link(run) if roadmap_on else {"state": "off"}   # story #427: the card says "Roadmap is off", no link
    except DeskError as e:
        errors.append(str(e))
    except (ValueError, KeyError):
        errors.append("gh returned bad JSON for the repository")
    return {
        "as_of": datetime.fromtimestamp(now, timezone.utc).isoformat(timespec="seconds"),
        "waiting": waiting,
        "decided": read_trace(repo_dir),
        "switches": read_switches(repo_dir),
        "roadmap": roadmap,
        "roadmap_link": roadmap_link,
        "features": feats,
        "spend": spend,
        "error": "; ".join(errors) or None,
        "stale": False,
    }


class Desk:
    def __init__(self, repo_dir, runner=None, clock=None, ttl=TTL_SECONDS, band=None):
        self.repo_dir = repo_dir
        self.band = band
        self.run = runner or gh_runner(repo_dir)
        self.clock = clock or time.time
        self.ttl = ttl
        self.lock = threading.Lock()
        self.payload = None      # last answer, fresh or not
        self.good = None         # last answer with no error
        self.at = 0.0
        self.status = 503        # no answer yet; set by every gather

    def state(self):
        """Return (http_status, payload). Never raises on gh failure."""
        with self.lock:
            now = self.clock()
            if self.payload is not None and now - self.at < self.ttl:
                return self.status, self.payload
            fresh = gather(self.run, self.repo_dir, now, self.band)
            self.at = now
            if fresh["error"] is None:
                self.good = fresh
                self.payload, self.status = fresh, 200
            elif self.good is not None:
                self.payload = dict(self.good, stale=True, error=fresh["error"], as_of=fresh["as_of"])
                self.status = 200
            else:
                self.payload, self.status = fresh, 503
            return self.status, self.payload


def host_allowed(header, port):
    return header in ("localhost:%d" % port, "127.0.0.1:%d" % port)


def origin_allowed(header, port):
    # A page from another site sends its own Origin; only this server's own origin, or no Origin at all, passes.
    return header is None or header in ("http://localhost:%d" % port, "http://127.0.0.1:%d" % port)


def make_server(port, desk, html_path=None):
    html = (html_path or HERE / "desk" / "index.html").read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, ctype, body):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            bound = self.server.server_address[1]
            if not host_allowed(self.headers.get("Host", ""), bound):
                return self._send(403, "text/plain; charset=utf-8", b"forbidden: bad Host header\n")
            path = self.path.split("?", 1)[0]
            if path == "/":
                return self._send(200, "text/html; charset=utf-8", html)
            if path == "/api/state.json":
                if not origin_allowed(self.headers.get("Origin"), bound):
                    return self._send(403, "text/plain; charset=utf-8", b"forbidden: cross-origin request\n")
                status, payload = desk.state()
                return self._send(status, "application/json; charset=utf-8",
                                  json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            self._send(404, "text/plain; charset=utf-8", b"not found\n")

        def log_message(self, fmt, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def parse_args(argv=None):
    """The project to read is --repo (default: the folder you run it from), never the kit folder."""
    ap = argparse.ArgumentParser(description="ShipQuick Desk on 127.0.0.1")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--repo", default=".", help="the project folder to read (default: the current folder)")
    ap.add_argument("--band", default=None, help="the Ponytail ledger CSV (default: ~/.config/ponytail/band/<project>.csv)")
    args = ap.parse_args(argv)
    args.repo = Path(args.repo).resolve()
    return args


def main(argv=None):
    args = parse_args(argv)
    server = make_server(args.port, Desk(args.repo, band=Path(args.band) if args.band else None))
    print("ShipQuick Desk on http://127.0.0.1:%d/ (Ctrl-C to stop)" % args.port, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
