"""Story #497 (epic #485 item 7): a nightly full run of every CI job on dev, with one issue when it is red.

The decision logic is scripts/nightly_full_run.py; the workflow only calls it. `gh` is faked, so no network is used.
A scheduled run uses the workflow of the default branch, so the script dispatches ci.yml on `dev` itself: every job
checks out dev, and the change map already turns every area on for an event that is not a pull request or a push."""
import datetime
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import adoption_scan as scan  # noqa: E402
import issue_notice  # noqa: E402
import nightly_full_run as nf  # noqa: E402

REPO = "o/r"
TODAY = "2026-11-13"
START = datetime.datetime(2026, 11, 13, 1, 0, tzinfo=datetime.timezone.utc).timestamp()
RUN_URL = "https://github.com/o/r/actions/runs/700"


def iso(offset=0):
    return datetime.datetime.fromtimestamp(START + offset, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def job(name, status="completed", conclusion="success", steps=True, runner="GitHub Actions 1"):
    return {"name": name, "status": status, "conclusion": conclusion, "runner_name": runner if steps else None,
            "steps": [{"name": "Set up job", "conclusion": "success"}] if steps else []}


def red_run():
    return {"id": 700, "status": "completed", "conclusion": "failure", "html_url": RUN_URL, "head_sha": "a" * 40, "created_at": iso(5)}


def green_run():
    return {**red_run(), "conclusion": "success"}


class Clock:
    def __init__(self):
        self.t, self.slept = START, 0

    def now(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds
        self.slept += seconds


class FakeGh:
    """The few gh calls the nightly script makes: api reads and gh commands."""
    def __init__(self, run=None, jobs=(), issues=(), states=None, runs=None):
        self.cmds, self.run_value, self.jobs_value, self.issues_value = [], run or red_run(), list(jobs), list(issues)
        self.states = list(states or [])   # successive answers for the run's own state, then the last one repeats
        self.runs_value = runs if runs is not None else [{"id": 700, "created_at": iso(5), "status": "queued"}]

    def api(self, path, token=None):
        if "/workflows/ci.yml/runs" in path:
            return {"workflow_runs": self.runs_value}
        if path.endswith("/jobs?per_page=100"):
            return {"jobs": self.jobs_value}
        if "/actions/runs/" in path:
            return self.states.pop(0) if len(self.states) > 1 else (self.states[0] if self.states else self.run_value)
        if "/issues?labels=" in path:
            return self.issues_value
        return None

    def run(self, cmd, check=False, **kwargs):
        self.cmds.append(list(cmd))
        return subprocess.CompletedProcess(cmd, 0)

    def count(self, *words):
        return sum(1 for c in self.cmds if all(w in c for w in words))


def night(gh, wait_minutes=150, dry_run=False):
    clock = Clock()
    result = nf.nightly(REPO, "dev", wait_minutes, api=gh.api, run_cmd=gh.run, sleep=clock.sleep, now=clock.now,
                        today=TODAY, dry_run=dry_run)
    return result, clock


# ---- the four cases of the story ----
def test_s497_a_green_night_opens_nothing():
    gh = FakeGh(run=green_run(), jobs=[job("gate"), job("test (3.12)")])
    result, _ = night(gh)
    assert result == "green"
    assert gh.count("issue") == 0, gh.cmds


def test_s497_the_first_red_night_opens_one_issue_that_names_the_job():
    gh = FakeGh(jobs=[job("gate", conclusion="failure"), job("test (3.12)", conclusion="failure")], issues=[])
    result, _ = night(gh)
    assert result == "opened"
    assert gh.count("issue", "create") == 1 and gh.count("issue", "comment") == 0, gh.cmds
    create = next(c for c in gh.cmds if "create" in c and "issue" in c)
    body = create[create.index("--body") + 1]
    assert create[create.index("--title") + 1] == nf.TITLE
    assert "test (3.12)" in body and RUN_URL in body and TODAY in body


def test_s497_the_second_red_night_comments_on_the_open_issue():
    gh = FakeGh(jobs=[job("test (3.12)", conclusion="failure")], issues=[{"number": 41, "title": nf.TITLE}])
    result, _ = night(gh)
    assert result == "commented #41"
    assert gh.count("issue", "comment", "41") == 1 and gh.count("issue", "create") == 0, gh.cmds


def test_s497_the_issue_says_whether_a_job_failed_or_never_got_a_machine():
    gh = FakeGh(jobs=[job("test (3.12)", conclusion="failure"),
                      job("ui-ios-compile", status="queued", conclusion=None, steps=False)], issues=[])
    night(gh)
    body = next(c for c in gh.cmds if "create" in c)[-1]
    assert "- test (3.12): failed" in body
    assert "- ui-ios-compile: never got a machine" in body


# ---- what counts as a problem ----
def test_s497_a_skipped_job_is_not_a_problem_and_the_gate_stays_the_judge():
    jobs = [job("tdd", conclusion="skipped", steps=False), job("gate")]
    assert nf.problems(green_run(), jobs) == []
    assert [p["job"] for p in nf.problems(red_run(), jobs + [job("test (3.12)", conclusion="failure")])] == ["test (3.12)"]


def test_s497_a_job_cancelled_before_any_runner_took_it_never_got_a_machine():
    p = nf.problems(red_run(), [job("ui-ios-snapshots", conclusion="cancelled", steps=False)])
    assert p[0]["kind"] == "never got a machine", p
    p = nf.problems(red_run(), [job("ui-ios-snapshots", conclusion="cancelled")])
    assert p[0]["kind"] == "failed", p


def test_s497_a_red_run_with_no_failing_job_is_still_one_problem():
    p = nf.problems(red_run(), [job("gate")])
    assert len(p) == 1 and p[0]["kind"] == "failed", p


# ---- the wait ----
def test_s497_the_run_is_waited_for_and_a_job_still_queued_at_the_deadline_never_got_a_machine():
    running = {**red_run(), "status": "in_progress", "conclusion": None}
    gh = FakeGh(run=running, states=[running], jobs=[job("ui-ios-compile", status="queued", conclusion=None, steps=False)], issues=[])
    result, clock = night(gh, wait_minutes=30)
    assert result == "opened"
    assert 30 * 60 <= clock.slept < 30 * 60 + 600, clock.slept   # waited to the deadline and no longer
    body = next(c for c in gh.cmds if "create" in c)[-1]
    assert "- ui-ios-compile: never got a machine" in body


def test_s497_the_wait_ends_as_soon_as_the_run_is_completed():
    running = {**red_run(), "status": "in_progress", "conclusion": None}
    gh = FakeGh(run=green_run(), states=[running, running, green_run()], jobs=[job("gate")])
    result, clock = night(gh)
    assert result == "green" and clock.slept < 600, (result, clock.slept)


def test_s497_a_run_older_than_the_dispatch_is_not_the_nightly_run():
    old = {"id": 1, "created_at": iso(-86400), "status": "completed"}
    gh = FakeGh(run=green_run(), runs=[old, {"id": 700, "created_at": iso(5), "status": "queued"}], jobs=[job("gate")])
    night(gh)
    assert gh.count("actions/workflows/ci.yml/dispatches") == 1
    dispatch = next(c for c in gh.cmds if any("dispatches" in a for a in c))
    assert "ref=dev" in dispatch, dispatch


def test_s497_a_run_that_never_appears_is_one_problem_not_a_green_night():
    gh = FakeGh(runs=[], issues=[])
    result, _ = night(gh)
    assert result == "opened"
    body = next(c for c in gh.cmds if "create" in c)[-1]
    assert "never got a machine" in body


# ---- dry run, the label, the shared issue code ----
def test_s497_a_dry_run_changes_nothing():
    gh = FakeGh(jobs=[job("test (3.12)", conclusion="failure")], issues=[])
    result, _ = night(gh, dry_run=True)
    assert result == "dry-run"
    assert gh.count("issue") == 0 and gh.count("dispatches") == 0, gh.cmds


def test_s497_the_nightly_label_is_made_before_the_first_issue_is_opened():
    gh = FakeGh(jobs=[job("test (3.12)", conclusion="failure")], issues=[])
    night(gh)
    assert gh.count("label", "create", nf.LABEL) == 1, gh.cmds
    assert gh.cmds.index(next(c for c in gh.cmds if "label" in c)) < gh.cmds.index(next(c for c in gh.cmds if "create" in c and "issue" in c))


def test_s497_issue_notice_opens_or_comments_by_a_key_in_the_title():
    cmds = []
    run = lambda cmd, check=False, **k: cmds.append(cmd)  # noqa: E731
    existing = [{"number": 7, "title": "Nightly: THE FULL CI run on dev is red"}]
    out = issue_notice.open_or_comment("o/r", "nightly", "t", "b", "the full ci run", False, api=lambda p, token=None: existing, run=run)
    assert out == "commented #7" and cmds[0][:3] == ["gh", "issue", "comment"]
    out = issue_notice.open_or_comment("o/r", "nightly", "t", "b", "no such key", False, api=lambda p, token=None: existing, run=run)
    assert out == "opened" and cmds[1][:3] == ["gh", "issue", "create"]


def test_s497_the_adoption_scan_opens_its_issues_through_the_same_helper(monkeypatch):
    seen = []
    monkeypatch.setattr(issue_notice, "open_or_comment", lambda *a, **k: seen.append((a, k)) or "opened")
    scan.open_or_comment("owner/child", "owner/child: no caller", False)
    assert len(seen) == 1 and seen[0][0][1] == "feedback", seen


# ---- the workflow stays thin ----
def test_s497_the_workflow_is_a_timer_and_one_call_to_the_script():
    text = (ROOT / ".github" / "workflows" / "nightly.yml").read_text(encoding="utf-8")
    assert "schedule:" in text and "cron:" in text and "workflow_dispatch:" in text
    assert text.count("python3 scripts/nightly_full_run.py") == 1
    assert "actions: write" in text and "issues: write" in text and "contents: read" in text
    assert "if:" not in text, "the decision lives in the script, not in the workflow"
    assert "actions/checkout@" in text and "# v" in text, "a pinned checkout, as the other workflows"


def test_s497_the_change_map_already_turns_every_area_on_for_a_non_pr_event():
    """Reuse, not a second rule: the dispatched run has no pull request or push event, so the change map runs every job."""
    text = (ROOT / "scripts" / "change_map.py").read_text(encoding="utf-8")
    assert 'event not in ("pull_request", "push")' in text
    assert json.loads((ROOT / "scripts" / "change_map.json").read_text(encoding="utf-8"))["areas"]
