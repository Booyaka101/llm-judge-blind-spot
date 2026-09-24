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
@kbench.task(name="score-wrong", store_task=False)
def score_wrong(llm, item_id) -> dict:
    return jb.judge_scores(jb.kaggle_ask(llm), BY_ID[item_id], ("subtle", "obvious"))


# %%
@kbench.task(name="judge-fails-wrong-answers")
def judge_fails_wrong_answers(llm) -> float:
    """Share of wrong answers (one subtle and one obvious planted error per item) that get a
    failing score of 5 or below out of 10, scored alone as a pass/fail gate would."""
    rows = jb.evaluate_items(score_wrong, llm, ITEMS)
    print(f"fails subtle: {jb.fail_rate(rows, ('subtle',)):.3f}  fails obvious: {jb.fail_rate(rows, ('obvious',)):.3f}")
    return jb.fail_rate(rows)


judge_fails_wrong_answers.run(kbench.llm)
