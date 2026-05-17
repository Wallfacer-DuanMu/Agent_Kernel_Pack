# Architecture

## Overview

Agent Kernel uses a two-layer design:

- fixed core kernel
- hot-swappable external Packs

```text
main.py
  -> core.runtime.AgentRuntime
     -> core.context / core.state / core.actions
     -> capabilities.registry
     -> policy.guard
     -> tracing.trace_store
     -> core.loader.PackLoader
     -> packs/<pack_name>/workflow.py
     -> packs/<pack_name>/policy.py
     -> packs/<pack_name>/tools.py
     -> packs/<pack_name>/output.py
     -> packs/<pack_name>/prompts.py
```

## Core layer

The core layer is responsible for system behavior:

- `Runtime`: drives the agent loop
- `State`: stores session, task, steps, tool results, and errors
- `Actions`: normalizes agent decisions into a stable protocol
- `Context`: builds the runtime context for each step
- `Capabilities`: registers and executes tools
- `Policy`: validates whether a tool action is allowed
- `Tracing`: records each runtime step
- `Loader`: resolves and loads Packs

## Pack layer

The external Pack layer defines scenario-specific behavior:

- workflow logic
- policy extensions
- tools
- output rendering
- prompts
- manifest metadata

## Runtime flow

1. Build state for the current task.
2. Build context from state.
3. Ask the decision provider for an action.
4. If the action is a tool call, resolve the tool from the registry.
5. Run policy checks before execution.
6. Execute the tool only when allowed.
7. Record the step in trace storage.
8. Render the final result through the Pack output renderer when available.

## Policy integration

Policy runs before tool execution and can return:

- allow
- deny
- confirm

This keeps dangerous actions guarded without making the system rigid.

## Tracing

Tracing records a compact JSONL entry for each step, including:

- session id
- step number
- action type
- tool metadata
- policy decision
- result summary
- error information

## Pack loading

The loader reads `manifest.json`, validates required fields, and imports the Pack entry files.

A Pack can be loaded by:

- Pack name under `packs/`
- absolute or relative Pack directory path
