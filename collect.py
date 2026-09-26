"""Download finished Kaggle runs for a model and report every metric, including the
ones that need more than one task (knows-but-passes, the rubric split) and the cost.

    python collect.py gemini-3.7-flash [claude-opus-5-default ...]

Per-item results land in results/kaggle/<model>.json in the same shape pilot.py writes.
"""

import glob
import json
import os
import subprocess
import sys

import judgebench as jb

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "results", "kaggle", "raw")
KAGGLE = os.path.join(HERE, ".venv", "Scripts", "kaggle")

TASKS = {
    "judge-docks-planted-error": "scores",
    "judge-spots-subtle-error": "detect",
    "judge-prefers-correct-answer": "pairwise",
    "judge-docks-with-error-rubric": "rubric",
    "judge-resists-false-claims": "manipulation",
}


def latest_run_dir(task, model):
    # raw/<task>/<version>/<model>/<run id>/
    dirs = glob.glob(os.path.join(RAW, task, "*", model, "*"))
    return max(dirs, key=lambda d: (int(d.split(os.sep)[-3]), int(d.split(os.sep)[-1])), default=None)


def load_run(run_dir):
    rows, cost, tokens = [], 0, {"input": 0, "output": 0}
    for path in glob.glob(os.path.join(run_dir, "*run_param_id_*.run.json")):
        with open(path, encoding="utf-8") as f:
            run = json.load(f)
        # Errored items still cost tokens up to the failure but have no result.
        if run["state"] == "BENCHMARK_TASK_RUN_STATE_COMPLETED":
            rows.append(run["results"][0]["dictResult"])
        for conv in run["conversations"]:
            m = conv.get("metrics") or {}
            cost += int(m.get("inputTokensCostNanodollars", 0)) + int(m.get("outputTokensCostNanodollars", 0))
            tokens["input"] += m.get("inputTokens", 0)
            tokens["output"] += m.get("outputTokens", 0) + m.get("thinkingTokens", 0)
    return sorted(rows, key=lambda r: r["id"]), cost / 1e9, tokens


def collect(model, items):
    """The model's results, or None if any task has errored items (a subset isn't comparable)."""
    out, costs, short = {}, {}, []
    for task, key in TASKS.items():
        subprocess.run([KAGGLE, "b", "t", "download", task, "-m", model, "-o", RAW],
                       check=True, capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        run_dir = latest_run_dir(task, model)
        if run_dir is None:
            raise SystemExit(f"{model}: no downloaded run for {task}")
        out[key], costs[key], _ = load_run(run_dir)
        if len(out[key]) != len(items):
            short.append(f"{task} {len(out[key])}/{len(items)}")
    out["cost_usd"] = costs
    if short:
        print(f"model {model}: incomplete, rerun needed ({', '.join(short)}); spent ${sum(costs.values()):.3f}")
        return None
    with open(os.path.join(HERE, "results", "kaggle", f"{model}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    return out


def main():
    items = jb.load_items()
    for model in sys.argv[1:]:
        d = collect(model, items)
        if d is None:
            continue
        jb.report(model, items, d["scores"], d["detect"], d["pairwise"], d["rubric"], d["manipulation"])
        print("  cost  " + "  ".join(f"{k} ${v:.3f}" for k, v in d["cost_usd"].items())
              + f"  total ${sum(d['cost_usd'].values()):.3f}")


if __name__ == "__main__":
    main()
