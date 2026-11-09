"""ShipQuick Desk, Option B (epic #91): Host check, state shape, 60 s cache, gh failure path. Stdlib unittest only."""
import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import desk  # noqa: E402

PRS = json.dumps([{
    "number": 101, "title": "Add the Desk", "isDraft": False, "url": "https://example.test/101",
    "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
}])
ISSUES = json.dumps([{"number": 91, "title": "ShipQuick Desk", "labels": [{"name": "epic"}]}])


def fake_runner(calls, fail=None):
    def run(args):
        calls.append(args)
        if fail:
            raise desk.DeskError(fail)
        if args[:2] == ["pr", "list"]:
            return PRS
        if args[:2] == ["issue", "list"]:
            return ISSUES
        raise AssertionError("unexpected gh call: %r" % (args,))
    return run


class FakeClock:
    def __init__(self, now=1_000_000.0):
        self.now = now

    def __call__(self):
        return self.now


class ServerCase(unittest.TestCase):
    def start(self, runner):
        self.clock = FakeClock()
        self.desk = desk.Desk(ROOT, runner=runner, clock=self.clock)
        self.server = desk.make_server(0, self.desk)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def get(self, path, host=None):
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, path))
        req.add_header("Host", host if host is not None else "127.0.0.1:%d" % self.port)
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, r.headers.get("Content-Type", ""), r.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Content-Type", ""), e.read().decode()


class HostCheck(ServerCase):
    def test_bad_host_gets_403_on_every_path(self):
        self.start(fake_runner([]))
        for path in ("/", "/api/state.json"):
            code, _, _ = self.get(path, host="evil.example")
            self.assertEqual(code, 403, path)

    def test_host_check_accepts_only_localhost_with_the_port(self):
        self.assertTrue(desk.host_allowed("localhost:8765", 8765))
        self.assertTrue(desk.host_allowed("127.0.0.1:8765", 8765))
        self.assertFalse(desk.host_allowed("localhost.evil.example:8765", 8765))
        self.assertFalse(desk.host_allowed("evil.example", 8765))
        self.assertFalse(desk.host_allowed("127.0.0.1:9999", 8765))


class StateShape(ServerCase):
    def test_state_json_has_the_sections_and_no_error(self):
        self.start(fake_runner([]))
        code, ctype, body = self.get("/api/state.json")
        self.assertEqual(code, 200)
        self.assertIn("application/json", ctype)
        data = json.loads(body)
        for key in ("as_of", "waiting", "decided", "switches", "roadmap", "error", "stale"):
            self.assertIn(key, data)
        self.assertIsNone(data["error"])
        self.assertFalse(data["stale"])
        self.assertEqual(data["waiting"][0]["number"], 101)
        self.assertEqual(data["waiting"][0]["checks"], "passing")
        self.assertEqual(data["roadmap"][0]["title"], "ShipQuick Desk")

    def test_root_serves_the_page(self):
        self.start(fake_runner([]))
        code, ctype, body = self.get("/")
        self.assertEqual(code, 200)
        self.assertIn("text/html", ctype)
        self.assertIn("ShipQuick Desk", body)
        self.assertIn("/api/state.json", body)
        self.assertNotIn("<script src=", body)


class Cache(ServerCase):
    def test_second_request_within_60_seconds_is_the_same_payload_without_gh(self):
        calls = []
        self.start(fake_runner(calls))
        first = json.loads(self.get("/api/state.json")[2])
        gh_calls = len(calls)
        self.clock.now += 30
        second = json.loads(self.get("/api/state.json")[2])
        self.assertEqual(first, second)
        self.assertEqual(len(calls), gh_calls)

    def test_after_60_seconds_gh_runs_again(self):
        calls = []
        self.start(fake_runner(calls))
        self.get("/api/state.json")
        gh_calls = len(calls)
        self.clock.now += 61
        self.get("/api/state.json")
        self.assertGreater(len(calls), gh_calls)


class GhFailure(unittest.TestCase):
    def test_gh_failure_returns_an_error_field_not_an_exception(self):
        clock = FakeClock()
        d = desk.Desk(ROOT, runner=fake_runner([], fail="gh is logged out: run gh auth login"), clock=clock)
        status, payload = d.state()
        self.assertEqual(status, 503)
        self.assertIn("gh is logged out", payload["error"])
        self.assertEqual(payload["waiting"], [])

    def test_failure_after_a_good_answer_returns_the_last_good_one_marked_stale(self):
        clock = FakeClock()
        good = fake_runner([])
        bad = fake_runner([], fail="gh timed out after 20 s")
        runner = {"fn": good}
        d = desk.Desk(ROOT, runner=lambda args: runner["fn"](args), clock=clock)
        status, first = d.state()
        self.assertEqual(status, 200)
        runner["fn"] = bad
        clock.now += 61
        status, payload = d.state()
        self.assertEqual(status, 200)
        self.assertTrue(payload["stale"])
        self.assertIn("timed out", payload["error"])
        self.assertEqual(payload["waiting"], first["waiting"])


class ParseArgs(unittest.TestCase):
    def test_repo_defaults_to_the_current_folder_and_takes_a_child_path(self):
        import os
        import tempfile
        here = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            try:
                os.chdir(tmp)
                self.assertEqual(desk.parse_args([]).repo, Path(tmp).resolve())
            finally:
                os.chdir(here)
            self.assertEqual(desk.parse_args(["--repo", tmp]).repo, Path(tmp).resolve())
            self.assertNotEqual(desk.parse_args(["--repo", tmp]).repo, desk.HERE.parent.resolve())


if __name__ == "__main__":
    unittest.main()
