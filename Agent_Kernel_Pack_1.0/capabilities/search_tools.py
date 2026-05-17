from __future__ import annotations

from pathlib import Path

from capabilities.base import RiskLevel, Tool


def search_text(args: dict[str, object]) -> dict[str, object]:
    query = str(args.get("query", "")).strip()
    root = Path(str(args.get("path", ".")))
    max_files = int(args.get("max_files", 50))
    max_results = int(args.get("max_results", 20))

    if not query:
        return {"ok": False, "error": "Query is required"}
    if not root.exists():
        return {"ok": False, "error": f"Path not found: {root}"}

    results: list[dict[str, object]] = []
    scanned = 0
    for file_path in root.rglob("*"):
        if scanned >= max_files or len(results) >= max_results:
            break
        if not file_path.is_file():
            continue
        scanned += 1
        try:
            text = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if query in text:
            results.append({"path": str(file_path), "match": query})

    return {"ok": True, "query": query, "path": str(root), "results": results, "scanned": scanned}


SEARCH_TEXT_TOOL = Tool(name="search_text", description="Search text in files", risk_level=RiskLevel.low, handler=search_text)
