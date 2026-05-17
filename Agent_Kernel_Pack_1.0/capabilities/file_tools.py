from __future__ import annotations

from pathlib import Path

from capabilities.base import RiskLevel, Tool

MAX_READ_CHARS = 4000


def read_file(args: dict[str, object]) -> dict[str, object]:
    path = Path(str(args.get("path", "")))
    if not path.exists():
        return {"ok": False, "error": f"Path not found: {path}"}
    if not path.is_file():
        return {"ok": False, "error": f"Not a file: {path}"}
    content = path.read_text(encoding="utf-8", errors="replace")
    truncated = content[:MAX_READ_CHARS]
    return {"ok": True, "path": str(path), "content": truncated, "truncated": len(content) > MAX_READ_CHARS}


def list_dir(args: dict[str, object]) -> dict[str, object]:
    path = Path(str(args.get("path", ".")))
    if not path.exists():
        return {"ok": False, "error": f"Path not found: {path}"}
    if not path.is_dir():
        return {"ok": False, "error": f"Not a directory: {path}"}
    items = sorted(item.name for item in path.iterdir())
    return {"ok": True, "path": str(path), "items": items[:200]}


READ_FILE_TOOL = Tool(name="read_file", description="Read a text file", risk_level=RiskLevel.low, handler=read_file)
LIST_DIR_TOOL = Tool(name="list_dir", description="List directory contents", risk_level=RiskLevel.low, handler=list_dir)
