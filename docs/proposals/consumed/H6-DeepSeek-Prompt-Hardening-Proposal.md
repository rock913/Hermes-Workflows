# Hermes PRD 更新提案：DeepSeek Prompt 风格硬化 — 从角色扮演到结构化指令

> 目标主 PRD：`02-Agent_Orchestration/Hermes-Workflows/README.md`
> 提案日期：2026-06-15
> 驱动来源：`meta-docs/strategy/upgrade-notes/0615-DeepSeek v4 Pro 架构适配与非对称成本优势指南.md`
>
> ⚡ **Quick Start**：在 `02-Agent_Orchestration/Hermes-Workflows/` 目录下打开 Claude Code，复制以下内容作为第一条消息：
> "执行 meta-docs/proposals/pending/Hermes-DeepSeek-Prompt-Hardening.md 中的提案。范围：重构 Hermes 模板 YAML 的 system_prompt 字段，将角色扮演风格改为结构化指令风格以适配 DeepSeek v4 Pro；新增 prompt 风格校验工具。
>  验收标准见文件末尾 checklist。完成后更新自身 ROADMAP.md (H6→✅) + 主 PRD (README.md)，并回复 done。"

## 动机 (Why)

DeepSeek v4 Pro 与 Claude 系列在 Prompt 响应模式上有显著差异：

| 维度 | Claude 风格 | DeepSeek 风格 |
|------|-----------|-------------|
| Prompt 风格 | 角色扮演 + 温和引导 ("你是一位经验丰富的架构法师，请深呼吸，一步步思考...") | 硬核指令 + 结构化约束 ("输入: X, 输出: Y, 格式: Z") |
| 最佳激活模式 | 长 system prompt + 场景设定 | 短 system prompt + JSON Schema + 伪代码 |
| 容错行为 | 优雅降级，不确定时多问 | 不确定时直接推理（需要硬边界约束） |

当前 Hermes 的 7 个工作流模板中，`system_prompt` 字段普遍采用 Claude 友好的角色扮演风格。切换到 DeepSeek v4 Pro 后，这些 Prompt 会降低 DeepSeek 的推理精准度（尤其是 tool calling 的准确率）。

**核心原则**：Prompt 风格切换不影响 YAML 模板结构，只修改 `system_prompt` 字段的内容风格。同时需要新增一个 Prompt 风格校验工具，确保未来新增的模板都符合 DeepSeek 硬核指令格式。

## 提议内容

### Task 1: 重构所有模板的 system_prompt (H6, 1.5d)

**7 个模板的 system_prompt 风格转换**：

以 `templates/eda_pipeline.yaml` 为例：

```yaml
# 旧 (Claude 风格 — 角色扮演)
system_prompt: |
  你是一位经验丰富的数据科学家。请深呼吸，一步步思考。
  你的任务是对提供的临床数据集执行探索性数据分析 (EDA)。
  请仔细检查数据质量，发现异常值，并生成一份全面的报告。

# 新 (DeepSeek 风格 — 结构化指令)
system_prompt: |
  Role: EDA pipeline executor for clinical datasets.
  Input: TSV/CSV with columns {schema_columns}.
  Steps:
  1. Load data → validate schema against {expected_schema}
  2. Descriptive stats: mean, std, min, max, missing% for numeric columns
  3. Outlier detection: IQR method, flag >3σ
  4. Output: JSON {eda_result} with keys [summary, outliers, warnings]
  Constraints:
  - Do NOT modify input files
  - If >50% missing in any column → mark as ERR_INSUFFICIENT_DATA
  - Use tools: [sros_db_query, sros_hpc_submit]
  Output format: strict JSON, no markdown wrapping.
```

**统一转换规则**：
1. 去掉"你是一位..."角色设定 → 替换为 `Role: <functional description>`
2. 去掉"请深呼吸，一步步思考" → 替换为 `Steps:` 编号列表
3. 输入/输出用 `Input:` / `Output:` 明确标注，附 JSON Schema
4. 新增 `Constraints:` 硬边界（不做的事）
5. 新增 `Output format:` 强制输出格式

### Task 2: Prompt 风格校验工具 (0.5d)

**新增** (`hermes_cli/prompt_validator.py`)：

```python
"""
Prompt 风格校验器 — 检查 system_prompt 是否符合 DeepSeek 硬核指令格式
"""

import re
import yaml
from typing import list


DEEPSEEK_REQUIRED_SECTIONS = [
    (r'Role:', 'ROLE_DECLARATION'),
    (r'Steps?:', 'STEPS_ENUMERATION'),
    (r'Output(?:\s*format)?:', 'OUTPUT_FORMAT'),
]

CLAUDE_ANTIPATTERNS = [
    (r'你是一位', 'ROLEPLAY_PERSONA'),
    (r'请深呼吸', 'BREATHE_INSTRUCTION'),
    (r'一步步思考', 'STEP_BY_STEP'),
    (r'请仔细', 'POLITENESS_MARKER'),
    (r'请(?!使用工具)', 'PLEASE_PATTERN'),
]


def validate_prompt_style(system_prompt: str) -> list[dict]:
    """
    返回警告列表。空列表 = 通过。
    """
    issues = []
    
    # 检查必需章节
    for pattern, label in DEEPSEEK_REQUIRED_SECTIONS:
        if not re.search(pattern, system_prompt):
            issues.append({
                "severity": "error",
                "code": f"MISSING_{label}",
                "message": f"缺少必需章节: {label} ({pattern})"
            })
    
    # 检查 Claude 残留模式
    for pattern, label in CLAUDE_ANTIPATTERNS:
        if re.search(pattern, system_prompt):
            issues.append({
                "severity": "warning",
                "code": f"CLAUDE_REMNANT_{label}",
                "message": f"检测到 Claude 风格残留: {label} — 建议替换为结构化指令"
            })
    
    return issues


def validate_all_templates(templates_dir: str = "templates") -> dict[str, list]:
    """校验所有 YAML 模板的 system_prompt"""
    results = {}
    for yaml_file in Path(templates_dir).rglob("*.yaml"):
        template = yaml.safe_load(yaml_file.read_text())
        if "system_prompt" in template:
            results[str(yaml_file)] = validate_prompt_style(template["system_prompt"])
    return results
```

**CLI 入口**：
```bash
hermes-cli validate-prompts          # 校验所有模板
hermes-cli validate-prompts --fix    # 交互式修复建议
```

## 验收标准

- [ ] 7 个 YAML 模板的 `system_prompt` 全部重构为 DeepSeek 结构化指令格式
- [ ] 所有模板通过 `hermes-cli validate-prompts` 零 error
- [ ] `hermes-cli` 新增 `validate-prompts` 命令
- [ ] ≥ 3 个 prompt_validator 单元测试（合法 prompt / 缺失 Role / Claude 残留）
- [ ] Hermes ROADMAP.md 新增 H6 (Prompt Hardening) 并标记 ✅
- [ ] 主 PRD (`README.md`) 新增"DeepSeek Prompt 适配"章节，记录转换规则
- [ ] 本提案移至 `proposals/delivered/`

## 参考实现

- Hermes 模板目录：`templates/eda_pipeline.yaml`, `templates/ml_experiment.yaml` 等 — 当前 system_prompt 字段
- Hermes CLI 验证器：`hermes_cli/` — 已有 `hermes-cli validate` (YAML schema 校验)，可扩展
- SROS adapter 联动：P3 提案的 `mcp_openai_adapter.py` — Hermes 调用 DeepSeek 时需同时使用 MCP Adapter + 硬化 Prompt
- 策略文档：`meta-docs/strategy/upgrade-notes/0615-DeepSeek v4 Pro 架构适配与非对称成本优势指南.md` — §2.2 Prompt 风格转变
