# Minimal Agent MVP

## Purpose of This Document

This document defines what a minimal Agent MVP means in `Mini Agent Kernel`.

The project intentionally avoids building a complex Agent platform in the first version. Instead, it focuses on the smallest meaningful runtime loop that can be executed, observed, and extended through Packs.

---

## Short Definition

In this project, a minimal Agent MVP is:

> A runnable loop that receives user input, builds runtime context, decides the next action, optionally calls tools under policy control, records trace events, and returns structured output to the frontend.

A minimal Agent does not need to be highly autonomous.

It does not need long-term memory, multi-agent collaboration, a workflow graph engine, or a large tool ecosystem in the first version.

---

## Minimal Agent Formula

The minimal Agent MVP can be described as:

```text
Minimal Agent MVP =
Input
+ State
+ Context
+ Decision
+ Action
+ Tool
+ Policy
+ Trace
+ Output
```

Each part has a specific role.

---

## 1. Input

The Agent must receive user messages.

For v0.1, input comes from the Web Chat UI.

Example:

```text
"Read the README and summarize the project."
```

The Kernel receives this message through the backend API and appends it to session state.

---

## 2. State

The Agent must maintain session state.

Minimal state includes:

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

State allows the Agent to know:

- what the user asked;
- what Pack is active;
- what tools are available;
- whether a tool call is waiting for approval;
- what has already happened in the current turn.

---

## 3. Context

The Agent must build a runtime context before asking for a decision.

The context is assembled by the Kernel.

It may include:

```text
kernel rules
current user message
recent conversation history
active Pack metadata
Pack prompts
available tools
policy summary
workflow hints
output preferences
previous tool results
```

The context is not only a prompt. It is a structured runtime object.

For an LLM provider, parts of this object can be converted into a prompt and tool-calling schema.

For a mock or rule provider, the object can be read directly.

---

## 4. Decision

The Agent must decide what to do next.

The decision is produced by a Decision Provider.

Supported provider types may include:

```text
MockDecisionProvider
RuleDecisionProvider
LLMDecisionProvider
```

The Decision Provider receives the runtime context and returns a structured Action.

This keeps the Kernel independent from any specific model vendor or prompting strategy.

---

## 5. Action

The Agent's next step must be represented by a standard protocol.

Minimal action types:

```text
respond
call_tool
request_approval
finish
fail
```

Example:

```json
{
  "type": "respond",
  "content": "This project is a lightweight Agent Kernel prototype."
}
```

Example tool action:

```json
{
  "type": "call_tool",
  "tool_name": "default.read_file",
  "arguments": {
    "path": "README.md"
  }
}
```

The Action protocol prevents the system from relying on unstructured text output as the only control mechanism.

---

## 6. Tool

A minimal Agent should be able to call tools.

A tool gives the Agent the ability to interact with the environment.

Minimal tool fields:

```text
name
description
args_schema
risk_level
executor
```

For v0.1, simple tools are enough, such as:

```text
default.echo
default.read_file
default.list_workspace
```

The goal is not to provide many tools, but to prove that tools can be registered, selected, policy-checked, executed, and traced.

---

## 7. Policy

Any Agent that calls tools needs a policy layer.

Policy determines whether an action is allowed, denied, or requires confirmation.

Minimal policy decisions:

```text
allow
deny
confirm
```

Example:

```json
{
  "decision": "confirm",
  "reason": "This command may modify files in the workspace."
}
```

In v0.1, Policy can be simple. The important point is that tool execution does not happen directly after a model or rule provider asks for it.

The action must pass through the Kernel's Policy Engine first.

---

## 8. Trace

A minimal Agent should be observable.

Trace events allow developers and users to inspect what happened during execution.

Minimal trace events include:

```text
user_message_received
pack_loaded
context_built
action_decided
policy_checked
tool_called
tool_finished
agent_responded
agent_finished
error_occurred
```

Tracing is important for this project because the frontend is expected to show not only the final answer, but also the internal execution process.

---

## 9. Output

The Agent should return structured output to the frontend.

The frontend should not only receive a plain string.

Instead, it should receive events such as:

```text
message.created
tool.called
policy.checked
approval.required
tool.finished
agent.finished
```

This allows the Web Chat UI to render:

- normal chat messages;
- tool call cards;
- policy decision cards;
- approval prompts;
- trace panels.

---

## What Is Not Required in v0.1

The following features are intentionally excluded from the first MVP:

```text
multi-agent collaboration
vector database memory
long-term memory
complex DAG workflow engine
automatic Pack selection
remote Pack marketplace
large tool ecosystem
advanced autonomous planning
self-reflection loop
```

They may be explored later, but they are not required to prove the first architecture.

---

## Why Not Start with a Complex Workflow Engine?

A complex workflow engine would make the first version harder to reason about.

The main goal of v0.1 is not to prove that the Agent can complete difficult tasks autonomously.

The main goal is to prove that the runtime boundary is correct:

```text
User Message
-> Runtime Context
-> Decision
-> Action
-> Policy
-> Tool Execution
-> Trace
-> Response
```

Once this loop is stable, more advanced workflow mechanisms can be added later.

---

## Why Mock or Rule Providers Are Acceptable in v0.1

The first version does not need to depend on a real LLM API.

This is intentional.

A mock or rule provider can validate:

- runtime flow;
- action protocol;
- tool registry;
- policy checks;
- trace recording;
- Pack loading;
- frontend event rendering.

Real LLM support can be added later through the same Decision Provider interface.

This avoids coupling the first version to unstable model prompts or external API configuration.

---

## MVP Acceptance Criteria

A v0.1 MVP is acceptable if it can demonstrate the following flow:

```text
1. User opens the Web Chat UI.
2. Kernel starts with default_pack.
3. User sends a message.
4. Kernel builds runtime context.
5. Decision Provider returns a structured action.
6. If the action calls a tool, Policy Engine checks it.
7. Tool executes only if allowed.
8. Trace events are recorded.
9. Frontend shows chat response and trace details.
```

A stronger v0.1 demo may also include:

```text
- switching from default_pack to another demo Pack;
- showing changed tool availability;
- showing changed workflow hints;
- showing Pack metadata in the UI.
```

---

## Summary

The first MVP should be small, but complete.

It should not try to build a full Agent platform.

It should prove one thing clearly:

> A stable Kernel can run an observable Agent loop, while behavior-specific configuration is provided by a Pack.
