"""ShipQuick Desk, Option B (epic #91): one stdlib server on 127.0.0.1 that asks gh on request.

Serves the page at / and the state at /api/state.json. The state is cached for 60 s.
Reads use read-only gh calls. The one write (story #428) is POST /api/features: same origin plus a per-start token, then
`features.sh set` in a throwaway worktree off the base branch, a new branch, and a PR for the owner's merge. Nothing else is written.
Usage: python3 scripts/desk.py [--port 8765]
"""
import argparse
import csv
import fnmatch
import hmac
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
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
MAX_BODY = 1024


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


def propose_feature(repo_dir, fid, on, base="dev"):
    """Open a PR that sets one feature. Works in a throwaway worktree off origin/<base>: the owner's checkout never changes.
    Returns {"pr", "url"}, or {"unchanged": True} when the base already has that value. Any failure raises DeskError."""
    repo = Path(repo_dir)

    def git(*a, cwd=None):
        try:
            p = subprocess.run(["git", *a], cwd=cwd or repo, capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise DeskError("git failed: %s" % e)
        if p.returncode:
            raise DeskError("git %s failed: %s" % (a[0], (p.stderr or p.stdout).strip() or "exit %d" % p.returncode))
        return p.stdout

    word = "on" if on else "off"
    git("fetch", "-q", "origin", base)
    tmp = tempfile.mkdtemp(prefix="desk-feature-")
    wt = Path(tmp) / "wt"
    branch = "chore/feature-%s-%s-%d" % (fid, word, int(time.time()))
    try:
        git("worktree", "add", "-q", "-b", branch, str(wt), "origin/" + base)
        try:
            cur = features.read(str(wt))["features"].get(fid)
        except features.FeaturesError as e:
            raise DeskError("the features file on %s is broken: %s" % (base, e))
        if cur is None:
            raise DeskError("unknown feature `%s`" % fid)
        if cur.get("locked"):
            raise DeskError("`%s` is locked: it guards every other feature and always stays on" % fid)
        if cur["on"] == on:
            return {"unchanged": True}
        p = subprocess.run(["bash", str(HERE / "features.sh"), "set", fid, word], cwd=wt, capture_output=True, text=True, timeout=30)
        if p.returncode:
            raise DeskError("features.sh set failed: %s" % (p.stderr.strip() or "exit %d" % p.returncode))
        git("add", ".shipquick/features.json", cwd=wt)
        ident = []
        if subprocess.run(["git", "config", "user.email"], cwd=repo, capture_output=True, text=True).stdout.strip() == "":
            ident = ["-c", "user.name=ShipQuick Desk", "-c", "user.email=desk@localhost"]
        title = "chore(features): turn %s %s" % (fid, word)
        git(*ident, "commit", "-q", "-m", title + "\n\nProposed from the ShipQuick Desk. `.shipquick/features.json` is a protected path: the owner merges.", cwd=wt)
        git("push", "-q", "origin", branch, cwd=wt)
        env = dict(os.environ)
        build = os.environ.get("SHIPQUICK_BUILD_USER")
        if build:
            t = subprocess.run(["gh", "auth", "token", "--user", build], capture_output=True, text=True)
            if t.returncode == 0 and t.stdout.strip():
                env["GH_TOKEN"] = t.stdout.strip()
        body = "Proposed from the ShipQuick Desk: set `%s` to `%s` in `.shipquick/features.json`.\n\nThis is a protected path: the owner merges it.\n" % (fid, word)
        try:
            c = subprocess.run(["gh", "pr", "create", "--base", base, "--head", branch, "--title", title, "--body", body],
                               cwd=repo, capture_output=True, text=True, timeout=GH_TIMEOUT * 2, env=env)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise DeskError("gh pr create failed: %s" % e)
        if c.returncode:
            raise DeskError("gh pr create failed: %s" % (c.stderr.strip() or "exit %d" % c.returncode))
        url = c.stdout.strip().splitlines()[-1] if c.stdout.strip() else ""
        m = re.search(r"/pull/(\d+)", url)
        if not m:
            raise DeskError("gh pr create gave no pull request link: %r" % c.stdout.strip())
        return {"pr": int(m.group(1)), "url": url}
    finally:
        subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=repo, capture_output=True)
        shutil.rmtree(tmp, ignore_errors=True)


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


def gather(run, repo_dir, now, band=None, pending=None):
    errors, waiting, roadmap, roadmap_link = [], [], [], {"state": "unknown"}
    open_nums = None   # None = the PR list failed: keep every pending switch, do not guess
    try:
        spend = read_spend(band or default_band_path(repo_dir))
    except (ValueError, OSError, csv.Error) as e:
        spend = {"rows": [], "note": "ledger unreadable: %s" % e}
    try:
        prs = json.loads(run(["pr", "list", "--state", "open", "--limit", "50",
                              "--json", "number,title,isDraft,url,statusCheckRollup,files,baseRefName,headRefName,body,reviewDecision"]))
        open_nums = {p["number"] for p in prs}
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
    now_vals = {i["id"]: i["on"] for g in feats["groups"] for i in g["items"]}
    # a switch the owner asked for waits on its PR: drop it once the PR is no longer open or the file already says so
    feats["pending"] = {k: v for k, v in (pending or {}).items() if (open_nums is None or v["pr"] in open_nums) and now_vals.get(k) != v["on"]}
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
        self.token = secrets.token_urlsafe(24)   # per start: the page carries it, a post without it is refused
        self.pending = {}        # {id: {on, pr, url}} proposals still waiting on their PR
        self.proposer = lambda fid, on: propose_feature(self.repo_dir, fid, on)

    def remember(self, fid, on, out):
        """A proposal went out: show it as waiting and refresh on the next read."""
        with self.lock:
            if "pr" in out:
                self.pending[fid] = {"on": on, "pr": out["pr"], "url": out["url"]}
            self.payload = None

    def state(self):
        """Return (http_status, payload). Never raises on gh failure."""
        with self.lock:
            now = self.clock()
            if self.payload is not None and now - self.at < self.ttl:
                return self.status, self.payload
            fresh = gather(self.run, self.repo_dir, now, self.band, self.pending)
            self.pending = dict(fresh["features"]["pending"])
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
                return self._send(200, "text/html; charset=utf-8", html.replace(b"__DESK_TOKEN__", desk.token.encode()))
            if path == "/api/state.json":
                if not origin_allowed(self.headers.get("Origin"), bound):
                    return self._send(403, "text/plain; charset=utf-8", b"forbidden: cross-origin request\n")
                status, payload = desk.state()
                return self._send(status, "application/json; charset=utf-8",
                                  json.dumps(payload, ensure_ascii=False).encode("utf-8"))
            self._send(404, "text/plain; charset=utf-8", b"not found\n")

        def _json(self, code, obj):
            self._send(code, "application/json; charset=utf-8", json.dumps(obj, ensure_ascii=False).encode("utf-8"))

        def do_POST(self):
            bound = self.server.server_address[1]
            if not host_allowed(self.headers.get("Host", ""), bound):
                return self._json(403, {"error": "forbidden: bad Host header"})
            if self.path.split("?", 1)[0] != "/api/features":
                return self._json(404, {"error": "not found"})
            origin = self.headers.get("Origin")
            if origin is None or not origin_allowed(origin, bound):   # a write needs an Origin: no Origin is not "same site"
                return self._json(403, {"error": "forbidden: cross-origin request"})
            if not hmac.compare_digest(self.headers.get("X-Desk-Token", "").encode(), desk.token.encode()):
                return self._json(403, {"error": "forbidden: missing or wrong token"})
            try:
                n = int(self.headers.get("Content-Length", ""))
            except ValueError:
                return self._json(400, {"error": "bad Content-Length"})
            if n < 0 or n > MAX_BODY:
                return self._json(400, {"error": "body too large"})
            try:
                body = json.loads(self.rfile.read(n).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                return self._json(400, {"error": "body is not JSON"})
            fid, on = (body.get("id"), body.get("on")) if isinstance(body, dict) else (None, None)
            if not isinstance(fid, str) or not isinstance(on, bool):
                return self._json(400, {"error": 'send {"id": "<feature>", "on": true or false}'})
            try:
                row = features.read(desk.repo_dir)["features"].get(fid)
            except features.FeaturesError as e:
                return self._json(502, {"error": "the features file is broken: %s" % e})
            if row is None:
                return self._json(400, {"error": "unknown feature `%s`" % fid})
            if row.get("locked"):
                return self._json(409, {"error": "`%s` is locked: it always stays on" % fid})
            try:
                out = desk.proposer(fid, on)
            except DeskError as e:
                return self._json(502, {"error": str(e)})
            except Exception as e:   # never a fake success
                return self._json(502, {"error": "unexpected %s: %s" % (type(e).__name__, e)})
            desk.remember(fid, on, out)
            return self._json(200, out)

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
