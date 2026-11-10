"""Story #189 (S11, epic #130): vibe tests. `bench/vibe.py` gives ten fixed screen prompts per platform and a
deterministic raw-UI scorer. Zero real API calls here: a fake `claude` on PATH logs its argv and copies fixture
files into its cwd, so the smoke path is exercised end to end without a model."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIBE = ROOT / "bench" / "vibe.py"
FIX = ROOT / "tests" / "fixtures"
GOOD = {"android": FIX / "android" / "src" / "good", "ios": FIX / "ios" / "Good", "web": FIX / "web" / "good"}
BAD = {"android": FIX / "android" / "src" / "bad", "ios": FIX / "ios" / "Bad", "web": FIX / "web" / "bad"}
SCREENS = {"sign_in", "list", "detail", "settings", "step_flow", "empty_state", "error", "form", "search", "profile"}

FAKE = """#!{py}
import json, os, shutil, sys
with open(os.environ["FAKE_LOG"], "a") as f:
    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": os.getcwd()}}) + "\\n")
for p in (os.listdir(os.environ["FAKE_DIR"]) if os.environ.get("FAKE_DIR") else []):
    shutil.copy(os.path.join(os.environ["FAKE_DIR"], p), p)
print(json.dumps({{"type": "result", "total_cost_usd": 0.01, "num_turns": 1, "usage": {{"output_tokens": 5}}}}))
"""


def _mod():
    spec = importlib.util.spec_from_file_location("bench_vibe", VIBE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _env(tmp_path, fake_dir=None):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    fake = bindir / "claude"
    fake.write_text(FAKE.format(py=sys.executable), encoding="utf-8")
    fake.chmod(0o755)
    env = {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}", "FAKE_LOG": str(tmp_path / "calls.jsonl")}
    if fake_dir:
        env["FAKE_DIR"] = str(fake_dir)
    return env


def _calls(tmp_path):
    p = tmp_path / "calls.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def test_selftest_scores_the_fixtures_and_makes_no_claude_call(tmp_path):
    env = _env(tmp_path)
    r = subprocess.run([sys.executable, str(VIBE), "--selftest"], capture_output=True, text=True, env=env, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "selftest 3/3 platforms pass" in r.stdout, r.stdout
    assert not (tmp_path / "calls.jsonl").exists(), "the selftest called claude"


def test_good_fixture_is_clean_and_bad_fixture_is_raw_on_every_platform():
    vibe = _mod()
    for platform in ("android", "ios", "web"):
        good = vibe.score_dir(platform, GOOD[platform])
        bad = vibe.score_dir(platform, BAD[platform])
        assert good["clean"] == 1, (platform, good)
        assert bad["clean"] == 0 and bad["hits"], (platform, bad)


def test_a_cell_with_no_screen_file_scores_zero(tmp_path):
    vibe = _mod()
    r = vibe.score_dir("android", tmp_path)
    assert r["clean"] == 0 and "no screen file" in r["reason"], r


def test_prompts_are_the_same_ten_generic_screens_on_three_platforms():
    vibe = _mod()
    prompts = vibe.prompts()
    assert sorted(prompts) == ["android", "ios", "web"]
    for platform, items in prompts.items():
        assert {p["id"] for p in items} == SCREENS, platform
        assert len(items) == 10, platform
        for p in items:
            assert p["prompt"].strip() and p["file"], p
    # fairness: the task text is identical across platforms; only the platform lead differs
    by_id = {p["id"]: p["task"] for p in prompts["android"]}
    assert all(p["task"] == by_id[p["id"]] for items in prompts.values() for p in items)


def test_smoke_runs_exactly_four_calls_and_only_the_kit_arm_gets_the_agent_block(tmp_path):
    fake_dir = tmp_path / "fake"
    fake_dir.mkdir()
    (fake_dir / "Screen.kt").write_text((GOOD["android"] / "GoodScreen.kt").read_text(), encoding="utf-8")
    (fake_dir / "Screen.swift").write_text((GOOD["ios"] / "GoodScreen.swift").read_text(), encoding="utf-8")
    out = tmp_path / "run"
    r = subprocess.run([sys.executable, str(VIBE), "--run", "--smoke", "--out", str(out)],
                       capture_output=True, text=True, env=_env(tmp_path, fake_dir), timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    calls = _calls(tmp_path)
    assert len(calls) == 4, calls
    kit = [c for c in calls if "--append-system-prompt" in c["argv"]]
    assert len(kit) == 2, "only the kit arm gets the agent block"
    for c in kit:
        assert "SELF-CHECK" in c["argv"][c["argv"].index("--append-system-prompt") + 1]
    for c in calls:
        assert c["argv"][c["argv"].index("--model") + 1] == "claude-haiku-5-5"
        assert "--disallowedTools" in c["argv"] and c["cwd"].endswith("work")
    data = json.loads((out / "results.json").read_text(encoding="utf-8"))
    assert len(data["results"]) == 4
    assert {(x["platform"], x["arm"]) for x in data["results"]} == {("android", "kit"), ("android", "no-kit"),
                                                                     ("ios", "kit"), ("ios", "no-kit")}
    assert data["score"] == {"kit": {"clean": 2, "screens": 2}, "no-kit": {"clean": 2, "screens": 2}}, data["score"]
    assert (out / "android__sign_in__kit__haiku" / "work" / "Screen.kt").exists()


def test_run_folder_inside_a_git_tree_is_refused_before_any_call(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    r = subprocess.run([sys.executable, str(VIBE), "--run", "--smoke", "--out", str(repo / "out")],
                       capture_output=True, text=True, env=_env(tmp_path), timeout=120)
    assert r.returncode != 0 and "inside a git work tree" in r.stderr, r.stdout + r.stderr
    assert not (tmp_path / "calls.jsonl").exists()


def test_a_full_run_needs_the_full_flag_so_a_typo_never_burns_sixty_calls(tmp_path):
    r = subprocess.run([sys.executable, str(VIBE), "--run", "--out", str(tmp_path / "out")],
                       capture_output=True, text=True, env=_env(tmp_path), timeout=120)
    assert r.returncode != 0 and "--full" in r.stderr, r.stdout + r.stderr
    assert not (tmp_path / "calls.jsonl").exists()
