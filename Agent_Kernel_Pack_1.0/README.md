# Agent Kernel

一个实验性的轻型 Agent Kernel 项目。

## 项目简介

Agent Kernel 采用 **固定通用内核 + 可热插拔外置 Pack** 的方式组织能力：

- 内核负责运行时、状态、动作、权限与追踪；
- Pack 负责场景化工作流、工具、策略扩展与输出渲染。

项目目标是做到可运行、可展示、结构清楚，并且不依赖真实 LLM API 也能完成演示。

## 项目定位

- 轻型
- 实验性
- 可运行
- 可展示
- 便于后续扩展

## 核心特性

- 统一 `Action` 协议
- 基础 `Runtime` 循环
- 工具注册与执行
- 权限拦截与确认
- Trace 记录
- Pack 加载与默认 Pack
- 轻量 Streamlit 控制台
- 支持 Mock 模式与可选 LLM 模式切换
- 无需真实 LLM API 即可演示

## 架构概览

项目分为两层：

- 固定通用内核：`core/`、`capabilities/`、`policy/`、`tracing/`
- 可插拔外置 Pack：`packs/<pack_name>/`

前端遵循：

- `Kernel + Pack => Runtime Execution`

更多说明见：

- `docs/architecture.md`
- `docs/pack_protocol.md`
- `docs/frontend_console.md`

## 环境要求

- Python `3.11` 或 `3.12`
- 推荐使用项目本地虚拟环境 `.venv`
- 不建议直接在全局 Python 或 Anaconda `base` 环境中安装依赖

## 快速开始

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd "Agent Kernel"
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
```

### 3. 激活虚拟环境

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

如果 PowerShell 阻止脚本执行，可先在当前终端运行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

然后再次执行激活命令。

#### Windows CMD

```bat
.venv\Scripts\activate.bat
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

### 4. 安装依赖

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. 查看帮助与版本

```bash
python main.py --help
python main.py --version
```

### 6. 基础运行

```bash
python main.py "hello agent"
```

### 7. 使用默认 Pack

```bash
python main.py --pack default_pack "list ."
```

### 8. 启动前端控制台

```bash
streamlit run ui/streamlit_app.py
```

### Mock 模式与 LLM 模式

默认进入 Mock 模式。该模式不需要 API Key，适合新用户、离线演示和测试。

如果你希望连接大模型，请在右上角或侧边栏开启 LLM mode，并填写：

- Provider（模型厂商）
- API Base URL
- API Key
- Model
- Optional System Prompt
- Temperature

当前内置了常见厂商预设（可继续自定义修改）：

- OpenAI Compatible
- Kimi Compatible
- Qwen Compatible（通义千问）
- DeepSeek Compatible
- Zhipu Compatible（智谱）
- Anthropic Compatible

点击 `Save` 后，配置会保存在项目根目录的 `.agent_kernel_llm.json` 中；点击 `Clear` 可清除本地保存的敏感信息。

开启 LLM mode 后，运行时会真正调用你配置的 OpenAI-compatible 接口，而不是使用内置 Mock 回复。

### 9. 运行测试

```bash
pytest
```

## 前端控制台说明

前端采用三栏布局：

- 左侧 `Kernel Status`：查看 runtime、state、actions、policy、context、tracing 与 recovery；
- 中间 `Task / Execution`：输入任务、运行、查看输出、trace、tool calls 与 policy decisions；
- 右侧 `Pack Details`：查看 manifest、workflow、tools、prompts、output 与 skills。

支持的轻交互包括：

- 切换 Pack；
- 调整 Max Steps；
- 导入 Skill JSON；
- 查看当前运行结果；
- 查看 Trace / Policy / Actions。

## Pack 机制说明

默认情况下会加载 `packs/default_pack`。你也可以通过 `--pack` 指定其他 Pack 路径或 Pack 名称。

Pack 通过 manifest 声明入口文件，并暴露工作流、策略、工具、输出与提示词。

## Skill 导入说明

前端支持导入单个 Skill JSON 作为当前会话临时 Skill。导入后可以在 Pack Skills 中查看，但不会写回源码或持久化到后端仓库。

## 示例命令

更多可复制命令见 `examples/demo_tasks.md` 和 `examples/ui_demo_tasks.md`。

## Trace 说明

运行任务后，Trace 会写入 `traces/` 目录下的 JSONL 文件。

每条记录会包含：

- session id
- run id
- step
- action type
- tool name
- policy decision
- result summary
- error

## 常见问题

### 为什么推荐使用 `.venv`？

使用项目本地虚拟环境可以避免全局环境或 Anaconda `base` 中已有依赖影响项目运行结果，保证你和其他下载者获得更一致的行为。

### 如果安装后 `streamlit` 命令不可用怎么办？

优先确认已经激活虚拟环境；如果仍有问题，可以改用：

```bash
python -m streamlit run ui/streamlit_app.py
```

### 如果测试里看到第三方库 warning 怎么办？

项目已经在 `pytest.ini` 中对已知的 `protobuf` 弃用 warning 做了定向过滤。如果你仍然遇到异常，请先确认：

- 当前已激活 `.venv`
- 已重新执行 `pip install -r requirements.txt`
- Python 版本符合要求

### 如何更新依赖？

新增项目依赖后，请同步更新 `requirements.txt`，然后重新安装并运行：

```bash
pip install -r requirements.txt
pytest
```

## 面向开发者的建议

- 提交前至少运行一次 `pytest`
- 新增依赖时同步更新 `requirements.txt`
- 避免把 `.venv/`、`traces/`、`.pytest_cache/` 提交到仓库
- 如果使用不同 Python 版本，请优先验证 `3.11` 或 `3.12`

## 项目边界

第一版前端只负责展示和轻交互，不做：

- 在线编辑 Python 源码；
- 拖拽 Workflow；
- 远程 Pack 市场；
- 多用户系统；
- 登录权限系统；
- 复杂数据库；
- 可视化 Agent Graph 编辑器。

## 测试方式

```bash
pytest
```

## 后续规划

- 保持内核稳定
- 扩展更多 Pack 示例
- 维持最小依赖
- 继续完善测试与展示材料
