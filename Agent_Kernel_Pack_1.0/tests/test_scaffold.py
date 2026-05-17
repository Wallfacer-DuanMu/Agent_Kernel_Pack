from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_main_py_exists() -> None:
    assert (ROOT / "main.py").exists()


def test_core_directories_exist() -> None:
    for folder in ["core", "capabilities", "policy", "tracing", "packs"]:
        assert (ROOT / folder).is_dir()


def test_key_modules_import() -> None:
    sys.path.insert(0, str(ROOT))
    __import__("core.config")
    __import__("core.runtime")
    __import__("capabilities.base")
    __import__("policy.decisions")
    __import__("tracing.logger")


def test_cli_version_runs() -> None:
    result = subprocess.run(
        [sys.executable, "main.py", "--version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip()
