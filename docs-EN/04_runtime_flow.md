# Runtime Flow

## Purpose of This Document

This document describes how one Agent turn runs in `Mini Agent Kernel`, and where Pack contributions participate in that runtime flow.

The main idea is:

> Pack provides behavior and capabilities. Decision Provider decides the next action. Kernel executes, constrains, and records the process.

---

## High-level Flow

```text
User Message
  -> Backend API
  -> State Update
  -> RuntimeContext Build
  -> DecisionProvider
  -> Action
  -> Policy Check
  -> Tool Execution or Response
  -> Trace Recording
  -> Frontend Events
```

The Kernel controls this flow.

A Pack influences this flow through registered tools, prompts, policy extensions, workflow hints, output style, and examples.

---

## Boot Flow

When the application starts, the Kernel should load a Pack.

If no Pack is selected, it loads `default_pack`.

```text
Kernel boot
  -> load default_pack
  -> validate manifest
  -> collect PackContribution
  -> register tools
  -> register policy extensions
  -> store prompts and workflow hints
  -> set State.active_pack
  -> record pack.loaded trace event
```

The normal runtime should always have an active Pack.

---

## User Message Flow

When the user sends a message from the Web Chat UI:

```text
1. Backend API receives message.
2. StateManager appends the user message.
3. TraceRecorder records user_message_received.
4. Runtime starts an Agent turn.
```

At this stage, the Kernel has not yet asked the Decision Provider what to do.

---

## RuntimeContext Build

The Context Builder creates a structured `RuntimeContext`.

Example structure:

```text
RuntimeContext
├─ session
│  ├─ session_id
│  ├─ messages
│  ├─ current_step
│  └─ pending_approval
│
├─ active_pack
│  ├─ name
│  ├─ version
│  └─ description
│
├─ kernel_rules
│  ├─ action protocol
│  ├─ tool execution rules
│  └─ safety boundaries
│
├─ pack_prompts
├─ available_tools
├─ policy_summary
├─ workflow_hints
├─ output_style
└─ previous_results
```

This context is created by the Kernel, not by the Pack.

The Pack contributes pieces of the context, but the Kernel owns the final assembly.

---

## Decision Flow

The Kernel sends `RuntimeContext` to the active Decision Provider.

```text
DecisionProvider.decide(RuntimeContext) -> Action
```

The returned action must follow the Action protocol.

Possible actions:

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
  "type": "call_tool",
  "tool_name": "default.read_file",
  "arguments": {
    "path": "README.md"
  }
}
```

The Decision Provider does not execute the tool. It only proposes the action.

The Kernel interprets and controls the action.

---

## How Pack Affects Decision

Pack affects decision making through the runtime context.

For example, a research Pack may provide:

```text
prompts: prefer structured research answers
workflow_hints: search first when current information is needed
tools: research.search_web, research.summarize_text
output_style: markdown sections with Summary and Sources
```

The Decision Provider sees these contributions in the context and may choose a different action than it would under the default Pack.

However, the Pack does not directly decide or execute the next step.

---

## Policy Check Flow

If the action is `call_tool`, the Kernel must check policy before execution.

```text
Action(call_tool)
  -> PolicyEngine.evaluate(action, state, active_pack)
  -> allow / deny / confirm
```

The final policy is composed as:

```text
FinalPolicy = KernelBasePolicy + ActivePackPolicyExtensions + SessionApprovals
```

Priority rule:

```text
KernelBasePolicy.deny > PackPolicy.allow
```

This means a Pack can add rules, but cannot lower the Kernel's base safety boundary.

---

## Policy Outcomes

### allow

If policy returns `allow`, the Kernel executes the tool.

```text
Policy: allow
  -> ToolRegistry.execute(tool_name, arguments)
  -> ToolResult
```

### deny

If policy returns `deny`, the Kernel does not execute the tool.

```text
Policy: deny
  -> record policy.denied
  -> return denial message or event
```

### confirm

If policy returns `confirm`, the Kernel pauses execution and asks the user for approval.

```text
Policy: confirm
  -> create pending_approval
  -> return approval.required event to frontend
```

The frontend can show a confirmation card.

If the user approves, the Kernel resumes with the same pending action.

---

## Tool Execution Flow

Tools are executed through the Tool Registry.

```text
ToolRegistry
  -> find tool by name
  -> validate arguments
  -> execute tool
  -> wrap result
  -> record trace
```

A tool result should be structured.

Example:

```json
{
  "tool_name": "default.read_file",
  "success": true,
  "result": "...file content or summary...",
  "error": null
}
```

The result is written back into session state and trace.

Then the Runtime may either:

```text
- ask the Decision Provider for another action; or
- produce a final response; or
- stop after max_steps.
```

---

## Step Limit

The Runtime should enforce a maximum step count.

Example:

```text
max_steps = 5
```

This prevents accidental infinite loops, especially when using an LLM Decision Provider.

If the step limit is reached, the Kernel should stop and return a controlled failure or partial response.

---

## Response Flow

If the Decision Provider returns `respond` or `finish`, the Kernel creates message events for the frontend.

```text
Action(respond)
  -> record agent.responded
  -> return message.created event
```

```text
Action(finish)
  -> record agent.finished
  -> return agent.finished event
```

The frontend renders these as normal chat messages and trace updates.

---

## Trace Flow

Trace recording should happen throughout the whole process.

Recommended event sequence for a simple response:

```text
user_message_received
context_built
action_decided
agent_responded
agent_finished
```

Recommended event sequence for a tool call:

```text
user_message_received
context_built
action_decided
policy_checked
tool_called
tool_finished
context_built
action_decided
agent_responded
agent_finished
```

Recommended event sequence for approval:

```text
user_message_received
context_built
action_decided
policy_checked
approval_required
approval_received
tool_called
tool_finished
agent_responded
agent_finished
```

Trace data should be available to the frontend trace panel.

---

## Pack Switching Runtime Flow

Pack switching should be explicit in v0.1.

Recommended flow:

```text
User selects Pack
  -> Backend API receives switch request
  -> Kernel validates new Pack
  -> Kernel unloads old Pack contributions
  -> Kernel registers new Pack contributions
  -> State.active_pack is updated
  -> trace records pack.switched
  -> frontend receives pack.switched event
```

When a Pack is switched:

```text
old Pack tools are removed
old Pack policy extensions are removed
old workflow hints are replaced
old output style is replaced
Pack-specific pending approvals are cleared
Kernel base policy remains active
session conversation may remain
```

In v0.1, only one active Pack should be supported.

---

## Important Separation of Responsibilities

The runtime has three major participants:

```text
Pack
DecisionProvider
Kernel
```

Their responsibilities are different.

### Pack

```text
Provides behavior and capabilities.
```

Examples:

```text
prompts
tools
policy extensions
workflow hints
output style
examples
```

### DecisionProvider

```text
Decides the next action under the current runtime context.
```

It may be mock-based, rule-based, or LLM-based.

### Kernel

```text
Executes, constrains, and records the process.
```

It owns:

```text
runtime loop
state
action interpretation
policy enforcement
tool execution
trace recording
event output
```

---

## Why This Is Stronger Than Prompt-only Packs

A prompt-only Pack can influence the model, but it cannot safely control runtime behavior.

This project uses structured Pack contributions so that:

```text
tools are formally registered
policies are enforceable
workflow hints are inspectable
trace events can show Pack influence
invalid Packs can be rejected
frontend can display Pack metadata
Kernel base safety cannot be bypassed
```

This makes Pack behavior more stable and observable than raw prompt injection.

---

## Summary

During runtime, the Kernel does not ask the Pack to run the Agent loop.

Instead:

```text
Pack contributes structured behavior.
Kernel assembles RuntimeContext.
DecisionProvider proposes Action.
Kernel enforces Policy.
Kernel executes Tools.
Kernel records Trace.
Frontend displays Events.
```

This keeps the Kernel stable while allowing Pack behavior to be changed or extended.
