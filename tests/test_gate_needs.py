"""Story #496 (epic #485 item 16): every job of ci.yml is in the `needs` of the `gate` job, or is named here as exempt.

A job left out of `needs` can fail and the gate never sees it (today `shortcut-ledger` is the one)."""
import re
from pathlib import Path

CI = (Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

# A job that is not in the gate's needs must be named here, with the reason. The gate cannot need itself.
EXEMPT = {"gate": "the gate itself"}


def jobs(text=CI):
    section = text.split("\njobs:\n", 1)[1]
    return re.findall(r"^  ([A-Za-z0-9_-]+):\s*$", section, re.M)


def gate_needs():
    block = CI.split("\n  gate:\n", 1)[1]
    m = re.search(r"^    needs:\s*\[(.*?)\]", block, re.M | re.S)
    assert m, "the gate job has no `needs: [...]` list"
    return [n.strip() for n in m.group(1).split(",") if n.strip()]


def test_s496_every_job_of_ci_yml_is_in_the_gate_needs_or_named_as_exempt():
    needs = set(gate_needs())
    missing = [j for j in jobs() if j not in needs and j not in EXEMPT]
    assert not missing, f"jobs the gate does not wait for: {missing}; add them to `needs` of the gate job, or name them in EXEMPT with a reason"


def test_s496_shortcut_ledger_is_in_the_gate_needs():
    assert "shortcut-ledger" in gate_needs()


def test_s496_the_exempt_list_holds_no_job_that_is_not_in_ci_yml_and_no_job_the_gate_needs():
    all_jobs, needs = set(jobs()), set(gate_needs())
    assert [j for j in EXEMPT if j not in all_jobs] == [], "a stale EXEMPT entry"
    assert [j for j in EXEMPT if j in needs] == [], "an EXEMPT job is in the gate's needs: drop the entry"


def test_s496_the_gate_needs_name_only_jobs_that_exist():
    assert [n for n in gate_needs() if n not in set(jobs())] == []


def test_s496_a_job_key_with_a_trailing_comment_is_a_job():
    sample = "name: x\njobs:\n  one:\n    runs-on: a\n  two:   # a note\n    runs-on: a\n  three: # another\n    runs-on: a\n"
    assert jobs(sample) == ["one", "two", "three"]
