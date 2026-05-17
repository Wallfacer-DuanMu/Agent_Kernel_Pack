from __future__ import annotations


class PackPolicyRule:
    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description


def get_policy_rules() -> list[PackPolicyRule]:
    return []
