# Kernel 定义

## 文档目的

本文定义在 `Mini Agent Kernel` 语境下，**Kernel** 具体指什么。

“Agent Kernel” 这个词在当前软件行业里并没有统一且公认的标准定义。不同项目可能会用相近的词来描述 runtime、orchestrator、workflow engine、tool router，或者 agent framework。

因此，本项目给出一个项目级、明确的定义：

> 在本项目中，Kernel 是稳定的运行时层，负责 Agent loop、state transition、decision interface、tool execution、policy enforcement、trace recording、event output，以及 Pack loading。它不负责场景特定的行为。

当 Agent 被适配到不同任务时，Kernel 应该仍然保持稳定；它是 Agent 系统中不应频繁变化的部分。

---

## 简要定义

在 `Mini Agent Kernel` 中：

```text
Kernel = Agent Runtime + State + Context + Decision Interface + Tool Runtime + Policy Runtime + Trace Runtime + Pack Loader
```

Kernel 定义的是 **Agent 如何运行**。

Pack 定义的是 **Agent 最终呈现成什么类型**。

---

## 为什么需要 Kernel

很多早期 Agent 原型往往从一个简单脚本开始：

```text
user input -> prompt -> model response -> optional tool call -> final answer
```

这对于快速试验很有帮助，但随着系统变大，通常会越来越难维护。

常见问题包括：

- prompt 直接控制了过多系统行为；
- tool 定义被硬编码在应用中；
- permission check 与业务逻辑混杂；
- CLI 或 UI 逻辑与 Agent loop 耦合；
- 缺少 execution trace，或 trace 难以检查；
- 新增一个场景就需要修改核心代码。

Kernel 的存在，就是为了把稳定的运行时职责，与场景特定的行为分离开来。

本项目的核心架构假设是：

> 如果 Agent runtime 足够稳定且通用，那么场景特定行为就可以移入外部 Pack，并独立演进。

---

## Kernel 负责什么

Kernel 负责一个最小 Agent 系统所需的通用机制。

### 1. Runtime Loop

Runtime Loop 控制一次 Agent turn 或多步执行的生命周期。

它负责：

- 接收用户消息；
- 创建或更新 session state；
- 构建 runtime context；
- 向 Decision Provider 请求下一步 action；
- 解释该 action；
- 在执行前进行 policy 检查；
- 在允许时执行 tool；
- 记录 trace event；
- 决定继续还是结束。

Runtime Loop 不应由 Pack 替换。

---

### 2. State Manager

State Manager 负责跟踪当前 session。

一个最小 session state 包括：

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

state 之所以属于 Kernel，是因为 state transition 必须保持可预测、可测试。

Pack 可以提供 Pack-specific 的配置或 metadata，但不应直接修改全局 Kernel state。

---

### 3. Context Builder

Context Builder 负责为 Decision Provider 构建结构化输入。

runtime context 不只是一个原始 prompt 字符串，而是由以下内容组装而成的结构化对象：

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

对于基于 LLM 的 provider，这个结构中的部分内容最终可能会被转换成 model prompt 或 tool-calling schema。

对于 mock 或 rule-based provider，同一个结构也可以被直接消费。

---

### 4. Decision Provider Interface

Kernel 不应硬编码某个具体的 model 或 reasoning mechanism。

它应当通过 Decision Provider interface 与外部决策模块通信。

支持的 provider 类型可以包括：

```text
MockDecisionProvider
RuleDecisionProvider
LLMDecisionProvider
```

Decision Provider 接收 runtime context，并返回一个结构化 action。

Kernel 不预设这个决策一定来自 LLM。

---

### 5. Action Protocol

Kernel 使用统一的 Action protocol，来描述 Agent 下一步想做什么。

最小 action 类型包括：

```text
respond
call_tool
request_approval
finish
fail
```

示例 action：

```json
{
  "type": "call_tool",
  "tool_name": "default.read_file",
  "arguments": {
    "path": "README.md"
  }
}
```

Action protocol 很重要，因为它避免了 model output、tool execution 与 frontend rendering 之间的紧耦合。

---

### 6. Tool Registry 与 Tool Runtime

Kernel 拥有 Tool Registry。

tool 可以来自 default Pack，也可以来自当前激活的外部 Pack，但它们都必须通过 Kernel 完成注册。

一个最小 tool 定义包括：

```text
name
description
args_schema
risk_level
executor
```

Kernel 负责：

- 校验 tool name；
- 防止命名冲突；
- 向 Decision Provider 暴露 tool schema；
- 路由 tool call；
- 包装 tool result；
- 在 trace event 中记录 tool 执行情况。

推荐命名约定：

```text
pack_name.tool_name
```

例如：

```text
default.read_file
research.search_web
coding.inspect_project
```

---

### 7. Policy Engine

Kernel 负责最终的 policy enforcement。

Pack 可以提供 policy extension，但不能绕过 Kernel base policy。

最终 policy 模型为：

```text
FinalPolicy = KernelBasePolicy + ActivePackPolicyExtensions + SessionApprovals
```

base policy 拥有最高优先级。

例如：

```text
KernelBasePolicy.deny > PackPolicy.allow
```

最小 policy decision 包括：

```text
allow
deny
confirm
```

Policy Engine 必须在 tool execution 之前执行。

---

### 8. Trace Recorder

Trace Recorder 让 Agent 行为变得可观察。

一个最小 trace 应记录：

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

在本项目中，tracing 是一等公民，因为系统不仅要展示最终答案，也要展示 Agent 是如何得出这个答案的。

---

### 9. Pack Loader

Pack Loader 负责加载并校验 Pack。

它处理：

- 读取 Pack manifest；
- 检查 Kernel version 兼容性；
- 加载 Pack entry；
- 收集 Pack contribution；
- 校验返回字段；
- 注册 tools；
- 注册 policy extensions；
- 注册 workflow hints；
- 更新 active Pack metadata；
- 记录 Pack load 与 switch event。

Pack Loader 属于 Kernel，因为 Pack loading 必须受到控制、校验，并且可观察。

---

### 10. Event Output

Kernel 应返回结构化 event，而不只是纯文本。

示例 event 类型：

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

这样 Web Chat UI 就不仅能展示消息本身，也能展示 tool call、policy decision 与 trace 细节。

---

## Kernel 不负责什么

Kernel 不应包含场景特定的行为。

它不应硬编码 research assistant、coding assistant、file assistant 或 planning assistant 的行为方式。

Kernel 不应负责：

```text
domain-specific prompts
scenario-specific tools
workflow preferences
specialized output formats
Pack-specific policy extensions
few-shot examples for a specific role
```

这些都应属于 Pack。

---

## Kernel 边界

### Kernel 负责

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

### Pack 负责

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

### Pack 不可以做的事

```text
replace the runtime loop
bypass Kernel base policy
mutate global Kernel state directly
register tools without schema
override another Pack's tools silently
execute uncontrolled code during validation
```

---

## Default Pack 与 Kernel Bootstrapping

系统应始终在存在 active Pack 的前提下运行。

如果用户没有选择 Pack，Kernel 就加载 `default_pack`。

这意味着：

```text
active_pack is never null in normal runtime
```

这种设计避免了“无 Pack 模式”的特殊分支逻辑，也确保 Pack 机制从第一版开始就处于启用并可验证的状态。

default Pack 不是对架构的例外处理，而是内建的基线 Pack。

---

## 总结

在本项目中，Kernel 是 Agent 的稳定执行基础。

它负责 Agent loop、state、context assembly、decision interface、tool runtime、policy enforcement、trace recording、event output，以及 Pack loading。

它有意不负责场景特定行为。

Kernel 应保持稳定，而可替换的行为由 Pack 提供。
