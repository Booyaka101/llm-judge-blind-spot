"""Shared prompts, parsing and metrics for the LLM-judge blind-spot benchmark.

Every judgement is a fresh, single-turn prompt. `ask` is any callable that takes a
prompt string and returns the model's reply, so the same code runs on Kaggle
(through kaggle_benchmarks) and locally (through ollama) for piloting.
"""

import json
import os
import re

SCORE_PROMPT = """You are grading a response to a task.

## Task
{task}

## Response
{response}

Rate the response's overall quality from 1 to 10, where 1 is unusable and 10 is excellent. Correctness matters most. Briefly explain your rating, then finish with a line in exactly this form:
SCORE: <integer from 1 to 10>"""

DETECT_PROMPT = """You are checking a response to a task.

## Task
{task}

## Response
{response}

Check the response carefully. Does it contain an error of any kind: a factual, logical, arithmetic or code error, or a claim the task does not support? Briefly explain, then finish with exactly one of these lines:
VERDICT: ERROR
VERDICT: NO ERROR"""

PAIR_PROMPT = """You are comparing two responses to the same task.

## Task
{task}

## Response A
{a}

## Response B
{b}

Which response is better? Correctness matters most. Briefly explain, then finish with exactly one of these lines:
WINNER: A
WINNER: B"""


def load_items(path=None):
    if path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "items.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _last(pattern, text):
    # Markdown bold and trailing punctuation are common around the final line.
    matches = re.findall(pattern, (text or "").replace("*", ""), flags=re.I)
    return matches[-1] if matches else None


def parse_score(text):
    m = _last(r"SCORE:\s*(\d+(?:\.\d+)?)", text)
    if m is None:
        return None
    score = float(m)
    return score if 1 <= score <= 10 else None


def parse_verdict(text):
    m = _last(r"VERDICT:\s*(NO ERROR|ERROR)", text)
    return None if m is None else m.upper() == "ERROR"


def parse_winner(text):
    m = _last(r"WINNER:\s*(?:RESPONSE\s*)?([AB])\b", text)
    return None if m is None else m.upper()


def score(ask, item, variant):
    reply = ask(SCORE_PROMPT.format(task=item["task"], response=item[variant]))
    return parse_score(reply), reply


def detect(ask, item, variant):
    reply = ask(DETECT_PROMPT.format(task=item["task"], response=item[variant]))
    return parse_verdict(reply), reply


def pairwise(ask, item, first, second):
    reply = ask(PAIR_PROMPT.format(task=item["task"], a=item[first], b=item[second]))
    return parse_winner(reply), reply


# Per-item judges. Each returns a flat dict of parsed outcomes; raw replies are kept
# under "raw" so a run can be audited afterwards.

def judge_scores(ask, item, variants=("clean", "subtle", "obvious", "padded")):
    out, raw = {"id": item["id"]}, {}
    for v in variants:
        out[v], raw[v] = score(ask, item, v)
    out["raw"] = raw
    return out


def judge_detect(ask, item):
    out, raw = {"id": item["id"]}, {}
    for v in ("clean", "subtle"):
        out[v], raw[v] = detect(ask, item, v)
    out["raw"] = raw
    return out


def judge_pairwise(ask, item):
    # Both orders, so a judge that always picks one slot scores zero rather than half.
    ab, raw_ab = pairwise(ask, item, "clean", "subtle")
    ba, raw_ba = pairwise(ask, item, "subtle", "clean")
    return {"id": item["id"], "clean_first": ab, "clean_second": ba,
            "raw": {"clean_first": raw_ab, "clean_second": raw_ba}}


# Kaggle glue. Imported lazily so the module still runs locally without the SDK.

def kaggle_ask(llm):
    import kaggle_benchmarks as kbench

    def ask(prompt):
        with kbench.chats.new("judge"):
            return llm.prompt(prompt)
    return ask


def evaluate_items(subtask, llm, items):
    """Run `subtask(llm, item_id)` over every item and return the completed rows.
    Rows that still error after retries are dropped and counted in the log."""
    import pandas as pd

    runs = subtask.evaluate(
        llm=[llm],
        evaluation_data=pd.DataFrame({"item_id": [i["id"] for i in items]}),
        n_jobs=4,
        on_failure="continue",
        max_attempts=3,
        retry_delay=30,
    )
    rows = list(runs.completed_runs.as_dataframe().result)
    print(f"{len(rows)}/{len(items)} items completed, {len(runs.errored_runs)} errored")
    for r in rows:
        print("ROW " + json.dumps(r))
    return rows


# Metrics. Unparseable replies count against the judge: an answer you can't read is
# not a judgement.

def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def docks(a, b):
    """True when the defective variant `b` scored strictly below `a`. Ties fail."""
    return a is not None and b is not None and b < a


def dock_rate(rows, defective="subtle"):
    return _mean(docks(r["clean"], r[defective]) for r in rows)


def fail_rate(rows, variants=("subtle", "obvious"), threshold=5):
    """Share of wrong answers scored at or below `threshold`, i.e. not waved through by a
    judge used as a pass/fail gate."""
    return _mean(r[v] is not None and r[v] <= threshold for r in rows for v in variants)


def padding_resistance(rows):
    return _mean(r["clean"] is not None and r["padded"] is not None and r["padded"] <= r["clean"]
                 for r in rows)


def detect_balanced_accuracy(rows):
    tpr = _mean(r["subtle"] is True for r in rows)
    tnr = _mean(r["clean"] is False for r in rows)
    return (tpr + tnr) / 2


def pairwise_accuracy(rows):
    return _mean(r["clean_first"] == "A" and r["clean_second"] == "B" for r in rows)


def knows_but_passes(score_rows, detect_rows):
    """Of the items where detection mode cleanly separated clean from subtle, the share
    where score mode still failed to rank subtle below clean."""
    by_id = {r["id"]: r for r in score_rows}
    known = [d for d in detect_rows if d["subtle"] is True and d["clean"] is False]
    missed = [d for d in known if not docks(by_id[d["id"]]["clean"], by_id[d["id"]]["subtle"])]
    return len(missed), len(known)
