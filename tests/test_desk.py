"""ShipQuick Desk, Option B (epic #91): Host check, state shape, 60 s cache, gh failure path. Stdlib unittest only."""
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest import mock

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
    def start(self, runner, band=None):
        self.clock = FakeClock()
        no_ledger = Path(tempfile.gettempdir()) / "desk-test-no-such-band.csv"
        self.desk = desk.Desk(ROOT, runner=runner, clock=self.clock, band=band or no_ledger)
        self.server = desk.make_server(0, self.desk)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def get(self, path, host=None, origin=None):
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (self.port, path))
        req.add_header("Host", host if host is not None else "127.0.0.1:%d" % self.port)
        if origin is not None:
            req.add_header("Origin", origin)
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
        for key in ("as_of", "waiting", "decided", "switches", "roadmap", "spend", "error", "stale"):
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


LEDGER = (
    "key,started,project,name,cost_usd,turns,agent_minutes,tokens_total,tokens_output,reuse_pct,reused,new,"
    "callers_open,tests,level,model\n"
    "abc,2026-11-10 14:00,shipquick_latest,A8 desk spend,0.42,12,14.0,120000,8000,50,2,2,0,3 passed,full,claude-haiku-5-5\n"
    "def,2026-11-10 15:00,shipquick_latest,A6 sheets,1.10,30,31.0,300000,20000,25,1,3,1,1 failed,full,claude-haiku-5-5\n"
)


class SpendLedger(unittest.TestCase):
    def test_missing_csv_gives_an_empty_spend_with_a_note(self):
        spend = desk.read_spend(Path(tempfile.gettempdir()) / "desk-test-no-such-band.csv")
        self.assertEqual(spend, {"rows": [], "note": "no ledger"})

    def test_real_ledger_header_is_read_row_by_row_with_totals(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.csv"
            path.write_text(LEDGER, encoding="utf-8")
            spend = desk.read_spend(path)
        self.assertEqual(len(spend["rows"]), 2)
        self.assertEqual(spend["rows"][0], {"task": "A8 desk spend", "cost": 0.42, "tokens": 120000.0,
                                            "agent_minutes": 14.0, "reuse": 50.0, "tests": "3 passed"})
        self.assertEqual(spend["rows"][1]["tests"], "1 failed")
        self.assertAlmostEqual(spend["totals"]["cost"], 1.52)
        self.assertEqual(spend["totals"]["tokens"], 420000.0)
        self.assertEqual(spend["totals"]["agent_minutes"], 45.0)
        self.assertNotIn("note", spend)

    def test_row_without_a_name_uses_the_key_as_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.csv"
            path.write_text(LEDGER.replace("abc,2026-11-10 14:00,shipquick_latest,A8 desk spend",
                                           "abc,2026-11-10 14:00,shipquick_latest,"), encoding="utf-8")
            spend = desk.read_spend(path)
        self.assertEqual(spend["rows"][0]["task"], "abc")

    def test_band_path_uses_the_same_name_rule_as_the_ponytail_writer(self):
        self.assertEqual(desk.default_band_path("/x/my repo (1)").name, "my_repo__1_.csv")
        self.assertEqual(desk.default_band_path("/x/shipquick_latest").name, "shipquick_latest.csv")

    def test_band_path_follows_xdg_config_home_like_the_writer(self):
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/tmp/xdgtest"}):
            self.assertEqual(desk.default_band_path("/x/shipquick_latest"),
                             Path("/tmp/xdgtest/ponytail/band/shipquick_latest.csv"))

    def test_band_name_rule_is_ascii_like_the_javascript_writer(self):
        self.assertEqual(desk.default_band_path("/x/caf\u00e9").name, "caf_.csv")


class SpendInServer(ServerCase):
    def test_state_json_carries_the_fixture_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            band = Path(tmp) / "x.csv"
            band.write_text(LEDGER, encoding="utf-8")
            self.start(fake_runner([]), band=band)
            data = json.loads(self.get("/api/state.json")[2])
        self.assertIsNone(data["error"])
        self.assertEqual([r["task"] for r in data["spend"]["rows"]], ["A8 desk spend", "A6 sheets"])

    def test_state_json_without_a_ledger_has_no_error(self):
        self.start(fake_runner([]))
        data = json.loads(self.get("/api/state.json")[2])
        self.assertEqual(data["spend"], {"rows": [], "note": "no ledger"})
        self.assertIsNone(data["error"])

    def test_unreadable_ledger_keeps_the_other_sections(self):
        bad = LEDGER.replace("0.42", "n/a")
        with tempfile.TemporaryDirectory() as tmp:
            band = Path(tmp) / "x.csv"
            band.write_text(bad, encoding="utf-8")
            self.start(fake_runner([]), band=band)
            code, _, body = self.get("/api/state.json")
        self.assertEqual(code, 200)
        data = json.loads(body)
        self.assertEqual(data["spend"]["rows"], [])
        self.assertIn("ledger unreadable", data["spend"]["note"])
        self.assertEqual(data["waiting"][0]["number"], 101)
        self.assertEqual(data["roadmap"][0]["title"], "ShipQuick Desk")

    def test_page_has_a_spend_section(self):
        self.start(fake_runner([]))
        self.assertIn('id="spend"', self.get("/")[2])


class OriginCheck(ServerCase):
    def test_origin_allowed_takes_only_the_own_origin_or_none(self):
        self.assertTrue(desk.origin_allowed(None, 8765))
        self.assertTrue(desk.origin_allowed("http://localhost:8765", 8765))
        self.assertTrue(desk.origin_allowed("http://127.0.0.1:8765", 8765))
        self.assertFalse(desk.origin_allowed("http://localhost:9999", 8765))
        self.assertFalse(desk.origin_allowed("https://evil.example", 8765))
        self.assertFalse(desk.origin_allowed("null", 8765))

    def test_cross_origin_api_request_gets_403(self):
        self.start(fake_runner([]))
        for origin in ("https://evil.example", "null", "http://localhost.evil.example"):
            code, _, _ = self.get("/api/state.json", origin=origin)
            self.assertEqual(code, 403, origin)

    def test_own_origin_and_no_origin_header_are_served(self):
        self.start(fake_runner([]))
        for origin in (None, "http://127.0.0.1:%d" % self.port, "http://localhost:%d" % self.port):
            code, _, _ = self.get("/api/state.json", origin=origin)
            self.assertEqual(code, 200, origin)


if __name__ == "__main__":
    unittest.main()
