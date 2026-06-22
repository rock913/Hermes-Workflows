# Hermes-Workflows Architecture — Module Topology

> 地方解剖图：工作流模板库与 MCP 消费者拓扑
> L3 编排层 — 独立 MCP Consumer，不耦合进 SROS/ARC 核心

## 架构

```
┌─────────────────────────────────────────────────┐
│  Layer 0: CLI Entry                              │
│  hermes-cli validate      — YAML schema 校验      │
│  hermes-cli validate-prompts — Prompt风格校验(H6) │
│  hermes-cli run --dry-run  — 工作流模拟执行        │
├─────────────────────────────────────────────────┤
│  Layer 1: Template Library                       │
│  templates/                                        │
│  ├── eda_pipeline.yaml     — EDA 通用模板         │
│  └── ml_experiment.yaml    — ML 实验模板          │
│  projects/                                         │
│  ├── sxmu_mdd_digital_twin.yaml — SXMU 5阶段流水线│
│  ├── hermes_mcp_test.yaml       — SROS MCP 验证   │
│  └── hermes_arc_mcp_test.yaml   — ARC MCP 验证    │
├─────────────────────────────────────────────────┤
│  Layer 2: MCP Consumer Contracts                 │
│  docs/mcp_mount_spec.md    — SROS + ARC 工具挂载  │
│  contracts/mcp/            — MCP tool schemas     │
├─────────────────────────────────────────────────┤
│  Layer 3: Prompt Engineering (H6)                │
│  System prompts: DeepSeek 硬化格式                │
│  Input/Output/Constraints 三要素必填              │
│  禁止 Claude 角色扮演风格                         │
└─────────────────────────────────────────────────┘
```

## Fan-out: Hermes → External MCP Tools

```
Hermes Workflow (YAML)
    ├── SROS MCP (7 tools, SSE transport)
    │   ├── sros-db-query
    │   ├── sros-hpc-submit
    │   ├── sros-hpc-status
    │   ├── sros-data-run-script
    │   ├── sros-manuscript-*
    │   └── sros-scholar-*
    └── ARC MCP (4 tools, stdio transport)
        ├── arc_mcp_impact
        ├── arc_mcp_context
        ├── arc_mcp_paths
        └── arc_data_wiki_read
```

## Key Constraints

- **Red Line**: Hermes 不得拥有 SROS/ARC 仓库写权限
- **Scope**: 编排科学流水线 (YAML templates)，不编写系统源代码
- **Version Binding**: 模板 YAML 与 Hermes 版本绑定，记录兼容版本号
- **No Coupling**: 不 `import sros` / `import arc_engine`
