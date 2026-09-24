"""Check every item in math.json against its own ground truth.

Exits non-zero on the first batch of failures; prints a per-item summary otherwise.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

TOL = 1e-6
KEYS = {"id", "domain", "task", "clean", "subtle", "subtle_defect", "subtle_defect_type",
        "obvious", "obvious_defect", "padded", "verify"}
FINAL = re.compile(r"Final answer:\s*(-?\d+(?:\.\d+)?)\s*$", re.M)
# "<expr> = <number>" where expr is digits, spaces and + - × ÷ * / ( ) and starts with a digit or "(".
EQ = re.compile(r"([\d(][\d.\s+\-×÷*/()]*?)\s*=\s*(-?\d+(?:\.\d+)?)\s*$")


def final_answer(text):
    found = FINAL.findall(text)
    if len(found) != 1:
        raise ValueError(f"expected exactly one 'Final answer:' line, found {len(found)}")
    return float(found[0])


def check_lines(text):
    """Return (checked, wrong) where wrong lists (line_no, line, lhs value)."""
    checked, wrong = 0, []
    for i, line in enumerate(text.split("\n"), 1):
        if "=" not in line:
            continue
        m = EQ.search(line)
        if not m or not re.search(r"[+\-×÷*/]", m.group(1).strip()):
            raise ValueError(f"unparseable arithmetic line {i}: {line!r}")
        lhs = eval(m.group(1).replace("×", "*").replace("÷", "/"), {"__builtins__": {}})
        checked += 1
        if abs(lhs - float(m.group(2))) > TOL:
            wrong.append((i, line, lhs))
    return checked, wrong


def main():
    items = json.loads(Path(__file__).with_name("math.json").read_text(encoding="utf-8"))
    errors = []
    ids = Counter(it["id"] for it in items)
    errors += [f"duplicate id {k}" for k, v in ids.items() if v > 1]
    types = Counter(it["subtle_defect_type"] for it in items)
    errors += [f"defect type {k} used {v} times" for k, v in types.items() if v > 2]

    rows = []
    for it in items:
        iid = it["id"]

        def fail(msg):
            errors.append(f"{iid}: {msg}")

        if set(it) != KEYS:
            fail(f"keys mismatch: {sorted(set(it) ^ KEYS)}")
        if it["domain"] != "math":
            fail("domain is not math")
        v = it["verify"]
        ns = {}
        exec(v["python"], ns)
        if abs(ns["ans"] - v["answer_clean"]) > TOL:
            fail(f"python ans {ns['ans']} != answer_clean {v['answer_clean']}")

        try:
            fa = {k: final_answer(it[k]) for k in ("clean", "padded", "subtle", "obvious")}
        except ValueError as e:
            fail(str(e))
            continue
        if abs(fa["clean"] - v["answer_clean"]) > TOL:
            fail(f"clean final {fa['clean']} != answer_clean")
        if abs(fa["padded"] - v["answer_clean"]) > TOL:
            fail(f"padded final {fa['padded']} != answer_clean")
        if abs(fa["subtle"] - v["answer_subtle"]) > TOL:
            fail(f"subtle final {fa['subtle']} != answer_subtle")
        if abs(fa["subtle"] - v["answer_clean"]) <= TOL:
            fail("subtle final equals answer_clean")
        if abs(fa["obvious"] - v["answer_clean"]) <= TOL:
            fail("obvious final equals answer_clean")

        clean_lines = it["clean"].split("\n")
        subtle_lines = it["subtle"].split("\n")
        if len(clean_lines) != len(subtle_lines):
            fail(f"line count clean {len(clean_lines)} != subtle {len(subtle_lines)}")
        diff_lines = sum(a != b for a, b in zip(clean_lines, subtle_lines))

        try:
            n_clean, wrong_clean = check_lines(it["clean"])
            n_subtle, wrong_subtle = check_lines(it["subtle"])
        except ValueError as e:
            fail(str(e))
            continue
        if n_clean < 3:
            fail(f"only {n_clean} checkable lines in clean")
        for ln, line, lhs in wrong_clean:
            fail(f"clean line {ln} wrong ({lhs}): {line}")
        expected = 1 if it["subtle_defect_type"].startswith("arith-") else 0
        if len(wrong_subtle) != expected:
            fail(f"subtle has {len(wrong_subtle)} wrong lines, expected {expected} "
                 f"for {it['subtle_defect_type']}: {wrong_subtle}")

        # obvious: same steps as clean, only the final line changed, and it contradicts the line above
        ob_lines = it["obvious"].split("\n")
        if ob_lines[:-1] != clean_lines[:-1] or ob_lines[-1] == clean_lines[-1]:
            fail("obvious should differ from clean only in the final line")
        above = float(EQ.search(ob_lines[-2]).group(2))
        if abs(above - fa["obvious"]) <= TOL:
            fail("obvious final does not contradict the line above")

        # padded: every clean line verbatim, no new arithmetic, ~2x words
        for line in clean_lines:
            if line not in it["padded"]:
                fail(f"padded is missing clean line: {line}")
        if it["padded"].count("=") != it["clean"].count("="):
            fail("padded adds or drops '=' lines")
        ratio = len(it["padded"].split()) / len(it["clean"].split())
        if not 1.6 <= ratio <= 2.2:
            fail(f"padded word ratio {ratio:.2f} outside 1.6-2.2")

        rows.append((iid, it["subtle_defect_type"], n_clean, [w[0] for w in wrong_subtle],
                     diff_lines, ratio, fa["clean"], fa["subtle"], fa["obvious"]))

    print(f"{'id':8} {'subtle_defect_type':36} chk wrong_lines diff ratio  clean      subtle     obvious")
    for r in rows:
        print(f"{r[0]:8} {r[1]:36} {r[2]:3} {str(r[3]):11} {r[4]:4} {r[5]:4.2f}  "
              f"{r[6]:<10g} {r[7]:<10g} {r[8]:<10g}")
    n_setup = sum(1 for it in items if not it["subtle_defect_type"].startswith("arith-"))
    print(f"\n{len(items)} items, {n_setup} setup slips, {len(items) - n_setup} arithmetic slips")
    if errors:
        print("\nFAIL")
        for e in errors:
            print("  " + e)
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
