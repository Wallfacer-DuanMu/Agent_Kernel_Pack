# Frontend Console

## 设计目标

Agent Kernel Console 是一个轻量、本地可运行的展示型前端，用来说明 `Kernel + Pack => Runtime Execution` 的结构关系。它不是在线编辑器，也不是完整生产级平台。

## 三栏布局

- 左侧 `Kernel Status`：展示运行时、状态、动作、能力、策略、上下文、追踪、恢复与加载信息。
- 中间 `Task / Execution`：输入任务、执行任务、查看 Agent 输出、Trace 时间线、Tool Calls、Policy Decisions、Context 和 Raw State。
- 右侧 `Pack Details`：展示当前 Pack 的 manifest、workflow、policy、tools、prompts、output 和 skills。

## Kernel Status

左侧面板只做状态展示，不修改核心内核逻辑。它用于帮助用户理解内核当前具备哪些能力、使用了哪些策略、以及运行态是否可用。

## Runtime Execution

中间面板负责一次任务的执行结果展示：

- 输入任务；
- 点击 Run 执行；
- 点击 Reset 清空当前 UI 会话；
- 查看 Agent 输出、执行轨迹、工具调用与策略决策。

## Pack Details

右侧面板用于查看当前 Pack 的静态信息与可选扩展内容。用户可以切换 Pack，但不需要修改源码。

## Skill 导入流程

前端支持导入单个 Skill JSON 文件：

1. 选择 `json` 文件；
2. 前端校验基础字段；
3. 通过后仅加入当前会话；
4. 之后可以在 Pack Skills 区域查看。

Skill 不会被写回源码，也不会自动注册为全局工具。

## 常见问题

### 为什么不支持嵌套 expander？

为了避免 Streamlit 的嵌套 expander 异常，二级详情统一使用 `selectbox`、`json`、`code` 或 `tabs` 展示。

### 为什么没有在线编辑功能？

第一版目标是展示架构与运行效果，不是构建在线 IDE。

### 为什么没有远程 Pack 市场？

为了保持项目轻量和兼容性，当前阶段不引入复杂网络功能或下载机制。

### 如何验证 CLI 仍然可用？

运行：

```bash
python main.py --help
python main.py --version
python main.py "hello"
```
