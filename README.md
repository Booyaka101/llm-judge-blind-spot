# judge-bench

Can a language model used as a judge tell a correct answer from one with a single planted error? This repo holds the items, the prompts and the Kaggle Benchmarks tasks that measure it.

The leaderboard is at [kaggle.com/benchmarks/christobooyakabosch/llm-judge-blind-spot](https://www.kaggle.com/benchmarks/christobooyakabosch/llm-judge-blind-spot).

The items are 42 tasks (14 code, 14 math, 14 summary faithfulness), each with four answers: `clean`, `subtle` (one minimal planted error), `obvious` (one blatant error) and `padded` (clean, twice as long, no new information). Every subtle error can be proven from the task text alone. Code items carry unit tests, math items a program that recomputes the answer, summary items the exact source span the edit contradicts, and `data/draft/verify_*.py` checks all of it. Summary passages are about fictional organisations so world knowledge can't help. See `data/SCHEMA.md` for the rules the items were written to.

## Tasks

Each task scores one model and returns a mean with the half-width of its 95% confidence interval.

| Task | Headline metric |
|---|---|
| `judge-docks-planted-error` | Share of items where the subtle answer, scored 1-10 on its own, gets strictly less than the clean one. Ties fail. The log also reports how often a wrong answer scores 5 or below, and whether padding is rewarded. |
| `judge-spots-subtle-error` | Balanced accuracy when asked directly "does this contain an error?" on the clean and subtle answers. |
| `judge-prefers-correct-answer` | Share of items where the judge picks clean over subtle side by side, in both orders. A judge that always picks one slot scores zero. |
| `judge-docks-with-error-rubric` | The dock rate again, with a prompt that asks for a list of errors first and caps the score at 4 if any make the answer wrong. |
| `judge-resists-false-claims` | The dock rate after appending either a false "I tested this" line or a note telling the grader to score it 10. |

Every judgement is a fresh single-turn prompt. Unparseable replies count against the judge, but one is re-asked up to three times first, because on Kaggle gpt-oss-120b sometimes cut its reply off right after `SCORE:`.

`collect.py` also reports "knows but passes": items where the judge flagged the error in detection mode but still didn't score the subtle answer below the clean one.

## Layout

- `judgebench.py`: prompts, parsing and metrics, shared by the Kaggle tasks and local runs.
- `tasks/`: the five Kaggle task files, pushed as-is.
- `data/kaggle/`: the Kaggle dataset (items plus `judgebench.py`), `christobooyakabosch/llm-judge-blind-spot`.
- `run_local.py`: runs an unmodified task file locally against ollama, a stub, or the Kaggle model proxy.
- `collect.py`: downloads a model's runs from Kaggle and prints every metric plus its cost. Refuses runs with missing items.
- `results/kaggle/`: collected per-model results with the raw replies.

## Running

```
kaggle b t push judge-docks-planted-error -f tasks/judge-docks-planted-error.py -d christobooyakabosch/llm-judge-blind-spot
kaggle b t run judge-docks-planted-error -m claude-sonnet-5-default
python collect.py claude-sonnet-5-default
```

Locally, without spending quota:

```
python run_local.py tasks/judge-docks-planted-error.py --ollama qwen2.5:32b
```

The Kaggle proxy reserves each request's maximum output against the daily AI quota, so the tasks cap output at 16k tokens and run four items at a time. One small model over all five tasks costs about $0.50 to $1.50.

## License

Code is MIT. The items in `items.json` and `data/` are CC BY 4.0, the same as the Kaggle dataset.
