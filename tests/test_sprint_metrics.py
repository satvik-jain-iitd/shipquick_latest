"""Story #568: one row of numbers per pull request. A pure function: no gh, no network."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from sprint_metrics import pr_row  # noqa: E402

ISSUE = {"number": 544, "createdAt": "2026-11-19T10:00:00Z"}


def pr(**kw):
    base = {"number": 564, "createdAt": "2026-11-19T12:00:00Z", "mergedAt": "2026-11-19T15:30:30Z", "reviews": []}
    base.update(kw)
    return base


def test_a_merged_pr_gives_its_six_numbers():
    runs = [{"conclusion": "failure"}, {"conclusion": "failure"}, {"conclusion": "success"}]
    reviews = [{"state": "CHANGES_REQUESTED"}, {"state": "APPROVED"}]
    row = pr_row(pr(reviews=reviews), runs, ISSUE)
    assert row == {
        "number": 564, "story": 544, "story_minutes": 120, "merge_minutes": 210,
        "runs": 3, "failed": 2, "cancelled": 0, "review_rounds": 1,
    }


def test_an_open_pr_has_no_merge_time():
    row = pr_row(pr(mergedAt=None), [], ISSUE)
    assert row["merge_minutes"] is None


def test_a_pr_with_no_story_has_no_story_time():
    for issue in (None, {}):
        row = pr_row(pr(), [], issue)
        assert row["story"] is None and row["story_minutes"] is None
