# Documentation

This directory contains design documents for `Mini Agent Kernel`.

The docs focus on the core architectural questions of the project:

- What does Kernel mean in this project?
- What is the smallest useful Agent MVP?
- What is a Pack?
- How does a Pack communicate with the Kernel?
- How does one Agent turn run?

## Documents

### 1. Kernel Definition

See: [01_kernel_definition.md](./01_kernel_definition.md)

Defines what the project means by `Kernel`, what responsibilities belong to it, and what should remain outside it.

### 2. Minimal Agent MVP

See: [02_minimal_agent_mvp.md](./02_minimal_agent_mvp.md)

Defines the smallest meaningful Agent runtime loop for the first version.

### 3. Pack Protocol

See: [03_pack_protocol.md](./03_pack_protocol.md)

Defines what a Pack is, what it can contribute, how it is validated, and how it communicates with Kernel subsystems.

### 4. Runtime Flow

See: [04_runtime_flow.md](./04_runtime_flow.md)

Describes the runtime execution flow from user message to decision, policy check, tool execution, trace recording, and frontend events.

## Core Summary

```text
Kernel = stable runtime layer
Pack   = structured behavior package
```

The Kernel owns:

```text
runtime loop
state transition
decision interface
tool runtime
policy enforcement
trace recording
Pack loading
event output
```

The Pack owns:

```text
metadata
prompts
tools
policy extensions
workflow hints
output style
examples
```

The key design principle is:

> Pack is strong enough to shape Agent behavior, but not allowed to break or replace the Kernel.
