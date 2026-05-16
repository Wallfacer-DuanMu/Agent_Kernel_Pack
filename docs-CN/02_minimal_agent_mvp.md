# 最小 Agent MVP

## 文档目的

本文定义在 `Mini Agent Kernel` 中，什么叫做一个最小的 Agent MVP。

项目在第一版中有意避免构建一个复杂的 Agent 平台，而是聚焦于“最小但有意义”的运行闭环：它必须能够运行、能够观察、并且能够通过 Pack 扩展。

---

## 简要定义

在本项目中，最小 Agent MVP 指的是：

> 一个可运行的闭环：接收用户输入，构建 runtime context，决定下一步 action，在 policy 控制下按需调用 tools，记录 trace event，并向 frontend 返回结构化输出。

一个最小 Agent 不需要高度自治。

在第一版中，它也不需要 long-term memory、multi-agent collaboration、workflow graph engine，或庞大的 tool ecosystem。

---

## 最小 Agent 公式

最小 Agent MVP 可以表示为：

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

每一部分都有明确职责。

---

## 1. Input

Agent 必须能够接收用户消息。

在 v0.1 中，输入来自 Web Chat UI。

示例：

```text
"Read the README and summarize the project."
```

Kernel 通过 backend API 接收消息，并将其追加到 session state。

---

## 2. State

Agent 必须维护 session state。

最小 state 包括：

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

state 让 Agent 知道：

- 用户问了什么；
- 当前激活的是哪个 Pack；
- 有哪些 tools 可用；
- 是否有等待审批的 tool call；
- 当前 turn 中已经发生过什么。

---

## 3. Context

在请求决策前，Agent 必须先构建 runtime context。

context 由 Kernel 负责组装。

其中可能包括：

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

context 不只是 prompt，它是一个结构化的运行时对象。

对于 LLM provider，这个对象中的部分内容可以被转换成 prompt 和 tool-calling schema。

对于 mock 或 rule provider，则可以直接读取这个对象。

---

## 4. Decision

Agent 必须决定下一步要做什么。

这个决策由 Decision Provider 产生。

支持的 provider 类型可以包括：

```text
MockDecisionProvider
RuleDecisionProvider
LLMDecisionProvider
```

Decision Provider 接收 runtime context，并返回一个结构化 Action。

这样 Kernel 就不会依赖某个具体的 model vendor 或 prompting strategy。

---

## 5. Action

Agent 的下一步必须通过标准协议表示。

最小 action 类型包括：

```text
respond
call_tool
request_approval
finish
fail
```

示例：

```json
{
  "type": "respond",
  "content": "This project is a lightweight Agent Kernel prototype."
}
```

tool action 示例：

```json
{
  "type": "call_tool",
  "tool_name": "default.read_file",
  "arguments": {
    "path": "README.md"
  }
}
```

Action protocol 的意义在于：系统不需要依赖非结构化文本输出，作为唯一控制手段。

---

## 6. Tool

一个最小 Agent 应当能够调用 tool。

tool 赋予 Agent 与环境交互的能力。

最小 tool 字段包括：

```text
name
description
args_schema
risk_level
executor
```

对于 v0.1，只需要一些简单 tool 即可，例如：

```text
default.echo
default.read_file
default.list_workspace
```

目标不是提供很多 tool，而是证明：tool 可以被注册、被选择、经过 policy 检查、被执行，并被写入 trace。

---

## 7. Policy

任何会调用 tool 的 Agent，都需要 policy layer。

policy 用来决定某个 action 是允许、拒绝，还是需要确认。

最小 policy decision 包括：

```text
allow
deny
confirm
```

示例：

```json
{
  "decision": "confirm",
  "reason": "This command may modify files in the workspace."
}
```

在 v0.1 中，Policy 可以很简单。关键点在于：无论是 model 还是 rule provider 提出 tool call，请求都不能直接执行。

它必须先经过 Kernel 的 Policy Engine。

---

## 8. Trace

一个最小 Agent 应该是可观察的。

trace event 允许开发者和用户查看执行过程中发生了什么。

最小 trace event 包括：

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

在本项目中，tracing 很重要，因为 frontend 预期展示的不只是最终答案，还包括内部执行过程。

---

## 9. Output

Agent 应向 frontend 返回结构化输出。

frontend 不应只收到一个纯字符串。

更合适的是返回如下 event：

```text
message.created
tool.called
policy.checked
approval.required
tool.finished
agent.finished
```

这样 Web Chat UI 就可以渲染：

- 普通聊天消息；
- tool call 卡片；
- policy decision 卡片；
- approval 提示；
- trace 面板。

---

## v0.1 不要求包含的内容

以下能力在第一版中有意排除：

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

这些方向可以以后再探索，但它们不是验证第一版架构所必需的内容。

---

## 为什么不从复杂的 Workflow Engine 开始

如果一开始就引入复杂的 workflow engine，会让第一版变得更难理解、更难验证。

v0.1 的主要目标，不是证明 Agent 能高度自治地完成复杂任务。

v0.1 真正要证明的是：运行时边界设计是否正确。

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

当这个闭环稳定后，再向上叠加更复杂的 workflow mechanism 才是合理的。

---

## 为什么在 v0.1 中使用 Mock 或 Rule Provider 是可以接受的

第一版并不需要依赖真实的 LLM API。

这是有意为之。

mock 或 rule provider 足以验证：

- runtime flow；
- action protocol；
- tool registry；
- policy checks；
- trace recording；
- Pack loading；
- frontend event rendering。

后续可以通过同一个 Decision Provider interface 接入真实 LLM 支持。

这样可以避免第一版被不稳定的 model prompt 或外部 API 配置所绑死。

---

## MVP 验收标准

如果 v0.1 MVP 能演示以下流程，就可以认为是合格的：

```text
1. User 打开 Web Chat UI。
2. Kernel 以 default_pack 启动。
3. User 发送消息。
4. Kernel 构建 runtime context。
5. Decision Provider 返回结构化 action。
6. 如果 action 是 tool call，Policy Engine 进行检查。
7. 只有在允许时，tool 才会执行。
8. Trace event 被记录下来。
9. Frontend 展示聊天响应与 trace 细节。
```

更强一些的 v0.1 演示还可以包含：

```text
- 从 default_pack 切换到另一个 demo Pack；
- 展示 tool availability 的变化；
- 展示 workflow hints 的变化；
- 在 UI 中展示 Pack metadata。
```

---

## 总结

第一版 MVP 应当小，但必须完整。

它不应试图一开始就构建一个完整的 Agent 平台。

它需要清晰地证明一件事：

> 稳定的 Kernel 可以运行一个可观察的 Agent loop，而行为特定的配置则由 Pack 提供。
