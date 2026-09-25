# %%
import glob
import os
import sys

import kaggle_benchmarks as kbench

sys.path.insert(0, os.path.dirname(glob.glob("/kaggle/input/**/judgebench.py", recursive=True)[0]))
import judgebench as jb

ITEMS = jb.load_items(glob.glob("/kaggle/input/**/items.json", recursive=True)[0])
BY_ID = {i["id"]: i for i in ITEMS}


# %%
@kbench.task(name="score-item", store_task=False)
def score_item(llm, item_id) -> dict:
    return jb.judge_scores(jb.kaggle_ask(llm), BY_ID[item_id])


# %%
@kbench.task(name="judge-docks-planted-error")
def judge_docks_planted_error(llm) -> tuple[float, float]:
    """Share of items where the answer with one planted error scores strictly lower (1-10,
    each answer scored alone) than the correct answer. The log adds obvious errors, fail
    rates and padding."""
    rows = jb.evaluate_items(score_item, llm, ITEMS)
    jb.print_score_metrics(rows)
    return jb.dock_rate(rows)


judge_docks_planted_error.run(kbench.llm)
