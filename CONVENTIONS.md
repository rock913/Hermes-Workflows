# Hermes-Workflows 局部开发法则

> 本文件是 Hermes-Workflows 子项目的"地方法规"。
> 全局宪法见根目录 `AI_RULES.md`。
> 功能规格见 `docs/PRD.md` (V1.0)。

## 技术栈
- 模板：YAML（工作流定义）
- CLI：Python (hermes-cli)
- MCP Consumer：通过 MCP 协议调用 SROS/ARC 工具

## 架构红线 (Hard Boundaries)
1. **不耦合进 SROS 核心**：Hermes 是独立的 MCP 消费者，不能被 SROS 源码 import
2. **只做科学流水线编排**：Hermes 不得在任何阶段拥有 SROS/ARC 仓库写权限
3. **YAML 模板版本绑定**：每个模板标注兼容的 SROS/ARC 版本
4. **独立 MCP Consumer**：通过 `docs/mcp_mount_spec.md` 定义的工具契约调用 SROS/ARC

## 模板规范
- 所有模板必须包含：`name`, `version`, `compatible_sros_version`, `steps`
- 每个 step 必须包含：`tool` (MCP tool name), `params`, `expected_output`
- system_prompt 使用 DeepSeek 硬化格式：`Role:` + `Input:` + `Steps:` + `Output format:` + `Constraints:`

## Prompt 风格 (DeepSeek 适配)
- ❌ 禁止：角色扮演 ("你是一位...")、温和引导 ("请深呼吸，一步步思考")
- ✅ 必须：结构化指令 (`Role:`, `Input:`, `Steps:`, `Output format:`, `Constraints:`)
- 校验：`hermes-cli validate-prompts`

## 测试
- `hermes-cli validate` — YAML schema 校验
- `hermes-cli validate-prompts` — Prompt 风格校验
- `hermes-cli run --dry-run` — 工作流模拟执行

## 禁止行为
- ❌ 在模板中直接写 Python 代码
- ❌ 耦合 SROS/ARC 的内部实现
- ❌ 使用 Claude 角色扮演风格的 system_prompt
