"""Story #427 (D1, epic #91): the Desk shows every ShipQuick feature from the one features reader (frame D: Overview rows and
feature groups on the left, the chosen group on the right). Read-only server: no route writes a file. Fake gh, no network."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import desk  # noqa: E402
from test_desk_owner_cards import runner  # noqa: E402
from test_desk import FakeClock, ServerCase  # noqa: E402

DEFAULTS = json.loads((ROOT / "scripts" / "features_default.json").read_text(encoding="utf-8"))["features"]


def state_for(repo, **kw):
    d = desk.Desk(repo, runner=runner([], **kw), clock=FakeClock(), band=Path("/nonexistent/band.csv"))
    return d.state()[1]


def write(repo, text):
    (Path(repo) / ".shipquick").mkdir(exist_ok=True)
    (Path(repo) / ".shipquick" / "features.json").write_text(text, encoding="utf-8")


class Features(unittest.TestCase):
    def test_the_state_lists_every_feature_in_groups_with_the_plain_words(self):
        with tempfile.TemporaryDirectory() as t:
            f = state_for(Path(t))["features"]
            self.assertIsNone(f["error"])
            items = [i for g in f["groups"] for i in g["items"]]
            self.assertEqual({i["id"] for i in items}, set(DEFAULTS))
            for i in items:
                for k in ("name", "what", "if_off"):
                    self.assertEqual(i[k], DEFAULTS[i["id"]][k])
            self.assertEqual([g["name"] for g in f["groups"]], list(dict.fromkeys(d["group"] for d in DEFAULTS.values())))

    def test_a_feature_that_differs_from_its_default_says_so(self):
        with tempfile.TemporaryDirectory() as t:
            write(t, json.dumps({"version": 1, "features": {"lanes": {"on": False}, "roadmap": {"on": True}}}))
            items = {i["id"]: i for g in state_for(Path(t))["features"]["groups"] for i in g["items"]}
            self.assertTrue(items["lanes"]["changed"] and not items["lanes"]["on"])
            self.assertFalse(items["roadmap"]["changed"])
            self.assertFalse(items["hosted-roadmap"]["changed"])

    def test_locked_features_are_always_on_and_marked(self):
        with tempfile.TemporaryDirectory() as t:
            write(t, json.dumps({"version": 1, "features": {"gate": {"on": False}}}))
            items = {i["id"]: i for g in state_for(Path(t))["features"]["groups"] for i in g["items"]}
            self.assertTrue(items["gate"]["locked"] and items["gate"]["on"])

    def test_a_broken_features_file_is_an_error_card_never_a_wrong_list(self):
        with tempfile.TemporaryDirectory() as t:
            write(t, "{oops")
            f = state_for(Path(t))["features"]
            self.assertIn("not valid JSON", f["error"])
            self.assertEqual(f["groups"], [])

    def test_the_roadmap_card_says_off_when_the_roadmap_feature_is_off(self):
        with tempfile.TemporaryDirectory() as t:
            write(t, json.dumps({"version": 1, "features": {"roadmap": {"on": False}}}))
            self.assertEqual(state_for(Path(t))["roadmap_link"], {"state": "off"})


class ReadOnly(ServerCase):
    def test_no_route_accepts_a_write_and_nothing_is_written(self):
        import urllib.request
        self.start(runner([]))
        before = sorted(p.name for p in Path(tempfile.gettempdir()).glob("desk-write-*"))
        for method in ("POST", "PUT", "DELETE", "PATCH"):
            req = urllib.request.Request("http://127.0.0.1:%d/api/features" % self.port, data=b"{}", method=method)
            req.add_header("Host", "127.0.0.1:%d" % self.port)
            try:
                with urllib.request.urlopen(req, timeout=5) as r:
                    self.fail("%s returned %s" % (method, r.status))
            except urllib.error.HTTPError as e:
                self.assertGreaterEqual(e.code, 400, method)
        self.assertEqual(sorted(p.name for p in Path(tempfile.gettempdir()).glob("desk-write-*")), before)


class Page(unittest.TestCase):
    H = (ROOT / "scripts" / "desk" / "index.html").read_text(encoding="utf-8")

    def test_the_page_follows_frame_d(self):
        for needle in ("Overview", "Feature groups", 'setAttribute("role", "switch")', "Waiting for you", "Decided for you", "Roadmap", "Spend",
                       "What is ShipQuick?", "What is this page?", "What can I do here?", "Changed from default", "aria-current"):
            self.assertIn(needle, self.H)
        self.assertIn("overflow: auto", self.H)           # at 1280 only the feature pane scrolls
        self.assertNotIn("innerHTML", self.H)
        self.assertNotIn("<script src=", self.H)

    def test_the_page_reads_features_and_roadmap_off_from_the_state(self):
        self.assertIn("data.features", self.H)
        self.assertIn('rl.state === "off"', self.H)


if __name__ == "__main__":
    unittest.main()
