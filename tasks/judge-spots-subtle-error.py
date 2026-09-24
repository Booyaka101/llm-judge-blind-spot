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
@kbench.task(name="detect-item", store_task=False)
def detect_item(llm, item_id) -> dict:
    return jb.judge_detect(jb.kaggle_ask(llm), BY_ID[item_id])


# %%
@kbench.task(name="judge-spots-subtle-error")
def judge_spots_subtle_error(llm) -> float:
    """Balanced accuracy when asked directly whether an answer contains an error, over the
    correct answer and the one with a planted error."""
    return jb.detect_balanced_accuracy(jb.evaluate_items(detect_item, llm, ITEMS))


judge_spots_subtle_error.run(kbench.llm)
