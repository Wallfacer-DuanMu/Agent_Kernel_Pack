# UI Demo Tasks

下面这些任务适合在 `Agent Kernel Console` 中演示。

## 基础演示

- `hello agent`
- `list .`
- `read README.md`
- `search Agent Kernel`
- `run command: python main.py --help`

## Pack 对比演示

- 切换到 `default_pack` 后运行 `hello agent`
- 切换到 `default_pack` 后运行 `list .`

## Trace / Policy 演示

- `run command: python main.py --version`
- `run command: python main.py --help`

## 说明

危险命令不建议实际执行。若用户尝试明显破坏性的命令，应由 Policy 拦截或要求确认。
