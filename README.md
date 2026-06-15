# Hermes-Workflows — 声明式多智能体科研流水线模板库

> SROS × ARC × Hermes 三系统协同的 L3 编排层

## 定位

本仓库是 Hermes 框架的工作流模板库，定义多 Agent 角色、任务编排和状态管理，驱动长周期无人值守科研流水线。

## 架构依赖

```
Hermes (L3 编排大脑)
  ├── 挂载 SROS MCP Tools (L1): 数据查询 / HPC 提交 / 文稿管理
  └── 挂载 ARC MCP Tools (L2): Data-Wiki 检索 / 图谱查询 / 交叉校验
```

## 目录结构

```
Hermes-Workflows/
├── README.md
├── pyproject.toml              # hermes-cli 安装配置
├── hermes_cli/                 # CLI 验证工具 (H1)
│   ├── cli.py
│   └── validator.py
├── config/
│   └── mcp_mount.yaml          # MCP mount 可执行配置
├── templates/                  # 通用可复用模板
│   ├── eda_pipeline.yaml
│   ├── ml_experiment.yaml
│   ├── hermes_mcp_test.yaml        # SROS MCP 连通性验证 (H2)
│   ├── hermes_arc_mcp_test.yaml    # ARC MCP 连通性验证 (H3)
│   ├── lit_review.yaml
│   └── multi_cohort_mega.yaml
├── projects/                   # 具体项目实例
│   └── sxmu_mdd_digital_twin.yaml
└── docs/
    └── mcp_mount_spec.md       # MCP 工具挂载规范
```

## 框架兼容性

| 组件 | 版本 | 说明 |
|------|------|------|
| **Hermes CLI** (`hermes-cli`) | v0.3.0 | 本仓库内置 CLI，提供 `validate` / `run --dry-run` / `mcp test` / `mcp list-tools` |
| 模板 Schema | v1.0 | agent/workflow YAML 结构约定 |
| Python | ≥3.10 | CLI 运行环境 |
| SROS MCP | v4.0 (SSE) | 7 tools 声明验证通过 (H2 ✅, mock 模式) |
| ARC MCP | DW5 (stdio) | 4 tools 声明验证通过 (H3 ✅, mock 模式) |

> `hermes-cli` 是本模板库的本地验证工具，与 PyPI 上的 `hermes` (HELMHOLTZ metadata) 是完全不同的项目。
> 生产运行需 Hermes 编排引擎 (L3)，`hermes-cli` 覆盖本地开发和 CI 阶段的模板校验。

## 快速开始

```bash
# 1. 克隆
git clone git@github.com:AutoBrainLab/Hermes-Workflows.git
cd Hermes-Workflows

# 2. 安装验证工具
pip install -e .

# 3. 验证模板语法
hermes-cli validate templates/eda_pipeline.yaml

# 4. 试运行 (dry-run)
hermes-cli run --dry-run projects/sxmu_mdd_digital_twin.yaml

# 5. MCP 工具发现测试
hermes-cli mcp list-tools config/mcp_mount.yaml
hermes-cli mcp test config/mcp_mount.yaml

# 6. 正式运行 (需 Hermes 编排引擎)
# hermes run projects/sxmu_mdd_digital_twin.yaml
```

## MCP 验证状态 (ROADMAP H1–H3)

| Task | 交付物 | 验证模式 | 工具数 | 状态 |
|------|--------|---------|--------|------|
| **H1** | `hermes-cli` v0.3.0 | 本地 CLI | — | ✅ |
| **H2** | `hermes_mcp_test.yaml` | SROS MCP mock | 7 SROS tools | ✅ |
| **H3** | `hermes_arc_mcp_test.yaml` | ARC MCP mock | 4 ARC tools | ✅ |
| **H4** | SXMU_MDD full dry-run | 跨系统端到端 | SROS + ARC 全部 | ❌ 待 ARC DW5 生产验证 |

> MCP 工具总数: **11** (7 SROS + 4 ARC)，全部通过 `hermes-cli mcp list-tools` 发现验证。
> 生产运行需 SROS MCP Gateway (`localhost:8000/sse`) + ARC MCP Server (`arc-mcp-server`) 同时在线。

## 设计原则

- **一个 Agent 只做一类事**（单一职责）
- **耗时步骤必须有 timeout_hours**
- **关键决策节点加入 feedback 回退环**
- **长周期项目的 Agent state.persist 设为 true**
- **不在 Hermes 中耦合 SROS/ARC 源码**（仅通过 MCP 协议消费工具）
