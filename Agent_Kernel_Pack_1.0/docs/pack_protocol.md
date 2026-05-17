# Pack Protocol

This document explains how to create a new Pack for Agent Kernel.

## Pack directory structure

```text
packs/
  my_pack/
    manifest.json
    workflow.py
    policy.py
    tools.py
    output.py
    prompts.py
```

## manifest.json

A Pack manifest must include:

- `name`
- `version`
- `kernel_version`
- `description`
- `entry`

Example:

```json
{
  "name": "my_pack",
  "version": "0.1.0",
  "kernel_version": "0.1",
  "description": "Example Pack",
  "entry": {
    "workflow": "workflow.py",
    "policy": "policy.py",
    "tools": "tools.py",
    "output": "output.py",
    "prompts": "prompts.py"
  }
}
```

## workflow.py

The workflow module should expose a workflow object or a getter:

- `WORKFLOW`
- or `get_workflow()`

The current runtime loads it as Pack metadata, so keep it simple and stable.

## policy.py

The policy module should expose one of the following:

- `get_policy_rules()`
- or `POLICY_RULES`

Return a list of policy rules that can extend the core guard.

## tools.py

The tools module should expose:

- `register_tools(registry)`

This function receives the capability registry and registers Pack tools.

## output.py

The output module should expose:

- `render(result, state)`

This function formats the final result for display.

## prompts.py

The prompts module should expose one of:

- `SYSTEM_PROMPT`
- `DEFAULT_PROMPT`

The runtime prepends this prompt to the step context when available.

## Minimal Pack example

```python
# tools.py
from capabilities.file_tools import register_file_tools
from capabilities.search_tools import register_search_tools
from capabilities.shell_tools import register_shell_tools


def register_tools(registry):
    register_file_tools(registry)
    register_search_tools(registry)
    register_shell_tools(registry)
```

```python
# output.py

def render(result, state):
    return result
```

```python
# prompts.py
SYSTEM_PROMPT = "You are a lightweight Agent Kernel Pack."
```

Keep the Pack small, explicit, and easy to inspect.
