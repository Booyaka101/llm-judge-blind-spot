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
@kbench.task(name="rubric-score-item", store_task=False)
def rubric_score_item(llm, item_id) -> dict:
    return jb.judge_scores(jb.kaggle_ask(llm), BY_ID[item_id], ("clean", "subtle", "obvious"),
                           jb.RUBRIC_SCORE_PROMPT)


# %%
@kbench.task(name="judge-docks-with-rubric")
def judge_docks_with_rubric(llm) -> tuple[float, float]:
    """judge-docks-subtle-error again, but the grading prompt asks the judge to list errors
    before scoring and says an error caps the score at 4. Compare the two to see how much
    of the blind spot a rubric fixes."""
    rows = jb.evaluate_items(rubric_score_item, llm, ITEMS)
    jb.print_score_metrics(rows)
    return jb.dock_rate(rows)


judge_docks_with_rubric.run(kbench.llm)
