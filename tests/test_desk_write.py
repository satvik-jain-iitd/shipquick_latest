"""Story #428 (D2, epic #91): the Desk's one write route. A switch click POSTs {id, on}; the server checks the Host, the Origin
and a per-start token, refuses a locked id, then runs `features.sh set` in a throwaway worktree off the base branch, commits on a
new branch, pushes it and opens the PR. The owner's checkout is never touched. Real git with a bare origin, a fake gh."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import desk  # noqa: E402
from test_desk import ServerCase  # noqa: E402
from test_desk_owner_cards import runner  # noqa: E402


class Route(ServerCase):
    def start_with(self, proposer, open_prs=()):
        self.proposals = []

        def fake(feature, on):
            self.proposals.append((feature, on))
            return proposer(feature, on)
        self.start(runner([{"number": n} for n in open_prs]))
        self.desk.proposer = fake

    def post(self, body, token="auto", origin="auto", host=None, raw=None):
        url = "http://127.0.0.1:%d/api/features" % self.port
        data = raw if raw is not None else json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Host", host if host is not None else "127.0.0.1:%d" % self.port)
        req.add_header("Content-Type", "application/json")
        if origin == "auto":
            origin = "http://127.0.0.1:%d" % self.port
        if origin is not None:
            req.add_header("Origin", origin)
        if token == "auto":
            token = self.desk.token
        if token is not None:
            req.add_header("X-Desk-Token", token)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode() or "{}") if e.headers.get("Content-Type", "").startswith("application/json") else {}

    def test_a_good_request_proposes_and_answers_with_the_pr(self):
        self.start_with(lambda f, on: {"pr": 77, "url": "https://example.test/pull/77"})
        code, body = self.post({"id": "lanes", "on": False})
        self.assertEqual((code, body["pr"]), (200, 77))
        self.assertEqual(self.proposals, [("lanes", False)])

    def test_a_cross_origin_post_is_403_and_nothing_runs(self):
        self.start_with(lambda f, on: {"pr": 1, "url": "u"})
        for origin in ("https://evil.example", "http://127.0.0.1:1", None):
            self.assertEqual(self.post({"id": "lanes", "on": False}, origin=origin)[0], 403, origin)
        self.assertEqual(self.proposals, [])

    def test_a_missing_or_wrong_token_is_403_and_nothing_runs(self):
        self.start_with(lambda f, on: {"pr": 1, "url": "u"})
        for tok in (None, "", "wrong"):
            self.assertEqual(self.post({"id": "lanes", "on": False}, token=tok)[0], 403, tok)
        self.assertEqual(self.proposals, [])

    def test_a_bad_host_is_403(self):
        self.start_with(lambda f, on: {"pr": 1, "url": "u"})
        self.assertEqual(self.post({"id": "lanes", "on": False}, host="evil.example")[0], 403)

    def test_a_locked_feature_is_refused_and_nothing_runs(self):
        self.start_with(lambda f, on: {"pr": 1, "url": "u"})
        for fid in ("gate", "adoption"):
            code, body = self.post({"id": fid, "on": False})
            self.assertEqual(code, 409, fid)
            self.assertIn("locked", body["error"])
        self.assertEqual(self.proposals, [])

    def test_bad_bodies_are_400(self):
        self.start_with(lambda f, on: {"pr": 1, "url": "u"})
        for body in ({"id": "nosuch", "on": True}, {"id": "lanes", "on": "yes"}, {"on": True}, {"id": 5, "on": True}):
            self.assertEqual(self.post(body)[0], 400, body)
        self.assertEqual(self.post(None, raw=b"{oops")[0], 400)
        self.assertEqual(self.post(None, raw=b"x" * 5000)[0], 400)
        self.assertEqual(self.proposals, [])

    def test_a_failed_proposal_is_a_502_with_the_reason(self):
        def boom(f, on):
            raise desk.DeskError("git push failed: no network")
        self.start_with(boom)
        code, body = self.post({"id": "lanes", "on": False})
        self.assertEqual(code, 502)
        self.assertIn("no network", body["error"])

    def test_the_served_page_carries_the_token_and_the_token_is_not_in_the_state(self):
        self.start_with(lambda f, on: {"pr": 1, "url": "u"})
        page = self.get("/")[2]
        self.assertIn('content="%s"' % self.desk.token, page)
        self.assertNotIn(self.desk.token, self.get("/api/state.json")[2])

    def test_a_pending_proposal_shows_in_the_features_until_its_pr_is_gone(self):
        prs = [77]
        self.start_with(lambda f, on: {"pr": 77, "url": "https://example.test/pull/77"}, open_prs=prs)
        self.post({"id": "lanes", "on": False})
        st = json.loads(self.get("/api/state.json")[2])
        self.assertEqual(st["features"]["pending"]["lanes"], {"on": False, "pr": 77, "url": "https://example.test/pull/77"})
        self.desk.run = runner([])   # the PR is merged or closed: it is no longer open
        self.clock.now += 61
        st = json.loads(self.get("/api/state.json")[2])
        self.assertEqual(st["features"]["pending"], {})


def sh(cwd, *a, **kw):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.test", *a], cwd=cwd, capture_output=True, text=True, check=True, **kw)


class RealProposal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = Path(self.tmp.name)
        self.bare = t / "origin.git"
        sh(t, "init", "-q", "--bare", "-b", "dev", str(self.bare))
        self.repo = t / "proj"
        sh(t, "clone", "-q", str(self.bare), str(self.repo))
        sh(self.repo, "checkout", "-q", "-b", "dev")
        (self.repo / "README.md").write_text("x\n", encoding="utf-8")
        sh(self.repo, "add", "-A")
        sh(self.repo, "commit", "-q", "-m", "base")
        sh(self.repo, "push", "-q", "origin", "dev")
        self.bin = t / "bin"
        self.bin.mkdir()
        self.log = t / "gh.log"
        g = self.bin / "gh"
        g.write_text('#!/usr/bin/env bash\necho "$@" >> %s\nif [ "$1 $2" = "pr create" ]; then echo https://example.test/pull/55; fi\nif [ "$1 $2" = "api user" ]; then echo "${FAKE_GH_USER-klickbae8yt-star}"; fi\n' % self.log, encoding="utf-8")
        g.chmod(0o755)
        self.old = os.environ["PATH"]
        os.environ["PATH"] = "%s:%s" % (self.bin, self.old)
        self.addCleanup(lambda: os.environ.__setitem__("PATH", self.old))
        self.addCleanup(self.tmp.cleanup)

    def test_it_changes_one_file_on_a_new_branch_and_leaves_the_checkout_alone(self):
        before_branch = sh(self.repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        out = desk.propose_feature(self.repo, "lanes", False, base="dev")
        self.assertEqual(out["pr"], 55)
        self.assertEqual(sh(self.repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(), before_branch)
        self.assertFalse((self.repo / ".shipquick").exists(), "the owner's checkout must not change")
        branches = sh(self.bare, "branch", "--list", "chore/feature-*").stdout.split()
        self.assertEqual(len(branches), 1)
        changed = sh(self.bare, "diff", "--name-only", "dev", branches[0]).stdout.split()
        self.assertEqual(changed, [".shipquick/features.json"])
        data = json.loads(sh(self.bare, "show", "%s:.shipquick/features.json" % branches[0]).stdout)
        self.assertEqual(data["features"], {"lanes": {"on": False}})
        self.assertIn("pr create", self.log.read_text(encoding="utf-8"))
        self.assertEqual(sh(self.repo, "worktree", "list").stdout.count("\n"), 1, "the throwaway worktree must be removed")

    def test_a_feature_already_at_that_value_on_the_base_opens_no_pr(self):
        out = desk.propose_feature(self.repo, "roadmap", True, base="dev")   # default on, nothing to change
        self.assertEqual(out, {"unchanged": True})
        self.assertFalse(self.log.exists())

    def test_a_locked_feature_raises_and_nothing_is_pushed(self):
        with self.assertRaises(desk.DeskError):
            desk.propose_feature(self.repo, "gate", False, base="dev")
        self.assertEqual(sh(self.bare, "branch", "--list", "chore/feature-*").stdout.strip(), "")

    def local_branches(self):
        return sh(self.repo, "branch", "--list", "chore/feature-*").stdout.strip()

    def test_s456_no_local_branch_is_left_after_a_good_proposal_an_unchanged_one_or_an_error(self):
        desk.propose_feature(self.repo, "lanes", False, base="dev")
        self.assertEqual(self.local_branches(), "")
        desk.propose_feature(self.repo, "roadmap", True, base="dev")
        self.assertEqual(self.local_branches(), "")
        with self.assertRaises(desk.DeskError):
            desk.propose_feature(self.repo, "gate", False, base="dev")
        self.assertEqual(self.local_branches(), "")

    def test_s456_the_pr_body_names_the_account_that_opens_it(self):
        desk.propose_feature(self.repo, "lanes", False, base="dev")
        self.assertIn("Opened by `klickbae8yt-star`", self.log.read_text(encoding="utf-8"))

    def commit_roles(self):
        (self.repo / ".shipquick").mkdir()
        (self.repo / ".shipquick" / "roles.yml").write_text("coder:\n  - klickbae8yt-star\nreviewer:\n  - satvik-jain-iitd\nowner: satvik-jain-iitd\n", encoding="utf-8")
        sh(self.repo, "add", "-A")
        sh(self.repo, "commit", "-q", "-m", "roles")
        sh(self.repo, "push", "-q", "origin", "dev")

    def test_s456_the_review_account_is_refused_before_anything_is_pushed(self):
        self.commit_roles()
        os.environ["FAKE_GH_USER"] = "satvik-jain-iitd"
        self.addCleanup(os.environ.pop, "FAKE_GH_USER", None)
        with self.assertRaises(desk.DeskError) as e:
            desk.propose_feature(self.repo, "lanes", False, base="dev")
        self.assertIn("satvik-jain-iitd", str(e.exception))
        self.assertIn("SHIPQUICK_BUILD_USER", str(e.exception))
        self.assertEqual(sh(self.bare, "branch", "--list", "chore/feature-*").stdout.strip(), "")
        self.assertNotIn("pr create", self.log.read_text(encoding="utf-8"))
        self.assertEqual(self.local_branches(), "")

    def test_s456_a_coder_account_is_accepted_when_roles_exist(self):
        self.commit_roles()
        self.assertEqual(desk.propose_feature(self.repo, "lanes", False, base="dev")["pr"], 55)

    def test_s456_an_account_gh_cannot_name_is_refused(self):
        os.environ["FAKE_GH_USER"] = ""
        self.addCleanup(os.environ.pop, "FAKE_GH_USER", None)
        with self.assertRaises(desk.DeskError):
            desk.propose_feature(self.repo, "lanes", False, base="dev")
        self.assertEqual(sh(self.bare, "branch", "--list", "chore/feature-*").stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
