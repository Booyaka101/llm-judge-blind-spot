"""Run the benchmark locally against an ollama model, to shake out the items and the
parsing before spending Kaggle runs.

    python pilot.py qwen2.5:32b [--max-calls N]

Replies are cached on disk per (model, prompt), so interrupted runs resume and
--max-calls lets it run in foreground chunks.
"""

import argparse
import hashlib
import json
import os
import sys
import urllib.request

import judgebench as jb

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "pilot_cache")


class Budget(Exception):
    pass


def make_ask(model, max_calls):
    os.makedirs(CACHE, exist_ok=True)
    calls = 0

    def ask(prompt):
        nonlocal calls
        key = hashlib.sha256(f"{model}\n{prompt}".encode()).hexdigest()
        path = os.path.join(CACHE, key + ".json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)["reply"]
        if max_calls is not None and calls >= max_calls:
            raise Budget
        calls += 1
        body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                           "options": {"temperature": 0, "num_ctx": 8192, "num_predict": 2048}})
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", body.encode(),
                                     {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=900) as r:
            reply = json.load(r)["response"]
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"model": model, "reply": reply}, f)
        return reply

    return ask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--items", default=os.path.join(HERE, "items.json"))
    ap.add_argument("--max-calls", type=int)
    args = ap.parse_args()

    items = jb.load_items(args.items)
    ask = make_ask(args.model, args.max_calls)
    scores, detects, pairs, rubric, manip = [], [], [], [], []
    try:
        for item in items:
            scores.append(jb.judge_scores(ask, item))
            detects.append(jb.judge_detect(ask, item))
            pairs.append(jb.judge_pairwise(ask, item))
            rubric.append(jb.judge_scores(ask, item, ("clean", "subtle", "obvious"), jb.RUBRIC_SCORE_PROMPT))
            manip.append(jb.judge_manipulation(ask, item))
    except Budget:
        print(f"budget hit after {len(scores)} complete items; re-run to continue")
        sys.exit(2)

    out = os.path.join(HERE, "results", f"pilot_{args.model.replace(':', '_').replace('/', '_')}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"scores": scores, "detect": detects, "pairwise": pairs, "rubric": rubric,
                   "manipulation": manip}, f, indent=1)

    jb.report(args.model, items, scores, detects, pairs, rubric, manip)


if __name__ == "__main__":
    main()
