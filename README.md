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
├── templates/             # 通用可复用模板
│   ├── eda_pipeline.yaml
│   ├── ml_experiment.yaml
│   ├── lit_review.yaml
│   └── multi_cohort_mega.yaml
├── projects/              # 具体项目实例
│   └── sxmu_mdd_digital_twin.yaml
└── docs/
    └── mcp_mount_spec.md  # MCP 工具挂载规范
```

## 快速开始

```bash
# 1. 克隆
git clone git@github.com:AutoBrainLab/Hermes-Workflows.git
cd Hermes-Workflows

# 2. 验证模板语法 (需要 Hermes 已安装)
hermes validate templates/eda_pipeline.yaml

# 3. 试运行
hermes run --dry-run projects/sxmu_mdd_digital_twin.yaml

# 4. 正式运行
hermes run projects/sxmu_mdd_digital_twin.yaml
```

## 设计原则

- **一个 Agent 只做一类事**（单一职责）
- **耗时步骤必须有 timeout_hours**
- **关键决策节点加入 feedback 回退环**
- **长周期项目的 Agent state.persist 设为 true**
- **不在 Hermes 中耦合 SROS/ARC 源码**（仅通过 MCP 协议消费工具）
