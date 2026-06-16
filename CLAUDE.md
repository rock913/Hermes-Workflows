# CLAUDE.md — Hermes-Workflows

> AI Agent 在此项目中的行为规范与上下文

## ⚠️ DevX 全局行为准则与 Git 规范

> 来源：Meta Phase 7 DevX 混合架构基础设施升级
> 本规范适用于交互式终端 (Tmux) 和非交互式飞书桥接两种运行环境。

1. **环境认知**：你可能运行在交互式终端 (Tmux) 或非交互式的飞书桥接中。严禁使用阻塞性交互命令 (`vim`, `nano`, `less`)。读取文件请用 `cat` 或 `head`。

2. **静默优先**：当前环境已开启 Auto Mode。对于确定性的依赖安装、Linter 执行、文件覆盖，请直接执行，遇到询问默认加 `-y`，尽量减少向用户索要权限。

3. **隔离红线**：当前所有项目运行在同一 Linux 账户下。**绝对禁止**通过 `cd ../` 访问或修改当前项目根目录以外的任何文件。所有操作必须在当前仓库目录内完成。

4. **Git 短期分支流 (SLAIB)**：
   - `main` 分支已被写保护，无法直接 push。
   - 任何修改前，必须执行 `git checkout -b <type>/<desc>`（例如 `feat/add-login`, `fix/oom-error`, `refactor/scheduler`）。
   - 修改完成后推送分支到远程。

5. **PR 门禁**：
   - 推送分支后，使用 GitHub CLI (`gh pr create --fill`) 发起 Pull Request。
   - 等待人类主理人在 GitHub 上审批并 Squash and Merge。
   - **严禁**尝试绕过 PR 机制直接 push main。

6. **自动清理**：
   - PR 被 Squash and Merge 后，远程分支会自动删除。
   - 本地执行 `git fetch --prune` 清理已删除的远程分支引用。
   - 本地分支可手动删除：`git branch -d <type>/<desc>`。

## Contract-First Development (Contract-First 契约优先)

> 来源：`conventions/devx-rules.md` §8 | Fable 5 架构哲学

### 本项目的三层契约

**Interface Contract**:
- YAML 模板 Schema: `name, version, compatible_sros_version, steps[].tool/params/expected_output`
- MCP Consumer: 通过 `docs/mcp_mount_spec.md` 定义的工具契约调用 SROS/ARC
- system_prompt: DeepSeek 硬化格式 (Role:/Input:/Steps:/Output format:/Constraints:)

**Behavior Contract**:
- `hermes-cli validate` — YAML schema 校验 (7 templates)
- `hermes-cli validate-prompts` — Prompt 风格校验 (H6)
- `hermes-cli run --dry-run` — 工作流模拟执行

**Cross-System Contract**:
- SROS MCP: 7 tools (SSE transport, `docs/mcp_mount_spec.md`)
- ARC MCP: 4 tools (stdio transport, DW5)
- 新增 MCP tool → 更新 `contracts/mcp/` + 创建验证模板 (`hermes_*_mcp_test.yaml`)

### Prompt 编写规范
- 所有 system_prompt 使用结构化指令格式
- Input/Output/Constraints 三要素必填
- 禁止 Claude 角色扮演风格 ("你是一位..."、"请深呼吸")
- 禁止 >3 步的 SOP 流程

## 架构依赖
