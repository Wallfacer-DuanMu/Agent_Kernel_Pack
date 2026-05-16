# Runtime Flow

## 文档目的

本文描述在 `Mini Agent Kernel` 中，一次 Agent turn 是如何运行的，以及 Pack contribution 在这个 runtime flow 中是如何参与进来的。

核心思想是：

> Pack 提供行为与能力，Decision Provider 决定下一步 action，Kernel 负责执行、约束并记录整个过程。

---

## 高层流程

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

整个流程由 Kernel 控制。

Pack 通过已注册的 tools、prompts、policy extensions、workflow hints、output style 和 examples，对这条流程产生影响。

---

## Boot Flow

应用启动时，Kernel 应先加载一个 Pack。

如果没有选定 Pack，则加载 `default_pack`。

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

正常运行时应始终存在 active Pack。

---

## User Message Flow

当用户从 Web Chat UI 发送一条消息时：

```text
1. Backend API 接收消息。
2. StateManager 追加该用户消息。
3. TraceRecorder 记录 user_message_received。
4. Runtime 启动一次 Agent turn。
```

此时，Kernel 还没有向 Decision Provider 询问下一步该做什么。

---

## RuntimeContext Build

Context Builder 会创建结构化的 `RuntimeContext`。

示例结构：

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

这个 context 是由 Kernel 创建的，而不是由 Pack 创建。

Pack 只贡献 context 的一部分，而最终组装权属于 Kernel。

---

## Decision Flow

Kernel 会把 `RuntimeContext` 发送给当前激活的 Decision Provider。

```text
DecisionProvider.decide(RuntimeContext) -> Action
```

返回的 action 必须遵循 Action protocol。

可能的 action：

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
  "type": "call_tool",
  "tool_name": "default.read_file",
  "arguments": {
    "path": "README.md"
  }
}
```

Decision Provider 不执行 tool，它只提出 action。

真正解释并控制 action 的，是 Kernel。

---

## Pack 如何影响 Decision

Pack 通过 runtime context 影响决策过程。

例如，一个 research Pack 可能提供：

```text
prompts: prefer structured research answers
workflow_hints: search first when current information is needed
tools: research.search_web, research.summarize_text
output_style: markdown sections with Summary and Sources
```

Decision Provider 在 context 中看到这些 contribution 后，就可能做出与 default Pack 下不同的 action 选择。

但 Pack 本身并不会直接决定或执行下一步。

---

## Policy Check Flow

如果 action 是 `call_tool`，Kernel 必须在执行前进行 policy 检查。

```text
Action(call_tool)
  -> PolicyEngine.evaluate(action, state, active_pack)
  -> allow / deny / confirm
```

最终 policy 组合方式为：

```text
FinalPolicy = KernelBasePolicy + ActivePackPolicyExtensions + SessionApprovals
```

优先级规则：

```text
KernelBasePolicy.deny > PackPolicy.allow
```

这意味着 Pack 可以增加规则，但不能降低 Kernel 的基础安全边界。

---

## Policy Outcomes

### allow

如果 policy 返回 `allow`，Kernel 执行该 tool。

```text
Policy: allow
  -> ToolRegistry.execute(tool_name, arguments)
  -> ToolResult
```

### deny

如果 policy 返回 `deny`，Kernel 不执行该 tool。

```text
Policy: deny
  -> record policy.denied
  -> return denial message or event
```

### confirm

如果 policy 返回 `confirm`，Kernel 会暂停执行，并向用户请求 approval。

```text
Policy: confirm
  -> create pending_approval
  -> return approval.required event to frontend
```

frontend 可以据此展示一个确认卡片。

如果用户批准，Kernel 再以同一个 pending action 继续执行。

---

## Tool Execution Flow

tools 通过 Tool Registry 执行。

```text
ToolRegistry
  -> find tool by name
  -> validate arguments
  -> execute tool
  -> wrap result
  -> record trace
```

tool result 应该是结构化的。

示例：

```json
{
  "tool_name": "default.read_file",
  "success": true,
  "result": "...file content or summary...",
  "error": null
}
```

result 会被写回 session state 和 trace。

之后 Runtime 可能会：

```text
- ask the Decision Provider for another action; or
- produce a final response; or
- stop after max_steps.
```

---

## Step Limit

Runtime 应强制执行最大 step 数限制。

例如：

```text
max_steps = 5
```

这样可以避免意外的无限循环，尤其是在使用 LLM Decision Provider 时。

如果达到 step limit，Kernel 应停止执行，并返回受控的失败结果或部分响应。

---

## Response Flow

如果 Decision Provider 返回 `respond` 或 `finish`，Kernel 会为 frontend 创建 message event。

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

frontend 将它们渲染为普通聊天消息和 trace 更新。

---

## Trace Flow

整个过程中都应持续记录 trace。

简单响应的推荐事件序列：

```text
user_message_received
context_built
action_decided
agent_responded
agent_finished
```

包含 tool call 的推荐事件序列：

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

包含 approval 的推荐事件序列：

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

trace data 应可供 frontend 的 trace panel 使用。

---

## Pack Switching Runtime Flow

在 v0.1 中，Pack switching 应是显式操作。

推荐流程：

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

当 Pack 被切换时：

```text
old Pack tools are removed
old Pack policy extensions are removed
old workflow hints are replaced
old output style is replaced
Pack-specific pending approvals are cleared
Kernel base policy remains active
session conversation may remain
```

在 v0.1 中，同一时间只应支持一个 active Pack。

---

## 重要的职责分离

runtime 中有三个主要参与者：

```text
Pack
DecisionProvider
Kernel
```

它们的职责各不相同。

### Pack

```text
Provides behavior and capabilities.
```

例如：

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

它可以是 mock-based、rule-based，或 LLM-based。

### Kernel

```text
Executes, constrains, and records the process.
```

它负责：

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

## 为什么这比仅使用 Prompt 的 Pack 更强

只依赖 prompt 的 Pack 可以影响 model，但无法安全地控制 runtime behavior。

本项目使用结构化 Pack contribution，因此可以做到：

```text
tools are formally registered
policies are enforceable
workflow hints are inspectable
trace events can show Pack influence
invalid Packs can be rejected
frontend can display Pack metadata
Kernel base safety cannot be bypassed
```

相比原始 prompt injection，这种方式让 Pack 行为更加稳定、更加可观察。

---

## 总结

在运行过程中，Kernel 并不会让 Pack 来执行 Agent loop。

相反：

```text
Pack contributes structured behavior.
Kernel assembles RuntimeContext.
DecisionProvider proposes Action.
Kernel enforces Policy.
Kernel executes Tools.
Kernel records Trace.
Frontend displays Events.
```

这种方式让 Kernel 保持稳定，同时允许 Pack 行为被替换和扩展。
