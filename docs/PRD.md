# Hermes-Workflows PRD — 声明式多智能体科研流水线模板库

> 版本：V1.0 | 日期：2026-06-15
> 定位：SROS × ARC × Hermes 三系统协同的 L3 编排层 — 功能规格文档
> 入口文档：`README.md` (概述 + 快速开始)

---

## 1. 产品定位

Hermes-Workflows 是 Hermes 框架的工作流模板库，定义多 Agent 角色、任务编排和状态管理，驱动长周期无人值守科研流水线。

### 1.1 架构依赖

```
Hermes (L3 编排大脑)
  ├── 挂载 SROS MCP Tools (L1): 数据查询 / HPC 提交 / 文稿管理
  └── 挂载 ARC MCP Tools (L2): Data-Wiki 检索 / 图谱查询 / 交叉校验
```

### 1.2 核心约束

- **不耦合进 SROS 核心**：Hermes 是独立的 MCP 消费者，不能被 SROS 源码 import
- **不做系统开发**：Hermes 的第一使命是编排科学流水线，不得在任何阶段拥有 SROS/ARC 仓库写权限
- **YAML 模板版本绑定**：每个模板标注兼容的 SROS/ARC 版本

---

## 2. 目录结构

```
Hermes-Workflows/
├── README.md                    # 概述 + 快速开始
├── docs/
│   ├── PRD.md                   # 本文件 — 功能规格
│   └── mcp_mount_spec.md        # MCP 工具挂载规范
├── pyproject.toml               # hermes-cli 安装配置
├── hermes_cli/                  # CLI 验证工具
│   ├── cli.py                   # 入口: validate / run / mcp
│   └── validator.py             # YAML schema 校验
├── config/
│   └── mcp_mount.yaml           # MCP mount 可执行配置
├── templates/                   # 通用可复用模板
│   ├── eda_pipeline.yaml
│   ├── ml_experiment.yaml
│   ├── hermes_mcp_test.yaml     # SROS MCP 连通性验证
│   ├── hermes_arc_mcp_test.yaml # ARC MCP 连通性验证
│   ├── lit_review.yaml
│   └── multi_cohort_mega.yaml
└── projects/                    # 具体项目实例
    └── sxmu_mdd_digital_twin.yaml
```

---

## 3. 模板规范

### 3.1 必填字段

每个 YAML 模板必须包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 模板名称 |
| `version` | string | 模板版本 (semver) |
| `compatible_sros_version` | string | 兼容的 SROS 版本 |
| `compatible_arc_version` | string | 兼容的 ARC 版本 |
| `steps` | list[Step] | 编排步骤列表 |

### 3.2 Step 规范

每个 Step 必须包含：

| 字段 | 类型 | 说明 |
|------|------|------|
| `tool` | string | MCP tool name (如 `sros_db_query`) |
| `params` | dict | 工具参数 |
| `expected_output` | dict | 期望输出 schema |
| `timeout_hours` | float | 超时时间 (耗时步骤必填) |
| `on_failure` | enum | `retry` / `skip` / `abort` / `feedback` |
| `feedback_to` | string | (可选) 失败时回退到的上游 step |

### 3.3 Prompt 风格 (DeepSeek v4 Pro 适配)

所有模板的 `system_prompt` 必须使用**结构化指令格式**：

```yaml
system_prompt: |
  Role: <functional role description>
  Input: <expected input schema>
  Steps:
  1. <step 1>
  2. <step 2>
  Output format: strict JSON, no markdown wrapping.
  Constraints:
  - <constraint 1>
  - <constraint 2>
```

禁止使用 Claude 角色扮演风格（"你是一位..."、"请深呼吸"、"一步步思考"）。

---

## 4. MCP 集成

### 4.1 已挂载工具

| 来源 | 工具数 | 验证状态 | 说明 |
|------|:------:|:------:|------|
| SROS MCP Gateway | 7 | ✅ H2 | SSE transport (`localhost:8000/sse`) |
| ARC MCP Server | 4 | ✅ H3 | stdio transport |

> 工具总数: 11。挂载规范见 `docs/mcp_mount_spec.md`。

### 4.2 新增 MCP 工具的流程

1. 在上游仓库 (SROS/ARC) 实现 MCP tool
2. 更新 `contracts/mcp/` 契约快照
3. 在 Hermes 侧创建对应的 `hermes_<source>_mcp_test.yaml` 验证模板
4. 运行 `hermes-cli mcp test` 验证连通性

---

## 5. 框架兼容性矩阵

| 组件 | 版本 | 说明 |
|------|------|------|
| Hermes CLI | v0.3.0 | `validate` / `run --dry-run` / `mcp test` / `mcp list-tools` |
| 模板 Schema | v1.0 | agent/workflow YAML 结构约定 |
| Python | ≥3.10 | CLI 运行环境 |
| SROS MCP | v4.0 (SSE) | 7 tools 声明验证通过 |
| ARC MCP | DW5 (stdio) | 4 tools 声明验证通过 |

---

## 6. 设计原则

- **一个 Agent 只做一类事** (单一职责)
- **耗时步骤必须有 timeout_hours**
- **关键决策节点加入 feedback 回退环**
- **长周期项目的 Agent state.persist 设为 true**
- **不在 Hermes 中耦合 SROS/ARC 源码** (仅通过 MCP 协议消费工具)
- **Prompt 契约优先**：system_prompt 使用 DeepSeek 硬化格式 (Role/Input/Steps/Output/Constraints)

---

## 7. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-06-15 | 从 README.md 分离正式 PRD；新增 Prompt 风格规范；MCP 集成矩阵 |
