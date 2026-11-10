#!/usr/bin/env python3
"""ShipQuick bench report (story #312, A1b). Stdlib only. Reads a run folder or a results.json and prints a
markdown table: for each model and metric, the median per task and arm, the ratio kit / no-kit per task, the
geometric mean of those ratios over tasks, and a 95% bootstrap interval over the tasks.

  python3 bench/report.py DIR_OR_results.json

A ratio below 1.00 means the kit arm used less. A metric nobody recorded shows n/a, never 0.
The bootstrap resamples the task ratios (2000 times, fixed seed), so the same input gives the same interval.
"""
import json
import math
import random
import statistics
import sys
from pathlib import Path

METRICS = ("loc", "output_tokens", "cost_usd", "seconds", "turns")
BASE, KIT = "no-kit", "kit"


def median(xs):
    return statistics.median(xs)


def geomean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs))


def bootstrap_ci(xs, n=2000, seed=1, stat=geomean):
    rng = random.Random(seed)
    samples = sorted(stat([rng.choice(xs) for _ in xs]) for _ in range(n))
    return samples[int(0.025 * n)], samples[int(0.975 * n)]


def load(path):
    p = Path(path)
    p = p / "results.json" if p.is_dir() else p
    return json.loads(p.read_text(encoding="utf-8"))["results"]


def task_ratios(results, model, metric):
    """Per task: median of the kit arm over median of the no-kit arm. A task missing either side is skipped."""
    ratios = []
    for task in sorted({r["task"] for r in results}):
        med = {}
        for arm in (BASE, KIT):
            vals = [r[metric] for r in results
                    if r["task"] == task and r["model"] == model and r["arm"] == arm and r.get(metric) is not None]
            med[arm] = median(vals) if vals else None
        if med[BASE] and med[KIT] is not None and med[KIT] > 0:
            ratios.append(med[KIT] / med[BASE])
    return ratios


def rate(results, model, arm, key):
    cells = [r for r in results if r["model"] == model and r["arm"] == arm]
    hit = sum(1 for r in cells if r.get(key))
    return f"{hit}/{len(cells)} ({round(100 * hit / len(cells))}%)" if cells else "n/a"


def table(results):
    models = sorted({r["model"] for r in results})
    out = ["| Model | Metric | Tasks | kit / no-kit (geometric mean) | 95% interval |", "|---|---|---|---|---|"]
    for m in models:
        for metric in METRICS:
            ratios = task_ratios(results, m, metric)
            if ratios:
                lo, hi = bootstrap_ci(ratios)
                out.append(f"| {m} | {metric} | {len(ratios)} | {geomean(ratios):.2f} | {lo:.2f} to {hi:.2f} |")
            else:
                out.append(f"| {m} | {metric} | 0 | n/a | n/a |")
    out += ["", "| Model | Arm | Hidden check pass | Safe | Test exists |", "|---|---|---|---|---|"]
    for m in models:
        for arm in (BASE, KIT):
            out.append(f"| {m} | {arm} | {rate(results, m, arm, 'correct')} | {rate(results, m, arm, 'safe')} "
                       f"| {rate(results, m, arm, 'has_test')} |")
    return "\n".join(out)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    print(table(load(argv[0])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
