# 文档说明

本目录提供 `Mini Agent Kernel` 设计文档的中文版。

这些文档聚焦于项目中的几个核心架构问题：

- 在这个项目里，Kernel 的含义是什么？
- 最小可用的 Agent MVP 应该是什么样？
- Pack 是什么？
- Pack 如何与 Kernel 通信？
- 一次 Agent turn 的运行流程是什么？

## 文档列表

### 1. Kernel 定义

参见：[01_kernel_definition.md](./01_kernel_definition.md)

说明项目中 `Kernel` 的定义、职责边界，以及哪些内容应当放在 Kernel 之外。

### 2. 最小 Agent MVP

参见：[02_minimal_agent_mvp.md](./02_minimal_agent_mvp.md)

定义第一版中最小但有意义的 Agent 运行闭环。

### 3. Pack Protocol

参见：[03_pack_protocol.md](./03_pack_protocol.md)

说明 Pack 的定义、可提供的能力、校验方式，以及它如何与 Kernel 各子系统协作。

### 4. Runtime Flow

参见：[04_runtime_flow.md](./04_runtime_flow.md)

描述从用户消息进入系统，到决策、policy 检查、tool 执行、trace 记录，再到前端事件输出的完整流程。

## 核心总结

```text
Kernel = 稳定的运行时层
Pack   = 结构化的行为包
```

Kernel 负责：

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

Pack 负责：

```text
metadata
prompts
tools
policy extensions
workflow hints
output style
examples
```

本项目最关键的设计原则是：

> Pack 足够强，可以塑造 Agent 的行为；但它不能破坏、绕过或替代 Kernel。
