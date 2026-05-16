# Pack Protocol

## Purpose of This Document

This document defines what a **Pack** is in `Mini Agent Kernel`, how it communicates with the Kernel, and how Pack contributions are loaded into Kernel subsystems.

The Pack protocol is the central extension mechanism of this project.

---

## Short Definition

In this project:

> A Pack is an external behavior package that declares scenario-specific prompts, tools, policy extensions, workflow hints, output preferences, examples, and metadata. A Pack does not replace the Kernel. It is validated and assembled by the Kernel through a structured protocol.

A Pack defines **what kind of Agent the Kernel becomes**.

The Kernel defines **how the Agent runs**.

---

## Why Pack Is Not Just a Prompt

A weak design would be to load a Pack by simply injecting a sentence into the prompt:

```text
You are now working inside research_pack.
```

This is not enough.

It is too implicit and too fragile because:

- tools are not formally registered;
- policy behavior is not enforceable;
- workflow preferences are not inspectable;
- frontend cannot display structured Pack information;
- invalid Pack definitions cannot be rejected safely;
- model output becomes the only control surface.

In this project, Pack communication is not only prompt injection.

It uses three layers:

```text
1. Load-time structured contribution
2. Runtime subsystem registration
3. Context injection for decision making
```

---

## Three Communication Layers Between Kernel and Pack

### Layer 1: Load-time Structured Contribution

When a Pack is loaded, the Kernel reads its manifest and calls its registration entry.

The Pack returns a structured `PackContribution` object.

This happens before the Agent loop uses the Pack.

```text
PackLoader.load(pack_name)
  -> read manifest
  -> validate compatibility
  -> call register_pack()
  -> validate PackContribution
  -> prepare runtime registration
```

This layer is not natural language communication. It is system-level assembly.

---

### Layer 2: Runtime Subsystem Registration

After validation, the Kernel distributes Pack contributions into different subsystems.

```text
PackContribution.metadata           -> State.active_pack
PackContribution.prompts            -> ContextBuilder
PackContribution.tools              -> ToolRegistry
PackContribution.policy_extensions  -> PolicyEngine
PackContribution.workflow_hints     -> RuntimeContext / ContextBuilder
PackContribution.output_style       -> ResponseRenderer / ContextBuilder
PackContribution.examples           -> ContextBuilder
```

This is the most important design point:

> A Pack is not passed to the Agent loop as one large blob. It is decomposed into structured contributions and registered into the appropriate Kernel subsystems.

---

### Layer 3: Context Injection

During each Agent turn, the Context Builder includes selected Pack information in the runtime context.

For example:

```text
active Pack metadata
Pack prompt additions
available Pack tools
workflow hints
policy summary
output preferences
few-shot examples
```

For an LLM Decision Provider, these may be rendered into a prompt and tool schema.

For a Rule Decision Provider, they may be read directly as structured fields.

Context injection is important, but it is only one layer of the communication design.

---

## Pack Directory Structure

A minimal Pack should look like this:

```text
packs/
└─ default_pack/
   ├─ manifest.json
   └─ pack.py
```

A future project may support additional files, but v0.1 should keep the structure simple.

---

## Manifest

Each Pack must provide a `manifest.json` file.

Example:

```json
{
  "name": "default_pack",
  "version": "0.1.0",
  "kernel_version": ">=0.1.0",
  "description": "The default baseline Pack for Mini Agent Kernel.",
  "entry": "pack.py",
  "capabilities": {
    "prompts": true,
    "tools": true,
    "policy_extensions": true,
    "workflow_hints": true,
    "output_style": true,
    "examples": false
  }
}
```

### Required Manifest Fields

```text
name
version
kernel_version
description
entry
```

### Optional Manifest Fields

```text
capabilities
author
tags
homepage
license
```

---

## Pack Registration Entry

Each Pack must expose a standard registration function.

Example:

```python
def register_pack():
    return {
        "metadata": {},
        "prompts": {},
        "tools": [],
        "policy_extensions": [],
        "workflow_hints": {},
        "output_style": {},
        "examples": []
    }
```

The returned object is called `PackContribution`.

---

## PackContribution

A `PackContribution` is the structured object returned by a Pack.

Recommended v0.1 shape:

```text
PackContribution
├─ metadata
├─ prompts
├─ tools
├─ policy_extensions
├─ workflow_hints
├─ output_style
└─ examples
```

Each field has a different destination inside the Kernel.

---

## metadata

`metadata` describes the Pack at runtime.

Example:

```json
{
  "display_name": "Default Assistant",
  "description": "A baseline general-purpose assistant Pack.",
  "category": "general"
}
```

Destination:

```text
State.active_pack
Frontend Pack display
Trace events
```

---

## prompts

`prompts` provides prompt additions or behavior rules.

Example:

```json
{
  "system_addition": "You are running as a concise general assistant.",
  "behavior_rules": [
    "Answer directly when no tool is needed.",
    "Use tools only when the user asks for environment inspection.",
    "Ask a clarifying question when the task is ambiguous."
  ]
}
```

Destination:

```text
ContextBuilder
DecisionProvider input
```

Important:

The Pack should not provide the entire final system prompt.

The Kernel should own the base rules and assemble the final context.

---

## tools

`tools` declares tools provided by the Pack.

A minimal tool spec includes:

```text
name
description
args_schema
risk_level
executor
```

Example tool name:

```text
default.read_file
```

Recommended naming convention:

```text
pack_name.tool_name
```

This prevents collisions when different Packs provide similar tools.

Destination:

```text
ToolRegistry
DecisionProvider tool schema
Trace events
```

### Tool Risk Levels

Recommended risk levels:

```text
safe
read_only
write
external
dangerous
```

The Policy Engine can use risk level as part of policy evaluation.

---

## policy_extensions

`policy_extensions` adds Pack-specific policy rules.

Example:

```json
[
  {
    "match": {
      "tool": "default.read_file"
    },
    "decision": "allow",
    "reason": "Reading files is allowed in the default Pack when inside the workspace."
  },
  {
    "match": {
      "risk_level": "write"
    },
    "decision": "confirm",
    "reason": "Write operations require user approval."
  }
]
```

Destination:

```text
PolicyEngine
Trace events
```

Important:

Pack policy extensions cannot override Kernel base policy.

The final policy model is:

```text
FinalPolicy = KernelBasePolicy + ActivePackPolicyExtensions + SessionApprovals
```

Base policy has priority.

```text
KernelBasePolicy.deny > PackPolicy.allow
```

---

## workflow_hints

`workflow_hints` describes preferred behavior for the current scenario.

In v0.1, workflow hints are soft constraints, not an executable workflow graph.

Example:

```json
{
  "preferred_steps": [
    "Understand the user's request.",
    "Use tools only when external state needs to be inspected.",
    "Summarize tool results before answering."
  ],
  "tool_preferences": [
    {
      "when": "the user asks to inspect a local file",
      "prefer": "default.read_file"
    }
  ],
  "clarification_rules": [
    "Ask a clarifying question if the target path is missing."
  ],
  "finish_criteria": [
    "The user has received a direct answer."
  ]
}
```

Destination:

```text
RuntimeContext
ContextBuilder
DecisionProvider input
```

Important:

workflow_hints should not:

```text
replace the Runtime Loop
define a DAG in v0.1
execute tools directly
bypass policy
mutate Kernel state
```

---

## output_style

`output_style` describes preferred response formatting.

Example:

```json
{
  "format": "markdown",
  "tone": "concise",
  "sections": ["Summary", "Details", "Next Steps"]
}
```

Destination:

```text
ContextBuilder
ResponseRenderer
Frontend display hints
```

The Kernel may use this field to guide the Decision Provider or render responses consistently.

---

## examples

`examples` can provide few-shot examples or scenario examples.

Example:

```json
[
  {
    "user": "Summarize this file.",
    "assistant": "I will inspect the file first, then provide a concise summary."
  }
]
```

Destination:

```text
ContextBuilder
DecisionProvider input
Documentation / demo cases
```

Examples are optional in v0.1.

---

## Pack Loading Flow

Recommended loading flow:

```text
1. User selects a Pack or Kernel chooses default_pack.
2. PackLoader reads manifest.json.
3. Kernel validates required manifest fields.
4. Kernel checks kernel_version compatibility.
5. Kernel loads the entry file.
6. Kernel calls register_pack().
7. Kernel validates PackContribution shape.
8. Kernel checks tool naming and schema.
9. Kernel registers tools into ToolRegistry.
10. Kernel registers policy_extensions into PolicyEngine.
11. Kernel stores prompts, workflow_hints, output_style, and metadata.
12. Kernel updates State.active_pack.
13. Kernel records a pack.loaded trace event.
```

---

## Pack Switching Flow

In v0.1, only one active Pack should be allowed.

When switching Packs:

```text
1. Pause current Agent turn if necessary.
2. Remove old Pack tools from ToolRegistry.
3. Remove old Pack policy extensions from PolicyEngine.
4. Clear Pack-specific pending approvals.
5. Load and validate the new Pack.
6. Register new Pack tools and policy extensions.
7. Replace active prompts, workflow_hints, output_style, and metadata.
8. Update State.active_pack.
9. Record pack.switched trace event.
10. Notify frontend through structured event output.
```

The Kernel base policy remains active during and after Pack switching.

---

## Default Pack

The system should always have an active Pack.

If the user does not explicitly select a Pack, the Kernel loads `default_pack`.

This means the normal runtime does not have a `null` Pack state.

```text
if user_selected_pack:
    load selected pack
else:
    load default_pack
```

The default Pack is not a special exception. It is the built-in baseline Pack.

This keeps the Pack mechanism active and testable from the first version.

---

## Is a Pack Selector Needed?

Not in v0.1.

There are two different concepts:

```text
PackSelector
DecisionProvider
```

A `PackSelector` automatically chooses which Pack to use based on the user request.

A `DecisionProvider` decides the next action under the currently active Pack.

In v0.1:

```text
PackSelector: not required
DecisionProvider: required
```

The user or system explicitly selects the active Pack.

Automatic Pack selection can be explored later.

---

## Pack Validation Rules

A Pack should be rejected if:

```text
manifest.json is missing
required manifest fields are missing
kernel_version is incompatible
entry file is missing
register_pack() is missing
PackContribution has invalid fields
tool names are duplicated
tool schemas are invalid
policy extension format is invalid
Pack attempts to override Kernel base policy
```

The currently active Pack should remain unchanged if a new Pack fails to load.

---

## Summary

A Pack is not just a prompt and not a second Agent.

It is a structured behavior package.

It communicates with the Kernel through:

```text
load-time contribution
runtime subsystem registration
context injection
```

This allows Packs to be strong enough to shape Agent behavior, while still being constrained enough to keep the Kernel stable and safe.
