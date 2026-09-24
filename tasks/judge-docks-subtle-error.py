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
    return jb.judge_scores(jb.kaggle_ask(llm), BY_ID[item_id], ("clean", "subtle", "obvious"))


# %%
@kbench.task(name="judge-docks-subtle-error")
def judge_docks_subtle_error(llm) -> float:
    """Share of items where a 1-10 score for the answer with one planted error is strictly
    lower than the score for the correct answer. Each answer is scored alone, as judges
    are used in practice."""
    rows = jb.evaluate_items(score_item, llm, ITEMS)
    print(f"docks obvious error: {jb.dock_rate(rows, 'obvious'):.3f}")
    return jb.dock_rate(rows)


judge_docks_subtle_error.run(kbench.llm)
