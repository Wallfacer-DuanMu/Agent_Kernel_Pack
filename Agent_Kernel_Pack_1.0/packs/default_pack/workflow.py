from __future__ import annotations


class Workflow:
    def __init__(self) -> None:
        self.name = "default_workflow"
        self.stages = ("understand_task", "choose_action", "execute_tool", "summarize")
        self.default_allowed_tools = ("read_file", "list_dir", "search_text", "run_command")


WORKFLOW = Workflow()


def get_workflow() -> Workflow:
    return WORKFLOW
