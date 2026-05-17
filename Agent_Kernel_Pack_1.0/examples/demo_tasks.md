# Demo Tasks

These commands are intended to be copied and run from the project root.

## Basic runs

```bash
python main.py "hello agent"
python main.py "list ."
python main.py "search Agent in README.md"
python main.py --pack default_pack "list ."
python main.py "run echo hello"
```

## Dangerous command example

```bash
python main.py "run rm -rf /"
```

This should be blocked by policy or require confirmation. It must not run directly.

## Trace check

After running a task, check the `traces/` directory for JSONL records.
