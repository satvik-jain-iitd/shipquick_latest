"""Stories #429 (D3) and #430 (D4, epic #91): the Desk's "Waiting for you" lists only what needs the owner, with a reason;
the Roadmap card links to the live roadmap. Fake gh, no network."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import desk  # noqa: E402
from test_desk import FakeClock, ISSUES  # noqa: E402


def pr(number, files=(), base="dev", head="feat/x", body="", decision="", draft=False):
    return {"number": number, "title": "PR %d" % number, "isDraft": draft, "url": "https://example.test/%d" % number,
            "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
            "files": [{"path": f} for f in files], "baseRefName": base, "headRefName": head, "body": body, "reviewDecision": decision}


def runner(prs, branch="exists", repo_url="https://github.com/acme/proj"):
    def run(args):
        if args[:2] == ["pr", "list"]:
            return json.dumps(prs)
        if args[:2] == ["issue", "list"]:
            return ISSUES
        if args[:2] == ["repo", "view"]:
            return json.dumps({"url": repo_url})
        if args[:1] == ["api"]:
            if branch == "exists":
                return "{}"
            raise desk.DeskError("gh failed: gh: Not Found (HTTP 404)" if branch == "missing" else "gh failed: boom")
        raise AssertionError("unexpected gh call: %r" % (args,))
    return run


def state(prs, tmp_repo=None, **kw):
    d = desk.Desk(tmp_repo or ROOT, runner=runner(prs, **kw), clock=FakeClock(), band=Path("/nonexistent/band.csv"))
    return d.state()[1]


UAT_OPEN = "## UAT on dev (https://dev.example)\n- [x] story one\n- [ ] Old flows still work\n"
UAT_DONE = "## UAT on dev (https://dev.example)\n- [x] story one\n- [x] Old flows still work\n"


class Waiting(unittest.TestCase):
    def test_a_protected_path_pr_waits_with_its_reason(self):
        w = state([pr(1, files=["README.md", "scripts/mode.sh"])])["waiting"]
        self.assertEqual([x["number"] for x in w], [1])
        self.assertIn("protected path", w[0]["reason"])
        self.assertIn("scripts/mode.sh", w[0]["reason"])

    def test_a_shipquick_file_is_protected_too(self):
        w = state([pr(2, files=[".shipquick/features.json"])])["waiting"]
        self.assertEqual(len(w), 1)
        self.assertIn("protected path", w[0]["reason"])

    def test_a_release_pr_with_unticked_uat_boxes_waits(self):
        w = state([pr(3, base="main", head="dev", body=UAT_OPEN)])["waiting"]
        self.assertEqual(len(w), 1)
        self.assertIn("1 unticked", w[0]["reason"])

    def test_a_release_pr_with_every_box_ticked_does_not_wait_on_uat(self):
        self.assertEqual(state([pr(3, base="main", head="dev", body=UAT_DONE)])["waiting"], [])

    def test_an_approved_pr_waits_in_manual_mode_not_in_auto(self):
        import tempfile
        for mode, expect in (("manual", 1), ("semi", 1), ("auto", 0)):
            with tempfile.TemporaryDirectory() as t:
                (Path(t) / ".shipquick").mkdir()
                (Path(t) / ".shipquick" / "mode").write_text(mode + "\n", encoding="utf-8")
                w = state([pr(4, files=["docs/a.md"], decision="APPROVED")], tmp_repo=Path(t))["waiting"]
                self.assertEqual(len(w), expect, mode)
                if expect:
                    self.assertIn("approved", w[0]["reason"])

    def test_other_open_prs_are_not_listed(self):
        self.assertEqual(state([pr(5, files=["docs/a.md"]), pr(6, files=["tests/x.py"], decision="REVIEW_REQUIRED")])["waiting"], [])

    def test_the_protected_list_is_the_one_review_merge_reads(self):
        # a path the file lists but this module never names: a custom repo's own list is honoured, no second copy in desk.py
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "scripts").mkdir()
            (Path(t) / "scripts" / "protected_paths.txt").write_text("# c\nspecial/*\n", encoding="utf-8")
            w = state([pr(7, files=["special/deep/x.txt"])], tmp_repo=Path(t))["waiting"]
            self.assertEqual(len(w), 1)


class RoadmapLink(unittest.TestCase):
    def test_the_link_points_at_roadmap_md_on_the_roadmap_branch(self):
        r = state([])["roadmap_link"]
        self.assertEqual(r, {"state": "link", "url": "https://github.com/acme/proj/blob/roadmap/ROADMAP.md"})

    def test_a_missing_roadmap_branch_says_so(self):
        r = state([], branch="missing")["roadmap_link"]
        self.assertEqual(r["state"], "no_branch")
        self.assertNotIn("url", r)

    def test_any_other_gh_failure_is_an_error_not_a_missing_branch(self):
        s = state([], branch="boom")
        self.assertIn("boom", s["error"] or "")


if __name__ == "__main__":
    unittest.main()


class Page(unittest.TestCase):
    def test_the_page_shows_the_reason_and_the_roadmap_link_with_no_innerhtml(self):
        h = (ROOT / "scripts" / "desk" / "index.html").read_text(encoding="utf-8")
        self.assertIn("p.reason", h)
        self.assertIn("roadmap_link", h)
        self.assertIn('rel = "noopener noreferrer"', h)
        self.assertNotIn("innerHTML", h)
