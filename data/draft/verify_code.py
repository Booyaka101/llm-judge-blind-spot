"""Check every item in code.json: clean/padded pass, subtle/obvious fail, edits are minimal."""
import difflib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
BLOCK = re.compile(r"```python\n(.*?)```", re.DOTALL)
REQUIRED = {"id", "domain", "task", "clean", "subtle", "subtle_defect", "subtle_defect_type",
            "obvious", "obvious_defect", "padded", "verify"}
HASH_SEEDS = ("0", "1", "12345")

RUNNER = """
import sys
ns = {"__name__": "__candidate__"}
exec(compile(sys.argv[1], "<candidate>", "exec"), ns)
assert callable(ns.get(sys.argv[3])), "entry point missing"
exec(compile(sys.argv[2], "<tests>", "exec"), ns)
"""


def split(answer):
    blocks = BLOCK.findall(answer)
    assert len(blocks) == 1, f"expected one python block, found {len(blocks)}"
    return blocks[0].rstrip("\n"), BLOCK.sub("", answer).strip()


def passes(code, tests, entry):
    results = set()
    for seed in HASH_SEEDS:
        env = dict(os.environ, PYTHONHASHSEED=seed)
        try:
            proc = subprocess.run([sys.executable, "-c", RUNNER, code, tests, entry],
                                  env=env, capture_output=True, text=True, timeout=10)
            results.add(proc.returncode == 0)
        except subprocess.TimeoutExpired:
            results.add(False)
    assert len(results) == 1, "result depends on hash seed"
    return results.pop()


def changed_lines(a, b):
    diff = list(difflib.ndiff(a.splitlines(), b.splitlines()))
    removed = [d for d in diff if d.startswith("- ")]
    added = [d for d in diff if d.startswith("+ ")]
    return removed, added


def check(item):
    problems = []

    def expect(cond, msg):
        if not cond:
            problems.append(msg)

    expect(REQUIRED <= item.keys(), f"missing keys {REQUIRED - item.keys()}")
    expect(item["domain"] == "code", "domain is not 'code'")
    entry, tests = item["verify"]["entry_point"], item["verify"]["tests"]

    parts = {k: split(item[k]) for k in ("clean", "subtle", "obvious", "padded")}
    clean_code, clean_prose = parts["clean"]

    n_lines = len(clean_code.splitlines())
    expect(8 <= n_lines <= 30, f"clean code has {n_lines} lines")
    expect(not any(line.lstrip().startswith("#") or " # " in line
                   for line in clean_code.splitlines()), "clean code contains comments")
    n_sent = len(re.findall(r"[.!?](?:\s|$)", clean_prose))
    expect(2 <= n_sent <= 4, f"clean explanation has {n_sent} sentences")

    expect(passes(clean_code, tests, entry), "clean FAILS tests")
    expect(parts["padded"][0] == clean_code, "padded code differs from clean")
    expect(passes(parts["padded"][0], tests, entry), "padded FAILS tests")
    expect(not passes(parts["subtle"][0], tests, entry), "subtle PASSES tests")
    expect(not passes(parts["obvious"][0], tests, entry), "obvious PASSES tests")

    for variant in ("subtle", "obvious"):
        removed, added = changed_lines(clean_code, parts[variant][0])
        expect(len(removed) == 1 and len(added) == 1,
               f"{variant} changes {len(removed)} removed / {len(added)} added lines")
        expect(parts[variant][1] == clean_prose, f"{variant} prose differs from clean")

    ratio = len(parts["padded"][1].split()) / len(clean_prose.split())
    expect(1.6 <= ratio <= 2.0, f"padded prose ratio {ratio:.2f}")
    expect(clean_prose in parts["padded"][1], "padded does not contain the clean explanation")
    return problems, ratio


def main():
    items = json.loads((HERE / "code.json").read_text(encoding="utf-8"))
    ids = [it["id"] for it in items]
    failures = 0
    if len(set(ids)) != len(ids):
        print("duplicate ids")
        failures += 1
    for tag, n in Counter(it["subtle_defect_type"] for it in items).items():
        if n > 2:
            print(f"defect type {tag!r} used {n} times")
            failures += 1
    for it in items:
        problems, ratio = check(it)
        status = "ok" if not problems else "FAIL: " + "; ".join(problems)
        print(f"{it['id']:8} {it['subtle_defect_type']:26} pad x{ratio:.2f}  {status}")
        failures += bool(problems)
    print(f"\n{len(items)} items, {failures} failing")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
