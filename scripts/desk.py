"""ShipQuick Desk, Option B (epic #91): one stdlib server on 127.0.0.1 that asks gh on request.

Serves the page at / and the state at /api/state.json. The state is cached for 60 s.
Only read-only gh calls. Nothing is written to disk, no token is read.
Usage: python3 scripts/desk.py [--port 8765]
"""
import argparse
import csv
import json
import subprocess
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
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


def default_band_path(repo_dir):
    # The Ponytail ledger for this project: one CSV per repo folder name, written on this Mac.
    return Path.home() / ".config" / "ponytail" / "band" / (Path(repo_dir).name + ".csv")


def read_spend(path):
    """Cost per task from the Ponytail ledger. A missing file is an empty section, never an error.

    Columns: task, cost_usd, tokens, agent_minutes, reuse, tests_per_task (an assumption: the ledger header was not found on this Mac).
    """
    path = Path(path)
    if not path.exists():
        return {"rows": [], "note": "no ledger"}
    rows = []
    # shortcut: a bad number in one cell stops the read (float raises), no per-row skip; add the skip when the ledger has bad rows.
    with path.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append({
                "task": (r.get("task") or "").strip(),
                "cost": float(r.get("cost_usd") or 0),
                "tokens": float(r.get("tokens") or 0),
                "agent_minutes": float(r.get("agent_minutes") or 0),
                "reuse": float(r.get("reuse") or 0),
                "tests_per_task": float(r.get("tests_per_task") or 0),
            })
    totals = {k: sum(r[k] for r in rows) for k in ("cost", "tokens", "agent_minutes")}
    return {"rows": rows, "totals": totals}


def gather(run, repo_dir, now, band=None):
    errors, waiting, roadmap = [], [], []
    try:
        prs = json.loads(run(["pr", "list", "--state", "open", "--limit", "50",
                              "--json", "number,title,isDraft,url,statusCheckRollup"]))
        waiting = [{"number": p["number"], "title": p["title"], "draft": p["isDraft"], "url": p["url"],
                    "checks": checks_summary(p.get("statusCheckRollup"))} for p in prs]
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
    return {
        "as_of": datetime.fromtimestamp(now, timezone.utc).isoformat(timespec="seconds"),
        "waiting": waiting,
        "decided": read_trace(repo_dir),
        "switches": read_switches(repo_dir),
        "roadmap": roadmap,
        "spend": read_spend(band or default_band_path(repo_dir)),
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
