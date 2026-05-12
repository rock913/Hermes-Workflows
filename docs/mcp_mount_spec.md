# Hermes MCP 工具挂载规范

## SROS MCP Gateway

```yaml
mcp_servers:
  sros:
    transport: sse
    url: "http://localhost:8000/sse"
    tools_prefix: "sros-"
    description: "SROS 科研操作系统 — 数据查询、HPC 提交、文稿管理"

    tools:
      - name: sros-db-query
        description: "对 DuckDB 异构图谱执行结构化 SQL 查询"
      - name: sros-hpc-submit
        description: "向交我算 Pi 2.0 提交 Slurm 批处理作业"
      - name: sros-hpc-status
        description: "查询 Slurm 作业状态 (squeue)"
      - name: sros-hpc-cancel
        description: "取消 Slurm 作业 (scancel)"
      - name: sros-data-run-script
        description: "在 HPC 上执行数据分析 Python 脚本"
      - name: sros-manuscript-insert
        description: "向文稿中插入章节/段落"
      - name: sros-scholar-search
        description: "跨数据库文献搜索"
```

## ARC MCP Server

```yaml
mcp_servers:
  arc:
    transport: stdio
    command: "arc-mcp-server"
    args: ["--wiki-dir", "docs/code_wiki"]
    tools_prefix: "arc-"
    description: "ARC 知识引擎 — Code-Wiki 查询、图谱搜索、交叉校验"

    tools:
      - name: arc-wiki-read
        description: "读取 Data-Wiki / Code-Wiki 页面内容"
      - name: arc-graph-query
        description: "跨项目图谱语义搜索"
      - name: arc-wiki-impact
        description: "分析代码变更的影响范围"
      - name: arc-wiki-paths
        description: "查找实体间的引用路径"
```

## Agent 工具分配最佳实践

| Agent 角色 | 推荐工具 | 说明 |
|-----------|---------|------|
| Data_Engineer | sros-db-query, sros-hpc-*, sros-data-run-script | 数据查询 + HPC 操作 |
| Statistician | arc-wiki-read, arc-graph-query, sros-data-run-script | 知识检索 + 统计计算 |
| Principal_Investigator | arc-wiki-read, sros-scholar-search, sros-manuscript-insert | 全局视角 + 文稿输出 |
| Code_Reviewer | arc-wiki-impact, arc-wiki-paths, arc-graph-query | 代码变更分析 |
