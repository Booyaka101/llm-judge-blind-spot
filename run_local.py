"""Execute a Kaggle task file locally, unmodified, with kbench.llm swapped for a local
backend and /kaggle/input redirected to ./data.

    python run_local.py tasks/judge-docks-subtle-error.py --stub
    python run_local.py tasks/judge-docks-subtle-error.py --ollama qwen2.5:32b
    python run_local.py tasks/judge-docks-subtle-error.py --proxy openai/gpt-5.4-nano-2026-03-17

--proxy goes through the Kaggle model proxy with the credentials `kaggle b init` wrote
to .env, so it spends real quota.
"""

import argparse
import glob
import os
import runpy

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

import kaggle_benchmarks as kbench  # noqa: E402  reads the proxy settings on import
from kaggle_benchmarks.actors.llms import LLMChat, LLMResponse  # noqa: E402

from pilot import make_ask  # noqa: E402

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
    ap.add_argument("--proxy")
    ap.add_argument("--data", default=os.path.join(HERE, "data", "kaggle"))
    args = ap.parse_args()

    if args.proxy:
        kbench.llm = kbench.llms[args.proxy]
    else:
        ask = stub_ask if args.stub else make_ask(args.ollama, None)
        kbench.llm = LocalChat(ask, args.ollama or "stub")

    real_glob = glob.glob
    glob.glob = lambda p, **kw: real_glob(p.replace("/kaggle/input", args.data), **kw)
    runpy.run_path(args.task_file, run_name="__main__")


if __name__ == "__main__":
    main()
