[English Version](./README-EN_02.md)

# Agent_Kernel_Pack2.0

> 一份围绕稳定 Kernel 与可加载行业 Pack 的模块化 Agent infrastructure 项目规划书

<p align="center">
  <strong>Stable Kernel. Industry Packs. Observable specialized Agents.</strong>
</p>

---

## 摘要

Agent_Kernel_Pack 是一个面向 specialized Agent 的模块化基础设施项目，通过稳定 Kernel 与可加载 Pack 的解耦，支持 Agent 的构建、扩展与演化。。

关键命题：

```text
Agent = Stable Kernel + Hot-swappable Pack
```

这个项目试图回答一个关键问题：**Agent 的核心运行机制，能否从具体行业能力中解耦出来，成为一个稳定、可复用、可持续演化的 Kernel；而不同场景的专业化能力，则以 Pack 的形式被独立加载、替换与扩展。**

### 1.0 是什么

`Agent_Kernel_Pack1.0`，也可称为旧版本名 `Mini Agent Kernel`，是第一阶段的架构验证版本。

它的主要目标是验证两件事：

- Kernel 能不能独立跑通；
- Pack 能不能被正确加载，并与 Kernel 形成有效协作。

换句话说，1.0 主要验证的是 **Kernel-Pack 解耦架构本身是否成立**。

### 2.0 是什么

`Agent_Kernel_Pack2.0` 是第二阶段的系统化验证版本。

它不再停留在“能不能跑通”的层面，而是进一步验证：

- 系统整体是否足够稳定；
- 同一个 Kernel 是否能够可靠加载多个不同行业的 Pack；
- Pack Protocol 是否足以支撑跨领域 specialized Agent 的行为承载。

当前 2.0 版本聚焦三个代表性领域作为验证样本：

- 金融分析
- 法务合同处理
- 医疗咨询

因此，2.0 的重点不是简单新增功能，而是**增强系统稳定性，并着重验证三个不同领域加载 Pack 的效能与可行性**。

简而言之：

- **1.0** 证明 `Kernel` 与 `Pack` 的基本架构可以成立；
- **2.0** 证明这套架构不仅能成立，而且能够更稳定地支撑多个行业 Pack 的加载与运行。

在这个基础上，项目进一步延伸出长期方向：让 Kernel 保持稳定、可观察、可治理，让 Pack 成为可制作、可分享、可下载、可评估的 specialized Agent 能力单元。

---

## 目录

- [项目定位](#项目定位)
- [2.0 使命陈述](#20-使命陈述)
- [为什么这个项目值得做](#为什么这个项目值得做)
- [核心架构方案](#核心架构方案)
- [Kernel 负责什么](#kernel-负责什么)
- [Pack 负责什么](#pack-负责什么)
- [Kernel 与 Pack 的通信协议](#kernel-与-pack-的通信协议)
- [2.0 验证范围](#20-验证范围)
- [代表性行业 Pack](#代表性行业-pack)
- [功能范围](#功能范围)
- [实现路径](#实现路径)
- [设计原则](#设计原则)
- [Roadmap](#roadmap)
- [长期平台方向](#长期平台方向)
- [未来的 Pack 形态](#未来的-pack-形态)
- [文档](#文档)
- [项目状态](#项目状态)
- [License](#license)

---

## 项目定位

`Agent_Kernel_Pack2.0` 是一个面向 specialized Agent 基础设施模型的项目立项尝试。

它的目标，不是再做一个垂直 Agent demo；它真正要验证的是：是否存在一种可复用的方式，可以让多个 specialized Agent 共用同一个 runtime 基座来构建。

整个项目建立在一个清晰的架构分层之上：

- **Kernel** 是稳定的 runtime 层；
- **Pack** 是结构化的领域行为层；
- 一个可用的 specialized Agent，由两者组合而成。

这意味着，这个项目本质上是在讨论：**架构、可扩展性，以及生态潜力**，而不只是一个单点应用。

---

## 2.0 使命陈述

2.0 版本的使命是：

> 在 Kernel-Pack 解耦思想已经被原则性验证之后，进一步验证：Kernel 是否能够可靠地加载行业 Pack，并在不改动核心 runtime 的前提下，支撑更贴近真实场景的 specialized Agent 行为。

这个使命包含三层含义。

### 1. 架构验证

证明 Kernel 与 Pack 的边界，不仅在概念上清晰，而且在运行上稳定。

### 2. 行业验证

证明同一个 runtime，能够承载具有真实差异的多个行业行为。

### 3. 生态验证

证明 Pack 最终有机会成为一种可复用、可分享、可评估的 specialized Agent 能力单元。

---

## 为什么这个项目值得做

很多早期 Agent 系统，往往从 prompt chain、CLI 工具，或者紧耦合的应用流程开始。

这种方式适合快速试验，但一旦系统开始需要支持下面这些能力，结构性问题就会暴露出来：

- 真实模型接入；
- tool execution；
- policy enforcement；
- frontend interaction；
- execution tracing；
- approval workflows；
- 多业务场景；
- 在不改写核心逻辑的前提下切换场景。

常见问题包括：

- CLI 逻辑和 Agent 行为混在一起；
- prompts 承担了过多系统职责；
- tools 被硬编码进 runtime 逻辑；
- workflow logic 与 output parsing 混杂；
- policy rules 分散、不一致；
- 每增加一个场景，都要修改 core runtime；
- 系统 observability 不足，可解释性较差。

`Agent_Kernel_Pack2.0` 要解决的正是这些问题，它的基本命题是：

> 保持 runtime 小而稳定，把场景行为放进 Pack，把整个过程做成可观察、可治理、可验证的系统。

---

## 核心架构方案

项目保留原有的核心技术公式不变：

```text
Agent = Stable Kernel + Hot-swappable Pack
```

它所主张的核心架构关系是：

- **Kernel** 回答的是“Agent 如何运行”；
- **Pack** 回答的是“在特定场景下，这个系统应该表现成什么样的 specialized Agent”。

这种拆分，能够清晰地区分：

- runtime control；
- domain behavior；
- policy enforcement；
- tool exposure；
- output shaping。

在实现上，项目并不把 Pack 当作一整段大 prompt 注入系统；相反，Pack 会被拆分成结构化贡献，再分别注册到 Kernel 的不同子系统里。

---

## Kernel 负责什么

Kernel 负责那些无论面对哪个行业，都必须稳定存在的 runtime 机制。

### Kernel 的稳定职责

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

### Kernel 的主要子系统

- **Runtime Loop**  
  控制一次 Agent turn，或者一个多步任务的执行过程。

- **State Manager**  
  维护 session state、messages、active Pack、pending approvals、step count 和 errors。

- **Context Builder**  
  根据 Kernel rules、session state、active Pack contributions、available tools、policy summaries 和 conversation history 组装 runtime context。

- **Decision Provider Interface**  
  让 runtime 可以在不改动 Kernel 逻辑的前提下，接入 mock、rule-based 或 LLM-based 的 decision providers。

- **Action Protocol**  
  用结构化 action 表示下一步行为：

```text
respond
call_tool
request_approval
finish
fail
```

- **Tool Registry**  
  注册来自 Pack 的 tools，并通过稳定 schema 向上层暴露。

- **Policy Engine**  
  判断某个 action 是 allowed、denied，还是 requires confirmation。

- **Trace Recorder**  
  记录 messages、context summaries、decisions、policy results、tool calls、tool results、errors 和 final responses。

- **Pack Loader**  
  负责 Packs 的加载、校验、激活与切换。

Kernel 定义的是：**系统如何安全地、可预测地、可观察地运行。**

---

## Pack 负责什么

Pack 负责场景相关、行业相关的行为定义。

### Pack 的结构化贡献

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

### 各字段含义

- **metadata**  
  描述 Pack 本身，供 runtime state、trace 展示和 frontend 呈现使用。

- **prompts**  
  提供领域相关的行为规则或 instructions。

- **tools**  
  声明应该通过 Kernel 暴露出来的工具。

- **policy_extensions**  
  增加场景专属约束，但不能覆盖 Kernel 的 base policy。

- **workflow_hints**  
  为决策过程提供柔性的 workflow 偏好。

- **output_style**  
  定义输出格式、语气或回答结构。

- **examples**  
  提供可选的 few-shot examples 或领域示例。

推荐的 tool 命名方式：

```text
pack_name.tool_name
```

Pack 可以塑造行为，但不拥有执行控制权。

---

## Kernel 与 Pack 的通信协议

Kernel 与 Pack 之间的通信模型，是一种结构化、稳定的协议。

它不是简单的 prompt injection。

### 1. 加载时的结构化贡献

当一个 Pack 被加载时，Kernel 会读取 manifest，并调用其注册入口。

```text
PackLoader.load(pack_name)
  -> read manifest
  -> validate compatibility
  -> call register_pack()
  -> validate PackContribution
```

Pack 返回的是结构化数据，而不是任意的 runtime instructions。

### 2. 运行时的子系统注册

通过校验之后，Pack contributions 会被分发到不同的 Kernel 子系统中。

```text
PackContribution.metadata           -> State.active_pack
PackContribution.prompts            -> ContextBuilder
PackContribution.tools              -> ToolRegistry
PackContribution.policy_extensions  -> PolicyEngine
PackContribution.workflow_hints     -> RuntimeContext / ContextBuilder
PackContribution.output_style       -> ResponseRenderer / ContextBuilder
PackContribution.examples           -> ContextBuilder
```

### 3. 决策时的上下文注入

在每一次 Agent turn 中，Context Builder 会把选定的 Pack 信息注入 runtime context，例如：

```text
active Pack metadata
Pack prompts
available Pack tools
policy summary
workflow hints
output preferences
few-shot examples
```

随后，Decision Provider 基于这些上下文来决定下一步 action。

Pack 会影响行为，但执行控制权始终保留在 Kernel 手中。

### 最小 Pack 结构

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

如果一个 Pack 无效，或者与当前 Kernel 不兼容，Kernel 应当拒绝它，同时不影响当前已经 active 的 Pack。

---

## 2.0 验证范围

2.0 不是一次普通的工程迭代，而是一次系统性的验证计划。

项目需要验证的内容包括：

### A. Pack 的稳定加载能力

- Pack 能否通过标准协议被加载；
- 在激活前能否完成兼容性检查；
- 无效 Pack 能否被安全拒绝；
- Pack switching 是否不会破坏 runtime。

### B. 跨行业行为承载能力

- 同一个 Kernel 能否支持实质上不同的行业任务；
- 行业行为是否可以通过 Pack contributions 改变，而不是通过 runtime 重写实现；
- tools、policies、workflows 和 outputs 是否能够随 Pack 而变化。

### C. runtime 可观察性

- 不同 Pack 的行为是否可以通过 trace events 被清晰观察；
- tool calls 与 policy decisions 是否始终可见；
- Pack 差异带来的行为变化是否能够被解释。

### D. 面向未来生态的准备度

- Pack 结构是否可以被文档化与复用；
- Pack 质量未来是否可以被对比；
- Pack 的价值未来是否可以被系统性评估。

---

## 代表性行业 Pack

2.0 版本选择三个行业方向作为初始验证案例。

### 金融分析 Pack

用于验证：Kernel 是否能够承载以数据分析、结构化输出，以及金融领域 tools / policies 为特征的行为模式。

### 法务合同处理 Pack

用于验证：Kernel 是否能够承载以文档审阅、风险提示，以及领域化输出规范为特征的行为模式。

### 医疗咨询 Pack

用于验证：Kernel 是否能够承载具有更强 policy constraints 和更谨慎输出风格的安全敏感型对话行为。

这三个 Pack 在任务模式、风险等级和输出形态上都具有明显差异，因此它们能够构成一组有意义的测试样本，用来判断 Pack 机制是否真正具备通用性。

---

## 功能范围

### 从原有架构中保留的核心功能范围

- Web Chat UI
- Agent session API
- 稳定的 Kernel runtime loop
- 结构化的 Pack loading protocol
- default Pack
- mock 或 rule-based decision provider
- basic tool registry
- tool 执行前的 policy checks
- trace event recording
- frontend trace visibility

### 2.0 在原始 MVP 基础上的重点强化

- 行业 Pack 的稳定加载；
- 跨行业行为验证；
- 更清晰的 Pack compatibility boundaries；
- 更强的 Pack-level comparison thinking；
- 为未来 Pack evaluation 提前做准备。

### 当前版本暂不纳入范围的内容

- multi-agent collaboration；
- vector database memory；
- complex DAG workflow engine；
- automatic Pack selection；
- large-scale tool ecosystem；
- 成熟的 Pack marketplace 运营能力；
- advanced autonomous planning。

---

## 实现路径

当前实现路径仍然保持克制和可测试。

### 1. 保持 Kernel 核心稳定

Kernel 仍然应当保持小而稳定、可预测。

### 2. 通过 Pack 加载行业行为

每个行业场景都应该通过 Pack contributions 表达，而不是写成 runtime 的硬编码分支。

### 3. 把 policy 控制权留在 Kernel 内部

最终的 policy 模型保持不变：

```text
FinalPolicy = KernelBasePolicy + ActivePackPolicyExtensions + SessionApprovals
```

并且 base policy 优先级最高：

```text
KernelBasePolicy.deny > PackPolicy.allow
```

### 4. 把 observability 作为一等公民

Trace、tool calls、policy decisions 和 Pack state 应当始终在产品表面可见。

### 5. 继续以 Web 界面作为主要交互面

主交互模型仍然是 Web Chat UI，而不是 CLI-first 的产品体验。

---

## 设计原则

### 1. Kernel 保持最小且稳定

Kernel 不应不断累积场景特定逻辑。

### 2. Pack 足够强，但必须受约束

Pack 可以塑造行为，但不能突破 Kernel 边界。

Pack 不应当：

```text
replace the runtime loop
bypass Kernel base policy
mutate global Kernel state directly
register tools without schema
override another Pack's tools silently
execute uncontrolled code during validation
```

### 3. Web Chat 是主要产品界面

系统应当在 UI 中清晰呈现 chat messages、current Pack、tool calls、policy decisions、approval requests 与 trace events。

### 4. 系统应始终存在一个默认 Pack

如果用户没有主动选择 Pack，系统就加载 `default_pack`。

这样可以简化 runtime 假设，也可以从一开始就验证 Pack 机制本身。

### 5. Pack 质量最终应该可衡量

一个长期可持续的 Pack 生态，不仅需要可加载，还需要可对比、可评估。

---

## Roadmap

### Phase 1 — Baseline Kernel completion

- 构建 Web Chat UI
- 实现基础 Agent Kernel API
- 添加 `MockDecisionProvider` 或 `RuleDecisionProvider`
- 添加 `default_pack`
- 添加 Pack validation
- 在 frontend 中展示 trace events

### Phase 2.0 — Stable industry Pack validation

核心目标：

> 验证一个稳定的 Kernel，是否能够通过统一协议，可靠承载多个行业 Pack。

主要工作：

- 验证 Pack 的稳定加载；
- 验证 Pack compatibility boundaries；
- 构建并测试三个代表性的行业 Pack；
- 对比不同 Pack 的行为差异；
- 在不重写 core logic 的前提下确保 runtime 稳定。

### 下一阶段技术演进

- 添加 `LLMDecisionProvider`
- 支持可配置的 model providers
- 增加结构化 model output protocol
- 把 tool specs 转换为 model tool-calling schemas
- 改进 prompt 与 context construction
- 支持显式的 runtime Pack switching
- 提升 UI 中的 Pack metadata 可见性
- 增强 policy 和 tool visualization
- 增加 Pack evaluation cases

---

## 长期平台方向

长期方向，是让项目从架构验证走向平台化形成。

规划中的战略方向包括：

- 上线围绕 Kernel 与 Pack 生态的网站；
- 让 Kernel 可以免费下载；
- 允许用户自己制作并上传 Pack；
- 允许用户下载其他人分享的 Pack；
- 建立系统性评估一个 Pack 价值的机制。

换句话说，未来的目标不只是让 Pack 可以被加载，而是让它们变成：

- 可复用的；
- 可分享的；
- 可对比的；
- 可评估的。

这才是一个真正 Pack 生态的基础。

### 商业化路径与阶段安排

如果 2.0 阶段验证成功，项目后续不会直接跳到“做一个大而全的平台”，而是会按能力成熟度逐步推进商业化。

整个路径会分成两个层次：

- **To C 路径**：先验证 Pack 的分发、下载、使用与社区流通是否成立；
- **To B 路径**：再验证 Pack 的评估、训练与企业级定制交付是否成立。

这两个方向并不是互相替代，而是前后衔接的：前者负责形成生态入口，后者负责形成可持续商业闭环。

#### 第一阶段：To C 生态入口

这一阶段的核心，不是先做重交付，而是先把用户侧的 Pack 流通机制跑通。

对应的产品安排包括：

- 上线项目网站，提供统一的 Kernel 与 Pack 展示入口；
- 允许用户免费下载 Kernel，降低试用门槛；
- 允许用户自己制作 Pack，并上传到平台；
- 允许用户浏览、下载、安装其他人分享的 Pack；
- 逐步沉淀 Pack 的元数据、使用反馈与基础评价信息。

这一阶段要验证的不是单个 Pack 能否“演示成功”，而是以下命题是否成立：

- Pack 是否可以作为独立能力单元被用户理解；
- Pack 是否真的具备被制作、被分享、被复用的价值；
- 一个稳定 Kernel，是否足以支撑用户围绕不同 Pack 形成使用习惯；
- 社区是否会自然产生对优质 Pack 的筛选与聚合需求。

如果这一阶段成立，那么项目就不只是一个技术架构实验，而开始具备平台化产品的用户基础。

#### 第二阶段：To B 能力深化

当 To C 阶段证明 Pack 具有流通价值之后，下一阶段的重点就不再只是“让 Pack 可下载”，而是“让 Pack 的质量可以被系统性定义、比较与提升”。

这一阶段的关键能力包括：

- 建立一套评估框架，系统性衡量一个 Pack 的有效性、稳定性、适配范围与实际业务价值；
- 基于历史任务、真实数据与目标指标，对 Pack 进行持续优化；
- 让 Pack 的改进过程，从人工经验驱动，逐步过渡到数据驱动与评测驱动；
- 形成面向企业场景的 Pack 定制与迭代方法论。

从长期看，这里的核心思想是：

> 如果神经网络可以通过数据与损失函数被训练，那么面向 specialized Agent 的 Pack，也应该逐步具备“可训练、可调优、可评测”的工程化演进路径。

这意味着，Pack 最终不只是静态配置包，而可能演化成一种可持续优化的行业能力资产。

#### 第三阶段：企业级 Pack 定制与交付

在具备评估与优化能力之后，项目就可以进入更明确的企业商业化路径。

对应的业务形态包括：

- 面向特定企业的数据、流程与任务类型，训练或调优专属 Pack；
- 为企业交付适配其内部知识结构、工具链与合规要求的 Pack；
- 以 Pack 为核心交付单元，提供定制开发、持续迭代与效果评估服务；
- 将企业内部沉淀的流程经验，转化为可复用、可维护、可升级的 Agent 能力组件。

在这个阶段，项目的商业价值不只来自软件分发，而来自对“行业能力资产化”的支撑：

- Kernel 提供稳定 runtime；
- Pack 承载行业经验；
- 评估与训练机制负责持续提高 Pack 质量；
- 企业付费的对象，最终会逐步从“一个 demo Agent”转向“可验证、可维护、可演化的专属 Pack 能力”。

#### 阶段关系总结

因此，整个商业化路径可以被概括为一条连续路线：

```text
Phase 2.0 validation
→ To C: Kernel free distribution + Pack creation/sharing/downloading
→ To B: Pack evaluation + Pack optimization/training
→ Enterprise delivery: custom Pack development and commercialization
```

这条路径的本质，不是先做流量、再做变现这么简单；它真正要建立的是一个新型的 Agent 能力生产方式：

- 先证明 Kernel 与 Pack 的解耦成立；
- 再证明 Pack 可以形成生态流通；
- 再证明 Pack 可以被评估和持续优化；
- 最终证明 Pack 可以成为企业愿意持续购买和迭代的能力载体。

如果这条路径走通，那么 `Agent_Kernel_Pack2.0` 的意义就不只是完成一个技术项目，而是为 specialized Agent 的平台化、产品化与商业化提供一条清晰的发展路线。

---

## 未来的 Pack 形态

项目的长期假设是：Pack 可能演化成一种 specialized Agent 能力的可复用单元。

未来的 Pack 可能会编码：

```text
domain prompts
tool choices
workflow preferences
safety policies
output formats
memory strategies
evaluation cases
```

如果这个假设成立，那么未来 specialized Agent 的构建方式，可能会越来越偏向于持续改进 Pack，而不是反复重建 runtime。

---

## 文档

详细设计文档见 [`docs/`](./docs/README.md)：

- [`01_kernel_definition.md`](./docs/01_kernel_definition.md)
- [`02_minimal_agent_mvp.md`](./docs/02_minimal_agent_mvp.md)
- [`03_pack_protocol.md`](./docs/03_pack_protocol.md)
- [`04_runtime_flow.md`](./docs/04_runtime_flow.md)

如需阅读中文版本，可对应查看：

- [`docs-cn/01_kernel_definition.md`](./docs-cn/01_kernel_definition.md)
- [`docs-cn/02_minimal_agent_mvp.md`](./docs-cn/02_minimal_agent_mvp.md)
- [`docs-cn/03_pack_protocol.md`](./docs-cn/03_pack_protocol.md)
- [`docs-cn/04_runtime_flow.md`](./docs-cn/04_runtime_flow.md)

---

## 项目状态

当前，这个项目已经明确进入 **2.0 项目立项阶段**。

当前优先事项包括：

```text
1. 保持稳定的 Kernel 边界；
2. 验证行业 Pack 的可靠加载；
3. 完成代表性 Pack 原型；
4. 保持 policy 与 execution control 在 Kernel 内部；
5. 提供 trace 级 observability 以支持对比和评估；
6. 为未来的 Pack 分享与 Pack 评估生态做准备。
```

---

## License

本项目计划采用 **MIT License** 发布。
