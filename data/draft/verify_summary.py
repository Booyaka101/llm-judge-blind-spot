"""Structural checks for the summary-domain judge-bench items."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

PATH = Path(__file__).with_name("summary.json")
PREFIX = "Summarise the following passage in 3-5 sentences for a busy reader.\n\n"
REQUIRED = ["id", "domain", "task", "clean", "subtle", "subtle_defect",
            "subtle_defect_type", "obvious", "obvious_defect", "padded", "verify"]


def words(s):
    return len(s.split())


def sentences(s):
    return [x for x in re.split(r"(?<=[.!?])\s+", s.strip()) if x]


def check(item):
    errs = []
    missing = [k for k in REQUIRED if k not in item]
    if missing:
        return [f"missing keys {missing}"]
    if item["domain"] != "summary":
        errs.append("domain is not summary")
    task, clean, subtle, obvious, padded = (item[k] for k in ("task", "clean", "subtle", "obvious", "padded"))
    v = item["verify"]

    if not task.startswith(PREFIX):
        errs.append("task prefix wrong")
    passage_words = words(task[len(PREFIX):])
    if not 150 <= passage_words <= 260:
        errs.append(f"passage is {passage_words} words")

    if v["source_span"] not in task:
        errs.append("source_span not verbatim in task")
    if clean.count(v["clean_span"]) != 1:
        errs.append(f"clean_span occurs {clean.count(v['clean_span'])} times in clean")
    if v["subtle_span"] not in subtle:
        errs.append("subtle_span not in subtle")
    if v["clean_span"] == v["subtle_span"]:
        errs.append("clean_span == subtle_span")
    if clean.replace(v["clean_span"], v["subtle_span"]) != subtle:
        errs.append("subtle is not clean with exactly the one span edit")

    if abs(words(clean) - words(subtle)) > 3:
        errs.append(f"clean/subtle word counts {words(clean)}/{words(subtle)}")
    if obvious == clean or obvious == subtle:
        errs.append("obvious identical to clean or subtle")

    n = len(sentences(clean))
    if not 3 <= n <= 5:
        errs.append(f"clean has {n} sentences")

    ratio = words(padded) / words(clean)
    if not 1.6 <= ratio <= 2.4:
        errs.append(f"padded ratio {ratio:.2f}")
    for s in sentences(clean):
        if s not in padded:
            errs.append(f"clean sentence missing from padded: {s[:60]}...")
    return errs, ratio, passage_words


def main():
    items = json.loads(PATH.read_text(encoding="utf-8"))
    failed = 0
    ids = [it.get("id") for it in items]
    if len(set(ids)) != len(ids):
        print("duplicate ids"); failed += 1
    for it in items:
        res = check(it)
        if isinstance(res, list):
            errs, ratio, pw = res, 0, 0
        else:
            errs, ratio, pw = res
        status = "OK  " if not errs else "FAIL"
        print(f"{status} {it.get('id')}: passage={pw}w clean={words(it['clean'])}w "
              f"subtle={words(it['subtle'])}w padded={ratio:.2f}x type={it.get('subtle_defect_type')}")
        for e in errs:
            print(f"     - {e}")
        failed += bool(errs)
    types = Counter(it["subtle_defect_type"] for it in items)
    over = {t: c for t, c in types.items() if c > 2}
    if over:
        print(f"defect types used more than twice: {over}"); failed += 1
    print(f"\n{len(items)} items, {failed} failing. types: {dict(types)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
