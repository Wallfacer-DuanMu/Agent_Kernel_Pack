from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ui.components.skill_importer import validate_skill


def test_valid_skill_passes_validation() -> None:
    payload = {
        "name": "sample_skill",
        "description": "A valid skill.",
        "steps": ["step one", "step two"],
        "recommended_tools": ["read_file"],
        "triggers": ["demo"],
    }
    ok, message = validate_skill(payload)
    assert ok is True
    assert "valid" in message.lower()


def test_skill_missing_name_fails() -> None:
    payload = {
        "description": "Missing name.",
        "steps": ["step one"],
    }
    ok, message = validate_skill(payload)
    assert ok is False
    assert "name" in message.lower()


def test_skill_steps_must_be_list() -> None:
    payload = {
        "name": "bad_skill",
        "description": "Invalid steps.",
        "steps": "not a list",
    }
    ok, message = validate_skill(payload)
    assert ok is False
    assert "steps" in message.lower()


def test_sample_skill_file_can_be_read() -> None:
    sample_path = ROOT / "ui" / "sample_skills" / "diagnose_cli_error.json"
    payload = json.loads(sample_path.read_text(encoding="utf-8"))
    ok, message = validate_skill(payload)
    assert ok is True
    assert message
