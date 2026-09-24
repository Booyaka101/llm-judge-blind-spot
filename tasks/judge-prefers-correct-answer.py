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
@kbench.task(name="pair-item", store_task=False)
def pair_item(llm, item_id) -> dict:
    return jb.judge_pairwise(jb.kaggle_ask(llm), BY_ID[item_id])


# %%
@kbench.task(name="judge-prefers-correct-answer")
def judge_prefers_correct_answer(llm) -> float:
    """Share of items where the correct answer beats the one with a planted error side by
    side, in both presentation orders."""
    return jb.pairwise_accuracy(jb.evaluate_items(pair_item, llm, ITEMS))


judge_prefers_correct_answer.run(kbench.llm)
