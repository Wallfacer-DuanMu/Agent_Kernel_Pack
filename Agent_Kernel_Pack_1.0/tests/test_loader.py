from __future__ import annotations

from pathlib import Path

import pytest

from core.loader import PackLoader, PackLoaderError
from capabilities.registry import CapabilityRegistry


ROOT = Path(__file__).resolve().parents[1]


def test_default_pack_manifest_can_be_read() -> None:
    loader = PackLoader(ROOT)
    manifest = loader.load_manifest(ROOT / "packs" / "default_pack")
    assert manifest["name"] == "default_pack"
    assert manifest["version"]
    assert manifest["entry"]


def test_manifest_missing_field_raises_clear_error(tmp_path: Path) -> None:
    pack_path = tmp_path / "broken_pack"
    pack_path.mkdir()
    (pack_path / "manifest.json").write_text('{"name":"broken","entry":{}}', encoding="utf-8")
    loader = PackLoader(tmp_path)
    manifest = loader.load_manifest(pack_path)
    with pytest.raises(PackLoaderError, match="version"):
        loader.validate_manifest(manifest, pack_path)


def test_default_pack_loads_and_registers_tools() -> None:
    loader = PackLoader(ROOT)
    pack = loader.load_pack("default_pack")
    registry = CapabilityRegistry()
    assert pack.register_tools is not None
    pack.register_tools(registry)
    assert {"read_file", "list_dir", "search_text", "run_command"}.issubset(set(registry.list_tools()))


def test_pack_path_loading_works() -> None:
    loader = PackLoader(ROOT)
    pack = loader.load_pack(str(ROOT / "packs" / "default_pack"))
    assert pack.name == "default_pack"
