from core.actions import Action, ActionType, parse_action


def test_action_creation() -> None:
    action = Action(type=ActionType.respond, content="hello")
    assert action.type is ActionType.respond
    assert action.content == "hello"


def test_parse_action_from_dict() -> None:
    action = parse_action({"type": "finish", "content": "done"})
    assert action.type is ActionType.finish
    assert action.content == "done"
