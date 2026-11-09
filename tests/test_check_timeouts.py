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
