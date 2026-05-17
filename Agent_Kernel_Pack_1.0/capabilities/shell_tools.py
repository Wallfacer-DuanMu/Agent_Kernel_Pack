from __future__ import annotations

import subprocess

from capabilities.base import RiskLevel, Tool


def run_command(args: dict[str, object]) -> dict[str, object]:
    command = str(args.get("command", "")).strip()
    timeout = int(args.get("timeout", 5))
    if not command:
        return {"ok": False, "error": "Command is required"}
    completed = subprocess.run(command, shell=False, capture_output=True, text=True, timeout=timeout)
    return {
        "ok": True,
        "command": command,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "exit_code": completed.returncode,
    }


RUN_COMMAND_TOOL = Tool(name="run_command", description="Run a safe command", risk_level=RiskLevel.high, handler=run_command)
