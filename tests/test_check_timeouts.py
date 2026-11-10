"""Story #154: every workflow job that runs on a runner carries `timeout-minutes`."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import check_timeouts as ct  # noqa: E402

GOOD = """on: push
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - run: echo hi
  call:
    uses: ./.github/workflows/other.yml
"""


def test_a_job_with_no_timeout_is_named():
    bad = GOOD + "  hang:\n    runs-on: ubuntu-latest\n    steps:\n      - run: sleep 9999\n"
    assert ct.missing(bad) == ["hang"]


def test_a_job_with_a_timeout_and_a_reusable_call_pass():
    assert ct.missing(GOOD) == []


def test_every_kit_workflow_job_has_a_timeout():
    found = {p.name: ct.missing(p.read_text()) for p in (ROOT / ".github/workflows").glob("*.yml")}
    assert {k: v for k, v in found.items() if v} == {}


# PR #171 second review: other indents, quoted keys and trailing comments must not slip past.
def test_a_job_key_with_a_trailing_comment_is_still_checked():
    text = "jobs:\n  b: # deploy\n    runs-on: ubuntu-latest\n    steps: []\n"
    assert ct.missing(text) == ["b"]


def test_a_four_space_indent_is_still_checked():
    text = "jobs:\n    b:\n        runs-on: ubuntu-latest\n        steps: []\n"
    assert ct.missing(text) == ["b"]


def test_a_quoted_job_key_is_still_checked():
    text = "jobs:\n  \"a\":\n    runs-on: ubuntu-latest\n"
    assert ct.missing(text) == ["a"]


def test_a_step_timeout_alone_does_not_count_for_the_job():
    text = "jobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n      - run: x\n        timeout-minutes: 5\n"
    assert ct.missing(text) == ["a"]


def test_jobs_with_nothing_parsed_fails_instead_of_passing():
    assert ct.missing("jobs: {build: {runs-on: ubuntu-latest}}\n") == [ct.NO_JOBS]


# Story #194: quoted keys and a space before the colon still count.
def test_s194_a_quoted_runs_on_and_timeout_key_count():
    assert ct.missing('jobs:\n  a:\n    "runs-on": ubuntu-latest\n') == ["a"]
    assert ct.missing('jobs:\n  a:\n    "runs-on": ubuntu-latest\n    "timeout-minutes": 5\n') == []


def test_s194_a_space_before_the_colon_still_counts():
    assert ct.missing("jobs:\n  a :\n    runs-on : ubuntu-latest\n") == ["a"]
    assert ct.missing("jobs:\n  a:\n    runs-on: x\n    timeout-minutes : 5\n") == []


def test_s194_the_no_jobs_line_names_the_fix():
    assert "block style" in ct.NO_JOBS


# Story #174: a workflow file with zero jobs (another indent style) is named, never passed silently.
def test_s174_a_file_with_zero_jobs_is_named_in_the_output(tmp_path, capsys):
    f = tmp_path / "indented.yml"
    f.write_text("on: push\n    jobs:\n        build:\n            runs-on: ubuntu-latest\n", encoding="utf-8")
    assert ct.main([str(f)]) == 0
    out = capsys.readouterr().out
    assert f"no jobs found in {f}" in out
