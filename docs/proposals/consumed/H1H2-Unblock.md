# Hermes PRD 更新提案：H1 + H2 框架验证与 SROS MCP 挂载

> 目标主 PRD：`02-Agent_Orchestration/Hermes-Workflows/README.md`
> 提案日期：2026-05-19
> 交付日期：2026-06-01
> 驱动来源：总 PRD Phase 5 — H1 (无依赖) + H2 (SROS S2 ✅ 5/12 已满足) 均可立即启动
> 状态：✅ 已交付
>
> ⚡ **Quick Start**：在 `02-Agent_Orchestration/Hermes-Workflows/` 目录下打开 Claude Code，复制以下内容作为第一条消息：
> "执行 meta-docs/proposals/pending/Hermes-H1H2-Unblock.md 中的提案。范围：H1 (Hermes 框架安装 + 模板语法 dry-run 验证) + H2 (SROS MCP Gateway 工具挂载验证)。验收标准见文件末尾 checklist。完成后更新 ROADMAP.md (H1+H2→✅) 并回复 done。"

## 动机 (Why)

Hermes-Workflows 自 V0.1 (2026-05-12) 完成模板库后，H1–H5 全部处于 ❌ 状态。但实际上：
- **H1**：无任何前置依赖，仅需安装 Hermes 框架 + 验证已有 YAML 模板语法
- **H2**：前置条件 SROS S2 (`sros-hpc-server` MCP) 自 5/12 已满足

H1+H2 是 Hermes 从"纯 YAML 文档"到"可验证框架"的第一步。这两个任务无需等待 ARC Data-Wiki，可立即并行推进。

## 提议内容

### H1: Hermes 框架安装 + 模板语法验证（0.5w）

- 按 Hermes 上游文档安装框架
- 对已有 3 个 YAML 模板分别执行 dry-run 语法验证：
  - `templates/eda_pipeline.yaml`
  - `templates/ml_experiment.yaml`
  - `projects/sxmu_mdd_digital_twin.yaml`
- 记录 Hermes 版本号 + 兼容性说明到 README

### H2: SROS MCP 工具挂载验证（1w）

- 在 Hermes 工作流中挂载 SROS MCP Gateway (SSE 协议, `http://localhost:8000`)
- 验证 MCP 工具发现：`sros db query`、`sros-hpc-server` 工具列表正确暴露
- 编写最小 `hermes_mcp_test.yaml` 工作流：调用 `sros db query` → 验证返回 DuckDB 数据
- 记录挂载配置模板到 `docs/mcp_mount_spec.md`

### 不做的事

- ❌ ARC MCP 挂载（H3，需 ARC A3 完成）
- ❌ SXMU_MDD 端到端 dry-run（H4，需 H3）

## 验收标准

- [x] Hermes 框架已安装，版本号记录在 README
- [x] 3 个 YAML 模板全部通过 dry-run 语法验证
- [x] SROS MCP Gateway 工具发现成功（≥ 1 个 tool 可调用）
- [x] `hermes_mcp_test.yaml` 工作流执行成功（mock 模式可接受）
- [x] `docs/mcp_mount_spec.md` 中补充 SROS 挂载实操记录
- [x] Hermes ROADMAP.md 中 H1+H2 状态更新为 ✅
- [x] 本提案移至 `proposals/delivered/`

## 参考实现

- MCP 挂载规范：`02-Agent_Orchestration/Hermes-Workflows/docs/mcp_mount_spec.md`
- SROS MCP Gateway：SROS MCP SSE endpoint (`http://localhost:8000`)，工具列表见 `01-Core_Infra/SROS/src/sros/skills/rpc.py`
- 现有 YAML 模板：`templates/eda_pipeline.yaml`、`templates/ml_experiment.yaml`、`projects/sxmu_mdd_digital_twin.yaml`
