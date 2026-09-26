"""Print a markdown table of the headline metrics for every collected model.

    python table.py
"""

import glob
import json
import os

import judgebench as jb

HERE = os.path.dirname(os.path.abspath(__file__))


def row(name, d):
    s, m = d["scores"], d.get("manipulation") or []
    note = jb.score_shift(m, "subtle_note")[0] if m else float("nan")
    return [name,
            jb.dock_rate(s)[0], jb.fail_rate(s)[0], jb.fail_rate(d["rubric"])[0],
            jb.detect_balanced_accuracy(d["detect"])[0], jb.pairwise_accuracy(d["pairwise"])[0],
            jb.manipulated_dock_rate(m)[0] if m else float("nan"), note,
            sum(d["cost_usd"].values())]


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(HERE, "results", "kaggle", "*.json"))):
        with open(path, encoding="utf-8") as f:
            rows.append(row(os.path.basename(path)[:-5], json.load(f)))
    rows.sort(key=lambda r: -r[1])
    print("| Model | Docks subtle | Fails wrong | Fails wrong, rubric | Detect | Pairwise | Docks, manipulated | Note shift | Cost |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r[0]} | " + " | ".join(f"{x:.2f}" for x in r[1:7]) + f" | {r[7]:+.2f} | ${r[8]:.2f} |")


if __name__ == "__main__":
    main()
