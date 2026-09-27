"""How much a judge's score for the same answer moves between calls.

The scoring task and the manipulation task both score the plain clean and subtle answers
with the same prompt in separate calls, so every run is its own test-retest. With an
older snapshot of the results (results/kaggle/run1/), the scoring task is compared across
runs as well.

    python stability.py
"""

import glob
import json
import os

import judgebench as jb

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results", "kaggle")


def agreement(a_rows, b_rows):
    """Exact score agreement over clean and subtle, and how often the dock decision
    (subtle strictly below clean) comes out the same."""
    b = {r["id"]: r for r in b_rows}
    pairs = [(r, b[r["id"]]) for r in a_rows if r["id"] in b]
    same = [x[v] == y[v] for x, y in pairs for v in ("clean", "subtle")]
    decision = [jb.docks(x["clean"], x["subtle"]) == jb.docks(y["clean"], y["subtle"]) for x, y in pairs]
    return sum(same) / len(same), sum(decision), len(decision)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    print("| Model | Same score, within run | Same dock decision, within run | Same score, across runs | Same dock decision, across runs |")
    print("|---|---|---|---|---|")
    for path in sorted(glob.glob(os.path.join(RESULTS, "*.json"))):
        name = os.path.basename(path)
        d = load(path)
        within = agreement(d["scores"], d["manipulation"])
        cells = [f"{within[0]:.2f}", f"{within[1]}/{within[2]}"]
        old = os.path.join(RESULTS, "run1", name)
        # A snapshot identical to the current file means the model hasn't been rerun.
        if os.path.exists(old) and load(old)["scores"] != d["scores"]:
            across = agreement(load(old)["scores"], d["scores"])
            cells += [f"{across[0]:.2f}", f"{across[1]}/{across[2]}"]
        else:
            cells += ["", ""]
        print(f"| {name[:-5]} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
