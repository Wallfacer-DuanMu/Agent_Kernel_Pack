# Pack Protocol

## 文档目的

本文定义在 `Mini Agent Kernel` 中，**Pack** 是什么、它如何与 Kernel 通信，以及 Pack contribution 如何被加载进 Kernel 的各个子系统。

Pack protocol 是本项目最核心的扩展机制。

---

## 简要定义

在本项目中：

> Pack 是一个外部行为包，用于声明场景特定的 prompts、tools、policy extensions、workflow hints、output preferences、examples，以及 metadata。Pack 不替代 Kernel，而是通过结构化 protocol 由 Kernel 校验并组装。

Pack 决定的是 **Kernel 最终变成什么类型的 Agent**。

Kernel 决定的是 **Agent 如何运行**。

---

## 为什么 Pack 不只是一个 Prompt

一种很弱的设计方式，是在加载 Pack 时只往 prompt 里插入一句话：

```text
You are now working inside research_pack.
```

这远远不够。

因为这种方式过于隐式，也过于脆弱，原因包括：

- tools 没有被正式注册；
- policy 行为无法被强制执行；
- workflow preference 无法被检查；
- frontend 无法展示结构化的 Pack 信息；
- 非法的 Pack 定义无法被安全拒绝；
- model output 会变成唯一的控制面。

在本项目中，Pack 通信不只是 prompt injection。

它分为三层：

```text
1. load-time structured contribution
2. runtime subsystem registration
3. context injection for decision making
```

---

## Kernel 与 Pack 之间的三层通信

### 第 1 层：Load-time Structured Contribution

当一个 Pack 被加载时，Kernel 会读取其 manifest，并调用它的 registration entry。

Pack 返回一个结构化的 `PackContribution` 对象。

这一过程发生在 Agent loop 实际使用该 Pack 之前。

```text
PackLoader.load(pack_name)
  -> read manifest
  -> validate compatibility
  -> call register_pack()
  -> validate PackContribution
  -> prepare runtime registration
```

这一层不是自然语言通信，而是系统级装配过程。

---

### 第 2 层：Runtime Subsystem Registration

完成校验后，Kernel 会把 Pack contribution 分发到不同子系统中。

```text
PackContribution.metadata           -> State.active_pack
PackContribution.prompts            -> ContextBuilder
PackContribution.tools              -> ToolRegistry
PackContribution.policy_extensions  -> PolicyEngine
PackContribution.workflow_hints     -> RuntimeContext / ContextBuilder
PackContribution.output_style       -> ResponseRenderer / ContextBuilder
PackContribution.examples           -> ContextBuilder
```

这是最关键的设计点：

> Pack 不是作为一个“大对象”直接塞给 Agent loop，而是被拆解成结构化 contribution，并分别注册到合适的 Kernel 子系统中。

---

### 第 3 层：Context Injection

在每一次 Agent turn 中，Context Builder 会把选定的 Pack 信息注入 runtime context。

例如：

```text
active Pack metadata
Pack prompt additions
available Pack tools
workflow hints
policy summary
output preferences
few-shot examples
```

对于 LLM Decision Provider，这些内容可以被渲染成 prompt 和 tool schema。

对于 Rule Decision Provider，这些内容也可以作为结构化字段直接读取。

context injection 很重要，但它只是整个通信设计中的一层。

---

## Pack 目录结构

一个最小 Pack 应如下所示：

```text
packs/
└─ default_pack/
   ├─ manifest.json
   └─ pack.py
```

未来项目可以支持更多文件，但 v0.1 应尽量保持结构简单。

---

## Manifest

每个 Pack 都必须提供一个 `manifest.json` 文件。

示例：

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

### 必需字段

```text
name
version
kernel_version
description
entry
```

### 可选字段

```text
capabilities
author
tags
homepage
license
```

---

## Pack Registration Entry

每个 Pack 都必须暴露一个标准的 registration function。

示例：

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

这个返回对象称为 `PackContribution`。

---

## PackContribution

`PackContribution` 是 Pack 返回的结构化对象。

推荐的 v0.1 结构如下：

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

每个字段在 Kernel 内部都有不同的归属位置。

---

## metadata

`metadata` 用于描述 Pack 在运行时的信息。

示例：

```json
{
  "display_name": "Default Assistant",
  "description": "A baseline general-purpose assistant Pack.",
  "category": "general"
}
```

去向：

```text
State.active_pack
Frontend Pack display
Trace events
```

---

## prompts

`prompts` 用于提供 prompt additions 或行为规则。

示例：

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

去向：

```text
ContextBuilder
DecisionProvider input
```

重要说明：

Pack 不应提供完整的最终 system prompt。

base rule 应由 Kernel 持有，并由 Kernel 统一组装最终 context。

---

## tools

`tools` 用于声明 Pack 提供的 tools。

一个最小 tool spec 包括：

```text
name
description
args_schema
risk_level
executor
```

示例 tool name：

```text
default.read_file
```

推荐命名约定：

```text
pack_name.tool_name
```

这样可以避免不同 Pack 提供相似 tool 时发生冲突。

去向：

```text
ToolRegistry
DecisionProvider tool schema
Trace events
```

### Tool Risk Levels

推荐的 risk level：

```text
safe
read_only
write
external
dangerous
```

Policy Engine 可以把 risk level 作为 policy evaluation 的一部分。

---

## policy_extensions

`policy_extensions` 用于添加 Pack-specific 的 policy rule。

示例：

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

去向：

```text
PolicyEngine
Trace events
```

重要说明：

Pack policy extension 不能覆盖 Kernel base policy。

最终 policy 模型为：

```text
FinalPolicy = KernelBasePolicy + ActivePackPolicyExtensions + SessionApprovals
```

base policy 优先级最高。

```text
KernelBasePolicy.deny > PackPolicy.allow
```

---

## workflow_hints

`workflow_hints` 用于描述当前场景下推荐的行为方式。

在 v0.1 中，workflow hints 是软约束，而不是可执行的 workflow graph。

示例：

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

去向：

```text
RuntimeContext
ContextBuilder
DecisionProvider input
```

重要说明：

`workflow_hints` 不应：

```text
replace the Runtime Loop
define a DAG in v0.1
execute tools directly
bypass policy
mutate Kernel state
```

---

## output_style

`output_style` 用于描述偏好的响应格式。

示例：

```json
{
  "format": "markdown",
  "tone": "concise",
  "sections": ["Summary", "Details", "Next Steps"]
}
```

去向：

```text
ContextBuilder
ResponseRenderer
Frontend display hints
```

Kernel 可以利用该字段来引导 Decision Provider，或者让响应渲染保持一致。

---

## examples

`examples` 可用于提供 few-shot examples 或场景示例。

示例：

```json
[
  {
    "user": "Summarize this file.",
    "assistant": "I will inspect the file first, then provide a concise summary."
  }
]
```

去向：

```text
ContextBuilder
DecisionProvider input
Documentation / demo cases
```

在 v0.1 中，examples 是可选项。

---

## Pack Loading Flow

推荐的加载流程：

```text
1. User 选择一个 Pack，或 Kernel 自动选择 default_pack。
2. PackLoader 读取 manifest.json。
3. Kernel 校验 manifest 的必需字段。
4. Kernel 检查 kernel_version 兼容性。
5. Kernel 加载 entry file。
6. Kernel 调用 register_pack()。
7. Kernel 校验 PackContribution 的结构。
8. Kernel 检查 tool naming 与 schema。
9. Kernel 将 tools 注册到 ToolRegistry。
10. Kernel 将 policy_extensions 注册到 PolicyEngine。
11. Kernel 存储 prompts、workflow_hints、output_style 与 metadata。
12. Kernel 更新 State.active_pack。
13. Kernel 记录 pack.loaded trace event。
```

---

## Pack Switching Flow

在 v0.1 中，同一时刻只应允许一个 active Pack。

切换 Pack 时：

```text
1. 如有必要，暂停当前 Agent turn。
2. 从 ToolRegistry 中移除旧 Pack 的 tools。
3. 从 PolicyEngine 中移除旧 Pack 的 policy_extensions。
4. 清理 Pack-specific 的 pending approvals。
5. 加载并校验新 Pack。
6. 注册新 Pack 的 tools 与 policy_extensions。
7. 替换 active prompts、workflow_hints、output_style 与 metadata。
8. 更新 State.active_pack。
9. 记录 pack.switched trace event。
10. 通过结构化 event output 通知 frontend。
```

Kernel base policy 在 Pack 切换前后都应保持生效。

---

## Default Pack

系统应始终存在 active Pack。

如果用户没有显式选择 Pack，Kernel 就加载 `default_pack`。

这意味着正常运行时不会出现 `null` Pack state。

```text
if user_selected_pack:
    load selected pack
else:
    load default_pack
```

default Pack 不是特殊例外，而是内建的基线 Pack。

这样从第一版开始，Pack 机制就是启用且可测试的。

---

## 是否需要 Pack Selector？

在 v0.1 中，不需要。

这里有两个不同概念：

```text
PackSelector
DecisionProvider
```

`PackSelector` 负责基于用户请求自动判断应使用哪个 Pack。

`DecisionProvider` 负责在当前 active Pack 之下，决定下一步 action。

在 v0.1 中：

```text
PackSelector: not required
DecisionProvider: required
```

active Pack 由用户或系统显式选择。

automatic Pack selection 可以留到后续再探索。

---

## Pack 校验规则

在以下情况下，Pack 应被拒绝加载：

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

如果一个新 Pack 加载失败，当前 active Pack 应保持不变。

---

## 总结

Pack 不只是一个 prompt，也不是第二个 Agent。

它是一个结构化的行为包。

它通过以下三层与 Kernel 通信：

```text
load-time contribution
runtime subsystem registration
context injection
```

这种设计使 Pack 足够强，能够塑造 Agent 行为；同时又足够受约束，保证 Kernel 保持稳定和安全。
