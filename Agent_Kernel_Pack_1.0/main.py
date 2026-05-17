from __future__ import annotations

import argparse

from core.config import VERSION
from core.llm_config import load_llm_config
from core.loader import PackLoaderError
from core.runtime import AgentRuntime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-kernel", description="Lightweight experimental Agent Kernel")
    parser.add_argument("task", nargs="?", help="Optional task to initialize")
    parser.add_argument("--pack", default="default_pack", help="Pack name or path to load")
    parser.add_argument("--yes", action="store_true", help="Auto-confirm safe shell actions")
    parser.add_argument("--trace-dir", default="traces", help="Directory for trace output")
    parser.add_argument("--mock", action="store_true", help="Force local mock runtime; otherwise persisted LLM config is used when enabled")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        llm_settings = None
        if args.mock:
            from core.llm import LLMSettings

            llm_settings = LLMSettings(enabled=False)
        else:
            llm_settings = load_llm_config()
        if args.task:
            runtime = AgentRuntime(auto_confirm=args.yes, trace_dir=args.trace_dir, pack_name_or_path=args.pack, llm_settings=llm_settings)
            print(runtime.run(args.task))
        else:
            print("Agent Kernel initialized.")
        print(f"Pack: {args.pack}")
        print(f"Decision mode: {'mock' if args.mock or not llm_settings.enabled else 'llm'}")
        return 0
    except PackLoaderError as exc:
        print(f"Pack load error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
