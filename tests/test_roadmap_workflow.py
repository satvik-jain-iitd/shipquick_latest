"""S0.13: the roadmap runs on GitHub Actions, not n8n (story #49). Text checks: CI installs pytest and nothing else."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLOW = (ROOT / ".github" / "workflows" / "roadmap.yml").read_text(encoding="utf-8")
CALL = (ROOT / ".github" / "workflows" / "roadmap-call.yml").read_text(encoding="utf-8")


def test_s13_the_roadmap_workflow_is_reusable_and_reads_only_by_default():
    assert re.search(r"^on:\n  workflow_call:", FLOW, re.M)
    assert re.search(r"^permissions:\n  contents: read\n", FLOW, re.M)


def test_s13_the_job_has_exactly_the_token_rights_it_needs():
    job = FLOW.split("\njobs:\n", 1)[1]
    perms = dict(re.findall(r"^      ([\w-]+): (read|write)$", job.split("steps:", 1)[0], re.M))
    assert perms == {"contents": "write", "issues": "read", "pull-requests": "read", "checks": "read", "statuses": "read"}, perms


def test_s13_only_the_built_in_token_is_used_and_no_secret_is_named():
    assert "secrets." not in FLOW and "secrets: inherit" not in CALL
    assert "github.token" in FLOW or "GITHUB_TOKEN" in FLOW
    assert "n8n" not in FLOW.lower()


def test_s13_the_page_goes_to_a_branch_of_its_own_and_an_unchanged_page_makes_no_commit():
    assert "roadmap" in FLOW and "ROADMAP.md" in FLOW
    assert "git push origin roadmap" in FLOW or "git push origin HEAD:roadmap" in FLOW
    assert "git diff --cached --quiet" in FLOW
    assert "concurrency:" in FLOW


def test_s13_settings_come_from_the_child_repo_and_shipquick_holds_no_child_name():
    assert "roadmap.json" in FLOW
    assert "shipquick_ref" in FLOW and "node .shipquick/roadmap/roadmap.js" in FLOW


def test_s13_the_dogfood_caller_never_runs_pull_request_code_with_write_rights():
    on_block = CALL.split("\npermissions:", 1)[0]
    assert not re.search(r"^  pull_request(_target)?:", on_block, re.M), "a PR would run its own unreviewed roadmap.js with contents: write"
    assert re.search(r"^  workflow_run:", on_block, re.M)   # CI runs on every PR push, so Review still shows
    assert "default branch" in CALL.split("\nname:", 1)[0]   # the header says why the ref is reviewed code


def test_s13_owner_and_name_are_sent_as_strings():
    assert 'gh api graphql -f owner=' in FLOW.replace("\\\n", " ") or "-f owner=" in FLOW
    assert " -F " not in FLOW  # -F guesses types: a repo named 123 or true would be sent as a number or a boolean


def test_s13_the_dogfood_caller_runs_on_issues_a_finished_ci_and_a_daily_cron():
    assert re.search(r"^  issues:", CALL, re.M)
    assert re.search(r"cron: ['\"][\d*/ ]+['\"]", CALL)
    assert "uses: ./.github/workflows/roadmap.yml" in CALL
    assert re.search(r"^permissions:\n  contents: read\n", CALL, re.M)   # the top level stays read only; the calling job gets the rights
    perms = CALL.split("jobs:", 1)[1]
    for p in ("contents: write", "issues: read", "pull-requests: read", "checks: read", "statuses: read"):
        assert p in perms, p


def test_s13_the_n8n_code_is_gone():
    for gone in ("build.js", "build.test.js", "sha256.js", "ids.json", "projects.json", "workflows", "lib"):
        assert not (ROOT / "roadmap" / gone).exists(), gone
    text = (ROOT / "docs" / "LIVE_ROADMAP.md").read_text(encoding="utf-8").lower()
    assert "n8n" not in text.replace("no n8n", "").replace("without n8n", "")


def test_s13_workflow_run_names_the_real_ci_workflow():
    """workflow_run matches the `name:` of a workflow. A wrong name never fires and nothing says so (PR #52 review)."""
    ci_name = re.search(r'^name: "?([^"\n]+)"?\s*$', (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8"), re.M).group(1)
    listed = re.search(r"^  workflow_run:\n    workflows: \[(.+)\]", CALL, re.M).group(1)
    assert [w.strip().strip("\"'") for w in listed.split(",")] == [ci_name], (listed, ci_name)
