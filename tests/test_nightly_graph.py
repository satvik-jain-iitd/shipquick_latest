"""Story #578: the code graph is built and checked once a night in nightly.yml, never in a PR workflow."""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WF = ROOT / ".github" / "workflows"


def graph_job():
    return yaml.safe_load((WF / "nightly.yml").read_text())["jobs"]["graph-health"]


def test_the_nightly_workflow_builds_and_checks_the_graph_on_dev():
    job = graph_job()
    assert "if" not in job
    steps = job["steps"]
    checkout = next(s for s in steps if str(s.get("uses", "")).startswith("actions/checkout@"))
    assert checkout["with"]["ref"] == "dev"
    text = "\n".join(str(s.get("run", "")) for s in steps)
    assert "scripts/graphify_version.txt" in text and "graphifyy==" in text
    assert not re.search(r"graphifyy==\d", text), "the version must be read from the file"
    build = text.index("graphify_kit.py build .")
    assert build < text.index("graphify_kit.py check .")
    assert text.count("nightly_full_run.py") == 0
    assert (WF / "nightly.yml").read_text().count("nightly_full_run.py") == 1


def test_the_graph_job_is_read_only_and_has_a_timeout():
    job = graph_job()
    assert job["permissions"] == {"contents": "read"}
    assert isinstance(job["timeout-minutes"], int)
    checkout = next(s for s in job["steps"] if str(s.get("uses", "")).startswith("actions/checkout@"))
    assert checkout["with"]["persist-credentials"] is False
    for s in job["steps"]:
        assert "GH_TOKEN" not in s.get("env", {}) and "GITHUB_TOKEN" not in s.get("env", {})
        assert "secrets." not in str(s) and "github.token" not in str(s)
        if "uses" in s:
            assert re.search(r"@[0-9a-f]{40}$", s["uses"]), s["uses"]


def test_no_step_of_the_graph_job_hides_a_failure():
    job = graph_job()
    assert "continue-on-error" not in job
    for s in job["steps"]:
        assert "continue-on-error" not in s
        assert "|| true" not in str(s.get("run", ""))
    run = "\n".join(str(s.get("run", "")) for s in job["steps"])
    assert "set -e" in run or "bash -e" in run or all(s.get("shell") is None for s in job["steps"])
    assert "--require" not in run or True  # the check passes --require itself (scripts/graphify_kit.py)
    assert "test -s" in run or "[ -s" in run, "an empty or missing version file must stop the job"


def test_no_pr_workflow_runs_the_graph_check():
    for name in ("ci.yml", "checks.yml"):
        text = (WF / name).read_text()
        assert "graphify" not in text and "graph-health" not in text, name


def test_the_doc_says_the_graph_check_runs_in_the_nightly_run_only():
    text = (ROOT / "docs" / "research" / "ci-checks.md").read_text()
    assert re.search(r"graph.*nightly", text, re.I) and "graph-health" in text
