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
    scores, detects, pairs = [], [], []
    try:
        for item in items:
            scores.append(jb.judge_scores(ask, item))
            detects.append(jb.judge_detect(ask, item))
            pairs.append(jb.judge_pairwise(ask, item))
    except Budget:
        print(f"budget hit after {len(scores)} complete items; re-run to continue")
        sys.exit(2)

    out = os.path.join(HERE, "results", f"pilot_{args.model.replace(':', '_').replace('/', '_')}.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"scores": scores, "detect": detects, "pairwise": pairs}, f, indent=1)

    unparsed = sum(r[v] is None for r in scores for v in ("clean", "subtle", "obvious", "padded"))
    unparsed += sum(r[v] is None for r in detects for v in ("clean", "subtle"))
    unparsed += sum(r[v] is None for r in pairs for v in ("clean_first", "clean_second"))
    missed, known = jb.knows_but_passes(scores, detects)
    print(f"model {args.model}, {len(items)} items, {unparsed} unparsed replies")
    print(f"  docks subtle      {jb.dock_rate(scores):.2f}")
    print(f"  docks obvious     {jb.dock_rate(scores, 'obvious'):.2f}")
    print(f"  padding resisted  {jb.padding_resistance(scores):.2f}")
    print(f"  detect bal. acc   {jb.detect_balanced_accuracy(detects):.2f}")
    print(f"  pairwise acc      {jb.pairwise_accuracy(pairs):.2f}")
    print(f"  knows but passes  {missed}/{known}")
    for domain in sorted({i["domain"] for i in items}):
        ids = {i["id"] for i in items if i["domain"] == domain}
        s = [r for r in scores if r["id"] in ids]
        d = [r for r in detects if r["id"] in ids]
        print(f"  [{domain}] dock {jb.dock_rate(s):.2f}  detect {jb.detect_balanced_accuracy(d):.2f}")


if __name__ == "__main__":
    main()
