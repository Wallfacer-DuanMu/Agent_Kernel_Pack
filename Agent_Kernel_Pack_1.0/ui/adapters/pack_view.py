from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.loader import PackLoader


ROOT = Path(__file__).resolve().parents[2]
PACKS_DIR = ROOT / "packs"
SAMPLE_SKILLS_DIR = ROOT / "ui" / "sample_skills"


@dataclass(frozen=True)
class PackSummary:
    name: str
    description: str
    manifest: dict[str, object]
    workflow: dict[str, Any] = field(default_factory=dict)
    policy: dict[str, Any] = field(default_factory=dict)
    tools: list[dict[str, Any]] = field(default_factory=list)
    prompts: dict[str, Any] = field(default_factory=dict)
    output: dict[str, Any] = field(default_factory=dict)
    skills: list[dict[str, Any]] = field(default_factory=list)


def list_available_packs() -> list[str]:
    if not PACKS_DIR.is_dir():
        return ["default_pack"]
    packs = [path.name for path in PACKS_DIR.iterdir() if path.is_dir()]
    return sorted(packs) or ["default_pack"]


def _read_manifest(pack_name: str) -> dict[str, object]:
    manifest_path = PACKS_DIR / pack_name / "manifest.json"
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _coerce_skill(skill: Any) -> dict[str, Any] | None:
    if not isinstance(skill, dict):
        return None
    name = str(skill.get("name", "")).strip()
    description = str(skill.get("description", "")).strip()
    steps = skill.get("steps") if isinstance(skill.get("steps"), list) else []
    if not name or not description or not steps:
        return None
    return {
        "name": name,
        "description": description,
        "triggers": skill.get("triggers") if isinstance(skill.get("triggers"), list) else [],
        "recommended_tools": skill.get("recommended_tools") if isinstance(skill.get("recommended_tools"), list) else [],
        "steps": steps,
        "output_format": skill.get("output_format", ""),
    }


def _load_builtin_skills(pack_name: str, manifest: dict[str, object]) -> list[dict[str, Any]]:
    builtin: list[dict[str, Any]] = []
    raw_skills = manifest.get("skills", []) if isinstance(manifest.get("skills", []), list) else []
    for skill in raw_skills:
        coerced = _coerce_skill(skill)
        if coerced and coerced["name"] and coerced["description"] and coerced["steps"]:
            builtin.append(coerced)

    sample_files = sorted(SAMPLE_SKILLS_DIR.glob("*.json")) if SAMPLE_SKILLS_DIR.is_dir() else []
    for sample in sample_files:
        try:
            payload = json.loads(sample.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        coerced = _coerce_skill(payload)
        if coerced and coerced["name"] and coerced["description"] and coerced["steps"]:
            builtin.append({**coerced, "source": f"sample:{sample.name}", "pack": pack_name})
    return builtin


def get_pack_summary(pack_name: str) -> PackSummary:
    manifest = _read_manifest(pack_name)
    loader = PackLoader()
    workflow: dict[str, Any] = {}
    policy: dict[str, Any] = {}
    prompts: dict[str, Any] = {}
    output: dict[str, Any] = {}
    tools: list[dict[str, Any]] = []

    try:
        loaded_pack = loader.load_pack(pack_name)
        workflow_obj = loaded_pack.workflow
        workflow = {
            "name": getattr(workflow_obj, "name", "unknown"),
            "stages": list(getattr(workflow_obj, "stages", [])),
            "allowed_tools": list(getattr(workflow_obj, "default_allowed_tools", [])),
            "completion_conditions": getattr(workflow_obj, "completion_conditions", []),
        }
        policy = {
            "rules": [
                {"name": getattr(rule, "name", "rule"), "description": getattr(rule, "description", "")}
                for rule in loaded_pack.policy_rules
            ],
            "effective_policy": "Kernel Policy + Pack Policy",
        }
        tools = [
            {
                "name": tool.name,
                "source": "pack",
                "risk_level": getattr(tool.risk_level, "value", str(tool.risk_level)),
                "args_schema": tool.args_schema,
            }
            for tool in []
        ]
        prompts = {
            "system_prompt": loaded_pack.prompts or "",
            "task_prompt_template": "Describe the task for the current pack.",
            "skill_hint_prompt": "",
        }
        output = {
            "renderer_name": getattr(loaded_pack.output_renderer, "__name__", "render"),
            "format": "text",
            "sections": ["summary"],
            "preview": "",
        }
    except Exception:
        pass

    description = str(manifest.get("description", "Pack information is not available yet."))
    skills = _load_builtin_skills(pack_name, manifest)

    return PackSummary(
        name=pack_name,
        description=description,
        manifest=manifest,
        workflow=workflow,
        policy=policy,
        tools=tools,
        prompts=prompts,
        output=output,
        skills=skills,
    )
