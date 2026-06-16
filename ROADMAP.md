# Hermes-Workflows ROADMAP

> Hermes 工作流模板库 — L3 编排层进度追踪
> 本文件是总 Meta 项目 ROADMAP.md 的 Hermes 侧权威进度源

## 文档索引

| 文档 | 用途 |
|------|------|
| `README.md` | 模板库概述 (Hermes 主 PRD — 定位与设计原则) |
| `docs/mcp_mount_spec.md` | SROS + ARC MCP 工具挂载规范 |
| `projects/sxmu_mdd_digital_twin.yaml` | SXMU_MDD 5 阶段流水线 (Hermes 特性 PRD) |
| `templates/` | 通用可复用模板 |
| `ROADMAP.md` | Hermes 进度追踪 |

---

## 当前能力矩阵

| 交付物 | 状态 | 说明 |
|--------|------|------|
| 工作流模板库结构 | ✅ 已完成 | `templates/` + `projects/` + `docs/` |
| MCP 挂载规范 | ✅ 已完成 | `docs/mcp_mount_spec.md` |
| EDA 通用模板 | ✅ 已完成 | `templates/eda_pipeline.yaml` |
| ML 实验模板 | ✅ 已完成 | `templates/ml_experiment.yaml` |
| SXMU_MDD 流水线 | ✅ 已完成 | `projects/sxmu_mdd_digital_twin.yaml` (v1.0) |
| Hermes 框架集成验证 | ✅ 已完成 | `hermes-cli` v0.3.0, 5 模板 dry-run 通过 |
| SROS MCP 工具挂载验证 | ✅ 已完成 | 7 tools 声明验证, `hermes_mcp_test.yaml` |
| ARC MCP 工具挂载验证 | ✅ 已完成 | DW5 4 tools 声明验证, `hermes_arc_mcp_test.yaml` |

---

## 里程碑

### Now → Next

| 里程碑 | 目标 | 状态 | 驱动来源 |
|--------|------|------|---------|
| **V0.1** | 模板库骨架 + SXMU 流水线 v1.0 | ✅ Done | SXMU PRD |
| **V0.2** | Hermes 框架 dry-run 通过 | ✅ Done | H1 |
| **V0.3** | SROS MCP 工具实挂验证 | ✅ Done | H2, SROS S2 满足 |
| **V0.4** | ARC MCP 工具实挂验证 | ✅ Done | H3, ARC DW5 满足 |
| **V1.0** | 首个端到端科研流水线生产运行 | ❌ | Phase 5 全部交付物 |

### SXMU 驱动开发任务

| Task ID | 描述 | 优先级 | 预估工作量 | 前置依赖 | 状态 |
|---------|------|--------|-----------|---------|------|
| H1 | Hermes 框架安装 + 模板语法验证 | P1 | 0.5 周 | 无 | ✅ |
| H2 | SROS MCP 工具挂载 + 功能测试 | P1 | 1 周 | SROS S2 | ✅ |
| H3 | ARC MCP 工具挂载 + Data-Wiki 查询测试 | P1 | 1 周 | ARC A3 | ✅ |
| H4 | SXMU_MDD 流水线 dry-run 全流程 | P1 | 1 周 | H1+H2+H3 | ✅ |
| H5 | Pipeline 2 (dTMS 106例) 端到端生产运行 | P1 | — | H4 + SROS S1+S2 + ARC A1+A2 | ❌ |
| H6 | DeepSeek Prompt 硬化 — 模板 model 切换 + prompt_validator + validate-prompts 命令 | P1 | 0.5w | — | ✅ |

---

## 风险

| 风险 | 缓解 |
|------|------|
| Hermes 框架 API 可能变更 | 模板 YAML 与 Hermes 版本绑定，记录兼容版本号 |
| 长周期运行状态丢失 | Agent `state.persist: true` + 关键中间产物写入 DuckDB/文件系统 |
| MCP Gateway 在 Hermes 运行时不可用 | 工作流前置条件检查 MCP 健康状态，失败自动重试 |
