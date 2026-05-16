# Agent_Kernel_Pack2.0

> Project planning document for a modular Agent infrastructure project built around a stable Kernel and loadable industry Packs.

<p align="center">
  <strong>Stable Kernel. Industry Packs. Observable specialized Agents.</strong>
</p>

---

## Executive Summary

Agent_Kernel_Pack is a modular infrastructure project for specialized Agents. Its core is to support the construction, extension, and evolution of specialized Agents through the decoupling of a stable Kernel and loadable Packs.

Key proposition:

```text
Agent = Stable Kernel + Hot-swappable Pack
```

The project is trying to answer a key question: **Can the core execution mechanism of an Agent be decoupled from industry-specific capability and stabilized into a reusable, evolvable Kernel, while specialized domain behaviors are independently loaded, replaced, and extended through Packs?**

### What 1.0 was

`Agent_Kernel_Pack1.0`, also known by its old name `Mini Agent Kernel`, was the first-stage architecture validation version.

Its primary goal was to validate two things:

- whether the Kernel could run independently;
- whether a Pack could be loaded correctly and collaborate effectively with the Kernel.

In other words, version 1.0 mainly validated whether the **Kernel-Pack decoupling architecture itself** was viable.

### What 2.0 is

`Agent_Kernel_Pack2.0` is the second-stage systematic validation version.

It no longer stops at the level of “can it run.” Instead, it further validates:

- whether the system as a whole is stable enough;
- whether the same Kernel can reliably load multiple industry Packs;
- whether the Pack Protocol is sufficient to carry cross-domain specialized Agent behavior.

The current 2.0 phase focuses on three representative domains as validation samples:

- Financial Analysis
- Legal Contract Processing
- Medical Consultation

Therefore, the focus of 2.0 is not simply to add more features, but to **strengthen system stability and validate the effectiveness and feasibility of loading Packs across three different domains**.

In short:

- **1.0** proved that the basic `Kernel` and `Pack` architecture could work;
- **2.0** aims to prove that this architecture not only works, but can stably support the loading and execution of multiple industry Packs.

On top of that, the project extends toward a longer-term direction: keep the Kernel stable, observable, and governable, while turning Packs into specialized Agent capability units that can be created, shared, downloaded, and evaluated.

---

## Table of Contents

- [Project Positioning](#project-positioning)
- [2.0 Mission Statement](#20-mission-statement)
- [Why This Project Matters](#why-this-project-matters)
- [Core Architecture Proposal](#core-architecture-proposal)
- [What the Kernel Owns](#what-the-kernel-owns)
- [What a Pack Owns](#what-a-pack-owns)
- [Kernel-Pack Communication Protocol](#kernel-pack-communication-protocol)
- [2.0 Validation Scope](#20-validation-scope)
- [Representative Industry Packs](#representative-industry-packs)
- [Functional Scope](#functional-scope)
- [Implementation Approach](#implementation-approach)
- [Design Principles](#design-principles)
- [Roadmap](#roadmap)
- [Long-term Platform Direction](#long-term-platform-direction)
- [Future Pack Vision](#future-pack-vision)
- [Documentation](#documentation)
- [Project Status](#project-status)
- [License](#license)

---

## Project Positioning

`Agent_Kernel_Pack2.0` is a project initiation effort around a specialized Agent infrastructure model.

Its goal is not to build yet another vertical Agent demo. What it really wants to validate is whether there is a reusable way to let multiple specialized Agents share the same runtime foundation.

The whole project is built on a clear architectural layering:

- **Kernel** is the stable runtime layer;
- **Pack** is the structured domain behavior layer;
- a usable specialized Agent is produced by combining the two.

This means the project is fundamentally about **architecture, extensibility, and ecosystem potential**, not just a single-point application.

---

## 2.0 Mission Statement

The mission of version 2.0 is:

> After the Kernel-Pack decoupling idea has been validated in principle, further validate whether the Kernel can reliably load industry Packs and support more realistic specialized Agent behaviors without modifying the core runtime.

This mission contains three layers of meaning.

### 1. Architecture validation

Prove that the boundary between Kernel and Pack is not only conceptually clear, but also operationally stable.

### 2. Domain validation

Prove that the same runtime can carry multiple industry behaviors with real differences.

### 3. Ecosystem validation

Prove that Packs can eventually become reusable, shareable, and evaluable units of specialized Agent capability.

---

## Why This Project Matters

Many early Agent systems begin from prompt chains, CLI tools, or tightly coupled application flows.

That approach is suitable for quick experimentation, but once the system needs to support the following capabilities, structural problems tend to surface:

- real model integration;
- tool execution;
- policy enforcement;
- frontend interaction;
- execution tracing;
- approval workflows;
- multiple business scenarios;
- switching scenarios without rewriting core logic.

Common problems include:

- CLI logic becoming mixed with Agent behavior;
- prompts taking on too many system responsibilities;
- tools being hardcoded into runtime logic;
- workflow logic getting mixed with output parsing;
- policy rules becoming scattered and inconsistent;
- every new scenario requiring core runtime changes;
- insufficient observability and weak explainability.

`Agent_Kernel_Pack2.0` is meant to address exactly these problems. Its basic proposition is:

> Keep the runtime small and stable, move scenario behavior into Packs, and make the whole process observable, governable, and verifiable.

---

## Core Architecture Proposal

The project keeps the original core technical formula unchanged:

```text
Agent = Stable Kernel + Hot-swappable Pack
```

The core architectural relationship it proposes is:

- the **Kernel** answers “how the Agent runs”;
- the **Pack** answers “what kind of specialized Agent this system should become in a given scenario.”

This split cleanly separates:

- runtime control;
- domain behavior;
- policy enforcement;
- tool exposure;
- output shaping.

In implementation terms, the project does not inject a Pack as one giant prompt. Instead, a Pack is decomposed into structured contributions and then registered into different Kernel subsystems.

---

## What the Kernel Owns

The Kernel owns the runtime mechanisms that must remain stable regardless of industry.

### Stable Kernel responsibilities

```text
runtime loop
session state
context assembly
decision provider interface
action protocol
tool registry
policy enforcement
trace recording
Pack loading
event output
```

### Main Kernel subsystems

- **Runtime Loop**  
  Controls one Agent turn or the execution process of a multi-step task.

- **State Manager**  
  Maintains session state, messages, active Pack, pending approvals, step count, and errors.

- **Context Builder**  
  Assembles runtime context based on Kernel rules, session state, active Pack contributions, available tools, policy summaries, and conversation history.

- **Decision Provider Interface**  
  Allows the runtime to connect mock, rule-based, or LLM-based decision providers without modifying Kernel logic.

- **Action Protocol**  
  Uses structured actions to represent the next step:

```text
respond
call_tool
request_approval
finish
fail
```

- **Tool Registry**  
  Registers tools contributed by Packs and exposes them through a stable schema.

- **Policy Engine**  
  Determines whether an action is allowed, denied, or requires confirmation.

- **Trace Recorder**  
  Records messages, context summaries, decisions, policy results, tool calls, tool results, errors, and final responses.

- **Pack Loader**  
  Handles Pack loading, validation, activation, and switching.

The Kernel defines **how the system runs safely, predictably, and observably**.

---

## What a Pack Owns

A Pack owns scenario-specific and industry-specific behavior definitions.

### Structured Pack contributions

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

### Meaning of each field

- **metadata**  
  Describes the Pack itself for runtime state, trace display, and frontend presentation.

- **prompts**  
  Provides domain-specific behavior rules or instructions.

- **tools**  
  Declares tools that should be exposed through the Kernel.

- **policy_extensions**  
  Adds scenario-specific constraints, but cannot override the Kernel base policy.

- **workflow_hints**  
  Provides soft workflow preferences for the decision process.

- **output_style**  
  Defines output format, tone, or response structure.

- **examples**  
  Provides optional few-shot examples or domain examples.

Recommended naming convention for tools:

```text
pack_name.tool_name
```

A Pack can shape behavior, but it does not own execution control.

---

## Kernel-Pack Communication Protocol

The communication model between Kernel and Pack is a structured, stable protocol.

It is not simple prompt injection.

### 1. Structured contribution at load time

When a Pack is loaded, the Kernel reads its manifest and calls its registration entry.

```text
PackLoader.load(pack_name)
  -> read manifest
  -> validate compatibility
  -> call register_pack()
  -> validate PackContribution
```

A Pack returns structured data rather than arbitrary runtime instructions.

### 2. Runtime subsystem registration

After validation, Pack contributions are distributed into different Kernel subsystems.

```text
PackContribution.metadata           -> State.active_pack
PackContribution.prompts            -> ContextBuilder
PackContribution.tools              -> ToolRegistry
PackContribution.policy_extensions  -> PolicyEngine
PackContribution.workflow_hints     -> RuntimeContext / ContextBuilder
PackContribution.output_style       -> ResponseRenderer / ContextBuilder
PackContribution.examples           -> ContextBuilder
```

### 3. Context injection during decision making

In each Agent turn, the Context Builder injects selected Pack information into the runtime context, for example:

```text
active Pack metadata
Pack prompts
available Pack tools
policy summary
workflow hints
output preferences
few-shot examples
```

The Decision Provider then uses this context to decide the next action.

A Pack influences behavior, but execution control always remains in the Kernel.

### Minimal Pack structure

```text
packs/
└─ default_pack/
   ├─ manifest.json
   └─ pack.py
```

### manifest.json

```json
{
  "name": "default_pack",
  "version": "0.1.0",
  "kernel_version": ">=0.1.0",
  "description": "The default baseline Pack for Agent_Kernel_Pack.",
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

### pack.py

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

If a Pack is invalid or incompatible with the current Kernel, the Kernel should reject it without affecting the currently active Pack.

---

## 2.0 Validation Scope

2.0 is not a normal engineering iteration. It is a systematic validation plan.

The project needs to validate the following:

### A. Stable Pack loading capability

- whether a Pack can be loaded through the standard protocol;
- whether compatibility checks can be completed before activation;
- whether invalid Packs can be rejected safely;
- whether Pack switching can happen without breaking the runtime.

### B. Cross-domain behavior carrying capability

- whether the same Kernel can support materially different industry tasks;
- whether industry behavior can be changed through Pack contributions rather than runtime rewrites;
- whether tools, policies, workflows, and outputs can vary with the Pack.

### C. Runtime observability

- whether the behavior of different Packs can be clearly observed through trace events;
- whether tool calls and policy decisions are always visible;
- whether the behavioral differences caused by different Packs can be explained.

### D. Readiness for a future ecosystem

- whether Pack structure can be documented and reused;
- whether Pack quality can be compared in the future;
- whether Pack value can eventually be evaluated systematically.

---

## Representative Industry Packs

Version 2.0 selects three industry directions as initial validation cases.

### Financial Analysis Pack

Used to validate whether the Kernel can carry a behavior pattern characterized by data analysis, structured output, and finance-specific tools and policies.

### Legal Contract Processing Pack

Used to validate whether the Kernel can carry a behavior pattern characterized by document review, risk highlighting, and domain-specific output conventions.

### Medical Consultation Pack

Used to validate whether the Kernel can carry a safety-sensitive conversation pattern with stronger policy constraints and a more cautious output style.

These three Packs differ substantially in task patterns, risk levels, and output forms. That makes them a meaningful test set for determining whether the Pack mechanism is truly general.

---

## Functional Scope

### Core functional scope retained from the original architecture

- Web Chat UI
- Agent session API
- stable Kernel runtime loop
- structured Pack loading protocol
- default Pack
- mock or rule-based decision provider
- basic tool registry
- policy checks before tool execution
- trace event recording
- frontend trace visibility

### What 2.0 strengthens beyond the original MVP

- stable loading of industry Packs;
- cross-domain behavior validation;
- clearer Pack compatibility boundaries;
- stronger Pack-level comparison thinking;
- early preparation for future Pack evaluation.

### What is not included in the current version

- multi-agent collaboration;
- vector database memory;
- complex DAG workflow engine;
- automatic Pack selection;
- large-scale tool ecosystem;
- mature Pack marketplace operations;
- advanced autonomous planning.

---

## Implementation Approach

The current implementation path remains restrained and testable.

### 1. Keep the Kernel core stable

The Kernel should remain small, stable, and predictable.

### 2. Load industry behavior through Packs

Each industry scenario should be expressed through Pack contributions rather than written as hardcoded runtime branches.

### 3. Keep policy control inside the Kernel

The final policy model remains:

```text
FinalPolicy = KernelBasePolicy + ActivePackPolicyExtensions + SessionApprovals
```

And the base policy has the highest priority:

```text
KernelBasePolicy.deny > PackPolicy.allow
```

### 4. Treat observability as a first-class concern

Trace, tool calls, policy decisions, and Pack state should always remain visible on the product surface.

### 5. Keep the web interface as the primary interaction surface

The main interaction model remains a Web Chat UI rather than a CLI-first product experience.

---

## Design Principles

### 1. Kernel stays minimal and stable

The Kernel should not keep accumulating scenario-specific logic.

### 2. Pack is powerful, but must remain constrained

A Pack can shape behavior, but it cannot break the Kernel boundary.

A Pack should not:

```text
replace the runtime loop
bypass Kernel base policy
mutate global Kernel state directly
register tools without schema
override another Pack's tools silently
execute uncontrolled code during validation
```

### 3. Web Chat is the primary product interface

The system should clearly present chat messages, current Pack, tool calls, policy decisions, approval requests, and trace events in the UI.

### 4. The system should always have a default Pack

If the user does not actively choose a Pack, the system loads `default_pack`.

This simplifies runtime assumptions and validates the Pack mechanism from the very beginning.

### 5. Pack quality should ultimately be measurable

A long-term sustainable Pack ecosystem requires not only loadability, but also comparability and evaluation.

---

## Roadmap

### Phase 1 — Baseline Kernel completion

- build the Web Chat UI
- implement the basic Agent Kernel API
- add `MockDecisionProvider` or `RuleDecisionProvider`
- add `default_pack`
- add Pack validation
- display trace events in the frontend

### Phase 2.0 — Stable industry Pack validation

Core objective:

> Validate whether a stable Kernel can reliably carry multiple industry Packs through a unified protocol.

Main work:

- validate stable Pack loading;
- validate Pack compatibility boundaries;
- build and test three representative industry Packs;
- compare the behavior differences across Packs;
- ensure runtime stability without rewriting core logic.

### Next-stage technical evolution

- add `LLMDecisionProvider`
- support configurable model providers
- add a structured model output protocol
- convert tool specs into model tool-calling schemas
- improve prompt and context construction
- support explicit runtime Pack switching
- improve visibility of Pack metadata in the UI
- strengthen policy and tool visualization
- add Pack evaluation cases

---

## Long-term Platform Direction

The long-term direction is to move the project from architecture validation toward platform formation.

The planned strategic directions include:

- launching a website around the Kernel and Pack ecosystem;
- making the Kernel freely downloadable;
- allowing users to create their own Packs and upload them;
- allowing users to download Packs shared by others;
- building a systematic mechanism to evaluate the value of a Pack.

In other words, the future goal is not only to make Packs loadable, but to make them:

- reusable;
- shareable;
- comparable;
- evaluable.

That is the foundation of a true Pack ecosystem.

### Commercialization path and stage planning

If the 2.0 stage is validated successfully, the project will not jump directly into building a large all-in-one platform. Instead, commercialization should advance progressively according to capability maturity.

The overall path can be divided into two layers:

- **To C path**: first validate whether Pack distribution, downloading, usage, and community circulation can work;
- **To B path**: then validate whether Pack evaluation, Pack training, and enterprise-grade customized delivery can work.

These two directions do not replace each other. They connect sequentially: the former creates the ecosystem entry point, while the latter creates a sustainable commercial loop.

#### Stage 1: To C ecosystem entry

The core of this stage is not heavy delivery first, but getting the user-side Pack circulation mechanism running first.

The corresponding product arrangements include:

- launch a project website as the unified entry for Kernel and Pack discovery;
- allow users to download the Kernel for free to reduce the trial barrier;
- allow users to create Packs and upload them to the platform;
- allow users to browse, download, and install Packs shared by others;
- gradually accumulate Pack metadata, usage feedback, and basic evaluation information.

What this stage needs to validate is not whether a single Pack can “demo successfully,” but whether the following propositions hold:

- whether users can understand a Pack as an independent capability unit;
- whether Packs truly have value as things that can be created, shared, and reused;
- whether a stable Kernel is enough to support usage habits centered around different Packs;
- whether the community naturally develops a need to filter and aggregate high-quality Packs.

If this stage succeeds, the project stops being just an architecture experiment and starts to gain the foundation of a platform product.

#### Stage 2: To B capability deepening

Once the To C stage proves that Packs have circulation value, the next stage is no longer only about making Packs downloadable, but about making Pack quality systematically definable, comparable, and improvable.

The key capabilities in this stage include:

- building an evaluation framework to systematically measure a Pack's effectiveness, stability, adaptation range, and practical business value;
- continuously optimizing Packs based on historical tasks, real data, and target metrics;
- shifting Pack improvement from experience-driven iteration toward data-driven and evaluation-driven iteration;
- forming a methodology for Pack customization and iteration in enterprise scenarios.

From a long-term perspective, the core idea here is:

> If neural networks can be trained through data and loss functions, then Packs for specialized Agents should also gradually develop an engineering path for being trainable, optimizable, and evaluable.

This means a Pack may ultimately become more than a static configuration package; it may evolve into a continuously optimized industry capability asset.

#### Stage 3: Enterprise Pack customization and delivery

After evaluation and optimization capabilities are in place, the project can enter a more explicit enterprise commercialization path.

The corresponding business forms include:

- training or tuning dedicated Packs for specific enterprise data, processes, and task types;
- delivering Packs adapted to an enterprise's internal knowledge structures, toolchains, and compliance requirements;
- using Packs as the core delivery unit for customized development, continuous iteration, and outcome evaluation services;
- transforming an enterprise's accumulated process knowledge into reusable, maintainable, and upgradeable Agent capability components.

At this stage, the commercial value of the project no longer comes only from software distribution, but from enabling the assetization of industry capability:

- the Kernel provides a stable runtime;
- Packs carry industry experience;
- evaluation and training mechanisms continuously improve Pack quality;
- what enterprises pay for gradually shifts from “a demo Agent” to “a validated, maintainable, evolvable dedicated Pack capability.”

#### Summary of stage relationships

Therefore, the full commercialization path can be summarized as one continuous route:

```text
Phase 2.0 validation
→ To C: Kernel free distribution + Pack creation/sharing/downloading
→ To B: Pack evaluation + Pack optimization/training
→ Enterprise delivery: custom Pack development and commercialization
```

The essence of this path is not simply “get traffic first, monetize later.” What it really tries to establish is a new mode of Agent capability production:

- first prove that Kernel-Pack decoupling works;
- then prove that Packs can circulate in an ecosystem;
- then prove that Packs can be evaluated and continuously optimized;
- finally prove that Packs can become the capability carrier that enterprises are willing to keep buying and iterating.

If this path succeeds, then the significance of `Agent_Kernel_Pack2.0` is not only to complete a technical project, but to provide a clear development route for the platformization, productization, and commercialization of specialized Agents.

---

## Future Pack Vision

The project's long-term hypothesis is that a Pack may evolve into a reusable unit of specialized Agent capability.

Future Packs may encode:

```text
domain prompts
tool choices
workflow preferences
safety policies
output formats
memory strategies
evaluation cases
```

If this hypothesis holds, then the way specialized Agents are built in the future may increasingly shift toward continuously improving Packs rather than repeatedly rebuilding the runtime.

---

## Documentation

Detailed design documents are available in [`docs/`](./docs/README.md):

- [`01_kernel_definition.md`](./docs/01_kernel_definition.md)
- [`02_minimal_agent_mvp.md`](./docs/02_minimal_agent_mvp.md)
- [`03_pack_protocol.md`](./docs/03_pack_protocol.md)
- [`04_runtime_flow.md`](./docs/04_runtime_flow.md)

For Chinese versions, see the corresponding files:

- [`docs-cn/01_kernel_definition.md`](./docs-cn/01_kernel_definition.md)
- [`docs-cn/02_minimal_agent_mvp.md`](./docs-cn/02_minimal_agent_mvp.md)
- [`docs-cn/03_pack_protocol.md`](./docs-cn/03_pack_protocol.md)
- [`docs-cn/04_runtime_flow.md`](./docs-cn/04_runtime_flow.md)

---

## Project Status

At present, this project has clearly entered the **2.0 project initiation stage**.

The current priorities include:

```text
1. maintain a stable Kernel boundary;
2. validate reliable loading of industry Packs;
3. complete representative Pack prototypes;
4. keep policy and execution control inside the Kernel;
5. provide trace-level observability to support comparison and evaluation;
6. prepare for a future Pack sharing and Pack evaluation ecosystem.
```

---

## License

This project is planned to be released under the **MIT License**.
