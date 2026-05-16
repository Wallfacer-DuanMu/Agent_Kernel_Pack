# Kernel Definition

## Purpose of This Document

This document defines what **Kernel** means in the context of `Mini Agent Kernel`.

The term "Agent Kernel" does not currently have a single universally accepted definition in the software industry. Different projects may use similar words to describe runtimes, orchestrators, workflow engines, tool routers, or agent frameworks.

Therefore, this project uses an explicit project-level definition:

> In this project, the Kernel is the stable runtime layer that owns the Agent loop, state transition, decision interface, tool execution, policy enforcement, trace recording, event output, and Pack loading. It does not own scenario-specific behavior.

The Kernel is the part of the Agent system that should remain stable when the Agent is adapted to different tasks.

---

## Short Definition

In `Mini Agent Kernel`:

```text
Kernel = Agent Runtime + State + Context + Decision Interface + Tool Runtime + Policy Runtime + Trace Runtime + Pack Loader
```

The Kernel defines **how the Agent runs**.

A Pack defines **what kind of Agent it becomes**.

---

## Why a Kernel Is Needed

Many early Agent prototypes begin as simple scripts:

```text
user input -> prompt -> model response -> optional tool call -> final answer
```

This is useful for quick experimentation, but it often becomes difficult to maintain when the system grows.

Common problems include:

- prompts directly control too much of the system behavior;
- tool definitions are hardcoded into the application;
- permission checks are mixed with business logic;
- CLI or UI logic becomes coupled with the Agent loop;
- execution traces are missing or hard to inspect;
- adding a new scenario requires modifying core code.

The Kernel exists to separate stable runtime responsibilities from scenario-specific behavior.

The core architectural hypothesis is:

> If the Agent runtime is stable and generic, scenario-specific behavior can be moved into external Packs and evolved independently.

---

## What the Kernel Owns

The Kernel owns the common mechanisms required by a minimal Agent system.

### 1. Runtime Loop

The Runtime Loop controls the lifecycle of one Agent turn or multi-step execution.

It is responsible for:

- receiving a user message;
- creating or updating session state;
- building the runtime context;
- asking the decision provider for the next action;
- interpreting that action;
- checking policy before execution;
- executing tools when allowed;
- recording trace events;
- deciding whether to continue or finish.

The Runtime Loop should not be replaced by a Pack.

---

### 2. State Manager

The State Manager keeps track of the current session.

A minimal session state includes:

```text
session_id
messages
active_pack
available_tools
pending_approval
last_action
last_result
trace_id
step_count
errors
```

The state belongs to the Kernel because state transitions must remain predictable and testable.

Packs may provide Pack-specific configuration or metadata, but they should not mutate global Kernel state directly.

---

### 3. Context Builder

The Context Builder creates the structured input for the Decision Provider.

The runtime context is not just a raw prompt string. It is a structured object assembled from:

```text
kernel rules
session state
user message
conversation history
active Pack metadata
Pack prompts
available tools
policy summary
workflow hints
output preferences
```

For LLM-based providers, part of this structure may eventually be converted into a model prompt or tool-calling schema.

For mock or rule-based providers, the same structure can be consumed directly.

---

### 4. Decision Provider Interface

The Kernel does not hardcode a specific model or reasoning mechanism.

Instead, it talks to a Decision Provider interface.

Supported provider types may include:

```text
MockDecisionProvider
RuleDecisionProvider
LLMDecisionProvider
```

The Decision Provider receives a runtime context and returns a structured action.

The Kernel does not assume that the decision must come from an LLM.

---

### 5. Action Protocol

The Kernel uses a standard Action protocol to describe what the Agent wants to do next.

Minimal action types:

```text
respond
call_tool
request_approval
finish
fail
```

Example action:

```json
{
  "type": "call_tool",
  "tool_name": "default.read_file",
  "arguments": {
    "path": "README.md"
  }
}
```

The Action protocol is important because it prevents model output, tool execution, and frontend rendering from being tightly coupled.

---

### 6. Tool Registry and Tool Runtime

The Kernel owns the Tool Registry.

Tools can come from the default Pack or from an active external Pack, but they must be registered through the Kernel.

A minimal tool definition includes:

```text
name
description
args_schema
risk_level
executor
```

The Kernel is responsible for:

- validating tool names;
- preventing naming conflicts;
- exposing tool schemas to the Decision Provider;
- routing tool calls;
- wrapping tool results;
- recording tool execution in trace events.

A recommended naming convention is:

```text
pack_name.tool_name
```

For example:

```text
default.read_file
research.search_web
coding.inspect_project
```

---

### 7. Policy Engine

The Kernel owns final policy enforcement.

A Pack may provide policy extensions, but it must not bypass Kernel base policy.

The final policy model is:

```text
FinalPolicy = KernelBasePolicy + ActivePackPolicyExtensions + SessionApprovals
```

The base policy has the highest priority.

For example:

```text
KernelBasePolicy.deny > PackPolicy.allow
```

Minimal policy decisions:

```text
allow
deny
confirm
```

The Policy Engine is executed before tool execution.

---

### 8. Trace Recorder

The Trace Recorder makes Agent behavior observable.

A minimal trace should record:

```text
user_message
active_pack
runtime_context_summary
decision
action
policy_decision
tool_call
tool_result
final_response
error
```

Tracing is a first-class part of this project because the system is intended to demonstrate not only the final answer, but also how the Agent reached that answer.

---

### 9. Pack Loader

The Pack Loader is responsible for loading and validating Packs.

It handles:

- reading the Pack manifest;
- checking Kernel version compatibility;
- loading the Pack entry;
- collecting Pack contributions;
- validating returned fields;
- registering tools;
- registering policy extensions;
- registering workflow hints;
- updating active Pack metadata;
- recording Pack load and switch events.

The Pack Loader is part of the Kernel because Pack loading must be controlled, validated, and observable.

---

### 10. Event Output

The Kernel should return structured events rather than only plain text.

Example event types:

```text
message.created
pack.loaded
action.decided
policy.checked
approval.required
tool.called
tool.finished
agent.finished
trace.recorded
error.occurred
```

This allows the Web Chat UI to display not only messages, but also tool calls, policy decisions, and trace details.

---

## What the Kernel Does Not Own

The Kernel should not contain scenario-specific behavior.

It should not hardcode how a research assistant, coding assistant, file assistant, or planning assistant behaves.

The Kernel should not own:

```text
domain-specific prompts
scenario-specific tools
workflow preferences
specialized output formats
Pack-specific policy extensions
few-shot examples for a specific role
```

Those belong to Packs.

---

## Kernel Boundary

### Kernel Owns

```text
runtime loop
session state
action protocol
decision provider interface
context assembly
tool registry
policy enforcement
trace recording
Pack validation
event output
```

### Pack Owns

```text
scenario metadata
prompt additions
tool declarations
tool implementations
policy extensions
workflow hints
output preferences
few-shot examples
```

### Pack Cannot

```text
replace the runtime loop
bypass Kernel base policy
mutate global Kernel state directly
register tools without schema
override another Pack's tools silently
execute uncontrolled code during validation
```

---

## Default Pack and Kernel Bootstrapping

The system should always run with an active Pack.

If the user has not selected a Pack, the Kernel loads `default_pack`.

This means:

```text
active_pack is never null in normal runtime
```

This design avoids special-case logic for "no Pack" mode and ensures the Pack mechanism is validated from the first version.

The default Pack is not an exception to the architecture. It is the built-in baseline Pack.

---

## Summary

In this project, the Kernel is the stable execution foundation of the Agent.

It owns the Agent loop, state, context assembly, decision interface, tool runtime, policy enforcement, trace recording, event output, and Pack loading.

It intentionally does not own scenario-specific behavior.

The Kernel should remain stable while Packs provide replaceable behavior.
