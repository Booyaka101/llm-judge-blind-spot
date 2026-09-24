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
@kbench.task(name="score-padding", store_task=False)
def score_padding(llm, item_id) -> dict:
    return jb.judge_scores(jb.kaggle_ask(llm), BY_ID[item_id], ("clean", "padded"))


# %%
@kbench.task(name="judge-ignores-padding")
def judge_ignores_padding(llm) -> float:
    """Share of items where the correct answer, padded to twice its length with filler that
    adds nothing, does not score higher than the original."""
    return jb.padding_resistance(jb.evaluate_items(score_padding, llm, ITEMS))


judge_ignores_padding.run(kbench.llm)
