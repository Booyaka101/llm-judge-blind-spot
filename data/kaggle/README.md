# LLM judge blind spot

42 items for testing language models used as judges: 14 code, 14 math, 14 summary-faithfulness.

Each item has a task and four answers:

- `clean`: correct.
- `subtle`: the clean answer with one minimal planted error (one changed code line, one slipped step carried through, one changed span in a summary). The error is provable from the task text alone.
- `obvious`: the clean answer with one blatant error.
- `padded`: the clean answer made about twice as long with filler that adds no information.

`subtle_defect` and `obvious_defect` describe each planted error. Code items carry unit tests (clean passes, subtle and obvious fail), math items carry a program that recomputes the correct answer, and summary items carry the exact source span the subtle edit contradicts. Summary passages are about fictional organisations so world knowledge can't help or hurt.

`judgebench.py` holds the prompts, reply parsing and metrics used by the Kaggle Benchmarks tasks.
