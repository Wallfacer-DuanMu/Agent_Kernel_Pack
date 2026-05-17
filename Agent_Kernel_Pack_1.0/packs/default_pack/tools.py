from __future__ import annotations

from capabilities.file_tools import LIST_DIR_TOOL, READ_FILE_TOOL
from capabilities.registry import CapabilityRegistry
from capabilities.search_tools import SEARCH_TEXT_TOOL
from capabilities.shell_tools import RUN_COMMAND_TOOL


DEFAULT_TOOLS = (READ_FILE_TOOL, LIST_DIR_TOOL, SEARCH_TEXT_TOOL, RUN_COMMAND_TOOL)


def register_tools(registry: CapabilityRegistry) -> None:
    for tool in DEFAULT_TOOLS:
        if tool.name not in registry.tools:
            registry.register(tool)
