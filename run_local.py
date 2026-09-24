"""Execute a Kaggle task file locally, unmodified, with kbench.llm swapped for a local
backend and /kaggle/input redirected to ./data.

    python run_local.py tasks/judge-docks-subtle-error.py --stub
    python run_local.py tasks/judge-docks-subtle-error.py --ollama qwen2.5:32b
"""

import argparse
import glob
import os
import runpy

import kaggle_benchmarks as kbench
from kaggle_benchmarks.actors.llms import LLMChat, LLMResponse

from pilot import make_ask

HERE = os.path.dirname(os.path.abspath(__file__))


class LocalChat(LLMChat):
    def __init__(self, ask, name):
        super().__init__(name=name)
        self._ask = ask

    def invoke(self, messages, system=None, **kwargs):
        # Every judgement runs in a fresh chat, so the last message is the whole prompt.
        return LLMResponse(content=self._ask(str(messages[-1].content)))


def stub_ask(prompt):
    if "WINNER:" in prompt:
        return "A is fine.\nWINNER: A"
    if "VERDICT:" in prompt:
        return "Looks off.\n**VERDICT: ERROR**"
    return "Decent.\nSCORE: 7"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task_file")
    ap.add_argument("--stub", action="store_true")
    ap.add_argument("--ollama")
    ap.add_argument("--data", default=os.path.join(HERE, "data", "kaggle"))
    args = ap.parse_args()

    ask = stub_ask if args.stub else make_ask(args.ollama, None)
    kbench.llm = LocalChat(ask, args.ollama or "stub")

    real_glob = glob.glob
    glob.glob = lambda p, **kw: real_glob(p.replace("/kaggle/input", args.data), **kw)
    runpy.run_path(args.task_file, run_name="__main__")


if __name__ == "__main__":
    main()
