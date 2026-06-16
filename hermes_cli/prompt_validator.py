"""
Prompt 风格校验器 — 检查 system_prompt 是否符合 DeepSeek 硬核指令格式

Proposal: meta-docs/proposals/pending/Hermes-DeepSeek-Prompt-Hardening.md
"""

import re
import yaml
from pathlib import Path
from typing import Any


# DeepSeek 结构化指令必须包含的章节
DEEPSEEK_REQUIRED_SECTIONS = [
    ("Role:", "ROLE_DECLARATION"),
    ("Input:", "INPUT_SCHEMA"),
    ("Output format:", "OUTPUT_FORMAT"),
]

# Claude 角色扮演残留模式（应被替换为结构化指令）
CLAUDE_ANTIPATTERNS = [
    (r"你是一位", "ROLEPLAY_PERSONA"),
    (r"请深呼吸", "BREATHE_INSTRUCTION"),
    (r"一步步思考", "STEP_BY_STEP"),
    (r"请仔细", "POLITENESS_MARKER"),
    (r"请(?!使用工具)", "PLEASE_PATTERN"),
]


def validate_prompt_style(system_prompt: str) -> list[dict[str, Any]]:
    """
    校验单个 system_prompt 是否符合 DeepSeek 结构化指令格式。
    返回问题列表，空列表 = 通过。
    """
    issues: list[dict[str, Any]] = []

    # 检查必需章节
    for pattern, label in DEEPSEEK_REQUIRED_SECTIONS:
        if not re.search(pattern, system_prompt):
            issues.append({
                "severity": "error",
                "code": f"MISSING_{label}",
                "message": f"缺少必需章节: {label} — 期望包含 '{pattern}'",
            })

    # 检查 Claude 残留模式
    for pattern, label in CLAUDE_ANTIPATTERNS:
        if re.search(pattern, system_prompt):
            issues.append({
                "severity": "warning",
                "code": f"CLAUDE_REMNANT_{label}",
                "message": f"检测到 Claude 风格残留: {label} — 建议替换为结构化指令",
            })

    # 检查是否有超过 3 步的 SOP 流程（应拆分为独立契约）
    step_matches = re.findall(r"^\d+\.", system_prompt, re.MULTILINE)
    if len(step_matches) > 3:
        issues.append({
            "severity": "warning",
            "code": "TOO_MANY_STEPS",
            "message": f"检测到 {len(step_matches)} 步 SOP 流程 — 步骤 >3 时应拆分为独立契约",
        })

    return issues


def validate_template_prompt(template: dict) -> list[dict[str, Any]]:
    """校验单个模板的 prompt 风格"""
    issues: list[dict[str, Any]] = []

    # 检查 agent role 风格
    for agent in template.get("agents", []):
        role = agent.get("role", "")
        for pattern, label in CLAUDE_ANTIPATTERNS:
            if re.search(pattern, role):
                issues.append({
                    "severity": "warning",
                    "code": f"AGENT_ROLE_{label}",
                    "message": f"Agent '{agent.get('name')}' role 含 Claude 残留: {label}",
                })

    # 检查 system_prompt 字段（如果存在）
    if "system_prompt" in template:
        issues.extend(validate_prompt_style(template["system_prompt"]))

    return issues


def validate_all_templates(templates_dir: str) -> dict[str, list[dict[str, Any]]]:
    """校验目录下所有 YAML 模板的 prompt 风格"""
    results: dict[str, list[dict[str, Any]]] = {}
    tmpl_dir = Path(templates_dir)
    if not tmpl_dir.exists():
        return results

    for yaml_file in sorted(tmpl_dir.rglob("*.yaml")):
        try:
            template = yaml.safe_load(yaml_file.read_text())
            if template and isinstance(template, dict):
                issues = validate_template_prompt(template)
                if issues:
                    results[str(yaml_file)] = issues
        except yaml.YAMLError as e:
            results[str(yaml_file)] = [{
                "severity": "error",
                "code": "YAML_PARSE_ERROR",
                "message": str(e),
            }]
    return results


def print_validation_report(results: dict[str, list[dict[str, Any]]]) -> int:
    """打印校验报告，返回 issue 总数"""
    total_issues = 0
    for file_path, issues in results.items():
        print(f"\n📄 {file_path}")
        for issue in issues:
            icon = "❌" if issue["severity"] == "error" else "⚠️"
            print(f"  {icon} [{issue['code']}] {issue['message']}")
            total_issues += 1

    if total_issues == 0:
        print("\n✅ 所有模板通过 DeepSeek Prompt 风格校验")
    else:
        print(f"\n📊 总计: {total_issues} 个问题 ({sum(1 for fp, issues in results.items() for i in issues if i['severity'] == 'error')} errors, {sum(1 for fp, issues in results.items() for i in issues if i['severity'] == 'warning')} warnings)")

    return total_issues
