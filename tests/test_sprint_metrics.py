"""Story #568: one row of numbers per pull request. A pure function: no gh, no network."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from sprint_metrics import main, pr_row  # noqa: E402

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


# ---- story #588: the command line (a fake reader, no network) ----
REPO = "example-org/child-a"
DAY = "2026-11-19"
SEARCH = (f"search/issues?q=repo:{REPO}+is:pr+is:merged+merged:{DAY}T00:00:00%2B00:00..{DAY}T23:59:59%2B00:00"
          "&per_page=100")


def pull(n, ref, body, created, merged):
    return {"number": n, "created_at": created, "merged_at": merged, "body": body, "head": {"ref": ref}}


def runs_path(ref, created, merged):
    return f"repos/{REPO}/actions/runs?branch={ref}&event=pull_request&created={created}..{merged}&per_page=100"


def world():
    """Two merged PRs: #564 links story #544, #565 links an issue that is not a story."""
    c1, m1 = "2026-11-19T12:00:00Z", "2026-11-19T15:30:30Z"
    c2, m2 = "2026-11-19T09:00:00Z", "2026-11-19T10:00:00Z"
    return {
        SEARCH: {"incomplete_results": False, "total_count": 2, "items": [{"number": 565}, {"number": 564}]},
        f"repos/{REPO}/pulls/564": pull(564, "feat/a", "Closes #544", c1, m1),
        f"repos/{REPO}/pulls/565": pull(565, "feat/b", "Fixes #700", c2, m2),
        f"repos/{REPO}/pulls/564/reviews?per_page=100": [{"state": "CHANGES_REQUESTED"}, {"state": "APPROVED"}],
        f"repos/{REPO}/pulls/565/reviews?per_page=100": [],
        runs_path("feat/a", c1, m1): {"total_count": 3, "workflow_runs": [
            {"conclusion": "failure"}, {"conclusion": "failure"}, {"conclusion": "success"}]},
        runs_path("feat/b", c2, m2): {"total_count": 1, "workflow_runs": [{"conclusion": "cancelled"}]},
        f"repos/{REPO}/issues/544": {"number": 544, "created_at": "2026-11-19T10:00:00Z",
                                     "labels": [{"name": "user-story"}]},
        f"repos/{REPO}/issues/700": {"number": 700, "created_at": "2026-11-18T10:00:00Z", "labels": [{"name": "bug"}]},
    }


def run(routes, *extra, capsys=None):
    calls = []

    def api(path, token=None):
        calls.append(path)
        return routes.get(path)

    code = main(["--repo", REPO, "--date", DAY, *extra], api=api)
    return code, calls


def test_a_day_with_two_merged_prs_prints_a_table_and_a_totals_line(capsys):
    code, _ = run(world())
    out = capsys.readouterr().out.splitlines()
    assert code == 0
    assert out[0].startswith("| PR | Story | Story to PR (min) | PR to merge (min) | CI runs | Failed | Cancelled |")
    rows = [line for line in out if line.startswith("| #")]
    assert rows == ["| #564 | #544 | 120 | 210 | 3 | 2 | 0 | 1 |", "| #565 | - | - | 60 | 1 | 0 | 1 | 0 |"]
    assert out[-1] == ("Total: 2 PRs, 120 min story to PR, 270 min PR to merge, 4 runs, 2 failed, "
                       "1 cancelled, 1 review rounds")


def test_the_command_reads_only_the_five_get_paths_through_the_shared_reader():
    import issue_notice
    import sprint_metrics
    assert sprint_metrics.gh_api is issue_notice.gh_api
    _, calls = run(world())
    shapes = ("search/issues?q=", f"repos/{REPO}/pulls/", f"repos/{REPO}/actions/runs?", f"repos/{REPO}/issues/")
    assert calls and all(c.startswith(shapes) for c in calls)
    assert len(calls) == len(set(calls)) and len(calls) == 1 + 2 * 3 + 2  # search, 2x(pull,reviews,runs), 2 issues


def test_a_pr_that_cannot_be_read_is_a_named_row_and_exit_1(capsys):
    routes = world()
    del routes[f"repos/{REPO}/pulls/564/reviews?per_page=100"]
    code, _ = run(routes)
    out = capsys.readouterr().out
    assert code == 1
    assert "| #564 | could not read: reviews |" in out
    assert "| #565 | - | - | 60 |" in out
    routes = world()
    del routes[f"repos/{REPO}/issues/544"]
    code, _ = run(routes)
    assert code == 1 and "| #564 | could not read: linked issue |" in capsys.readouterr().out
    routes = world()
    routes[runs_path("feat/a", "2026-11-19T12:00:00Z", "2026-11-19T15:30:30Z")]["total_count"] = 101
    code, _ = run(routes)
    assert code == 1 and "| #564 | could not read: more than 100 runs |" in capsys.readouterr().out


def test_a_failed_search_prints_the_reason_and_no_table(capsys):
    for bad in (None, {"incomplete_results": True, "total_count": 1, "items": [{"number": 1}]},
                {"incomplete_results": False, "total_count": 101, "items": [{"number": 1}]}):
        code, _ = run({SEARCH: bad})
        out = capsys.readouterr().out
        assert code == 1 and out.strip() and "|" not in out


def test_an_empty_value_prints_a_dash_and_adds_nothing_to_the_totals(capsys):
    routes = world()
    routes[f"repos/{REPO}/pulls/565"]["merged_at"] = None
    routes[runs_path("feat/b", "2026-11-19T09:00:00Z", None)] = routes.pop(
        runs_path("feat/b", "2026-11-19T09:00:00Z", "2026-11-19T10:00:00Z"))
    run(routes)
    out = capsys.readouterr().out
    assert "| #565 | - | - | - | 1 | 0 | 1 | 0 |" in out
    assert "210 min PR to merge" in out


def test_a_day_with_no_merged_pr_says_so_and_exits_0(capsys):
    code, _ = run({SEARCH: {"incomplete_results": False, "total_count": 0, "items": []}})
    assert code == 0 and capsys.readouterr().out.strip() == f"no merged PRs on {DAY}"


def test_the_day_is_read_on_the_clock_the_offset_names(monkeypatch):
    monkeypatch.delenv("GH_REPO", raising=False)
    seen = []
    main(["--repo", REPO, "--date", DAY, "--utc-offset", "+05:30"], api=lambda p, token=None: seen.append(p))
    assert f"merged:{DAY}T00:00:00%2B05:30..{DAY}T23:59:59%2B05:30" in seen[0]
    for argv in (["--utc-offset", "5:30"], ["--utc-offset", "+25"], ["--date", "19-11-2026"], ["--repo", ""]):
        seen.clear()
        args = ["--repo", REPO, "--date", DAY]
        for i in range(0, len(argv), 2):
            args = [a for a in args]
            if argv[i] in args:
                args[args.index(argv[i]) + 1] = argv[i + 1]
            else:
                args += argv[i:i + 2]
        assert main(args, api=lambda p, token=None: seen.append(p)) == 2 and not seen
