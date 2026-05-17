from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Callable


class PackLoaderError(RuntimeError):
    pass


@dataclass
class LoadedPack:
    name: str
    version: str
    description: str = ""
    workflow: Any | None = None
    policy_rules: list[Any] = field(default_factory=list)
    register_tools: Callable[[Any], Any] | None = None
    output_renderer: Callable[[Any, Any], str] | None = None
    prompts: Any = None


@dataclass
class PackLoader:
    project_root: Path | None = None

    def __post_init__(self) -> None:
        if self.project_root is None:
            self.project_root = Path(__file__).resolve().parents[1]

    def _pack_root(self) -> Path:
        assert self.project_root is not None
        return self.project_root / "packs"

    def load_pack(self, pack_name_or_path: str) -> LoadedPack:
        pack_path = self._resolve_pack_path(pack_name_or_path)
        manifest = self.load_manifest(pack_path)
        self.validate_manifest(manifest, pack_path)

        entry = manifest["entry"]
        workflow_mod = self.load_module(pack_path, entry["workflow"])
        policy_mod = self.load_module(pack_path, entry["policy"])
        tools_mod = self.load_module(pack_path, entry["tools"])
        output_mod = self.load_module(pack_path, entry["output"])
        prompts_mod = self.load_module(pack_path, entry["prompts"])

        workflow = getattr(workflow_mod, "WORKFLOW", None)
        if workflow is None and hasattr(workflow_mod, "get_workflow"):
            workflow = workflow_mod.get_workflow()

        policy_rules = []
        if hasattr(policy_mod, "get_policy_rules"):
            policy_rules = list(policy_mod.get_policy_rules())
        elif hasattr(policy_mod, "POLICY_RULES"):
            policy_rules = list(policy_mod.POLICY_RULES)

        register_tools = getattr(tools_mod, "register_tools", None)
        output_renderer = getattr(output_mod, "render", None)
        prompts = getattr(prompts_mod, "SYSTEM_PROMPT", None)
        if prompts is None:
            prompts = getattr(prompts_mod, "DEFAULT_PROMPT", None)

        return LoadedPack(
            name=manifest["name"],
            version=manifest["version"],
            description=manifest.get("description", ""),
            workflow=workflow,
            policy_rules=policy_rules,
            register_tools=register_tools,
            output_renderer=output_renderer,
            prompts=prompts,
        )

    def load_manifest(self, pack_path: Path) -> dict[str, Any]:
        manifest_path = pack_path / "manifest.json"
        if not manifest_path.exists():
            raise PackLoaderError(f"Pack manifest not found: {manifest_path}")
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PackLoaderError(f"Invalid manifest JSON: {manifest_path}") from exc

    def validate_manifest(self, manifest: dict[str, Any], pack_path: Path) -> None:
        for key in ("name", "version", "entry"):
            if key not in manifest or not manifest[key]:
                raise PackLoaderError(f"Manifest missing required field '{key}' in {pack_path}")
        entry = manifest["entry"]
        if not isinstance(entry, dict):
            raise PackLoaderError(f"Manifest field 'entry' must be an object in {pack_path}")
        for key in ("workflow", "policy", "tools", "output", "prompts"):
            if key not in entry or not entry[key]:
                raise PackLoaderError(f"Manifest entry missing required field '{key}' in {pack_path}")
            if not (pack_path / entry[key]).exists():
                raise PackLoaderError(f"Manifest entry file not found: {(pack_path / entry[key])}")

    def load_module(self, pack_path: Path, entry_file: str) -> ModuleType:
        module_path = pack_path / entry_file
        if not module_path.exists():
            raise PackLoaderError(f"Pack module not found: {module_path}")
        module_name = f"pack_{pack_path.name}_{module_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise PackLoaderError(f"Unable to load pack module: {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _resolve_pack_path(self, pack_name_or_path: str) -> Path:
        candidate = Path(pack_name_or_path)
        if candidate.exists():
            if candidate.is_dir():
                return candidate.resolve()
            raise PackLoaderError(f"Pack path is not a directory: {candidate}")

        pack_path = self._pack_root() / pack_name_or_path
        if pack_path.exists() and pack_path.is_dir():
            return pack_path.resolve()
        raise PackLoaderError(f"Pack not found: {pack_name_or_path}")
