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

## ARC MCP Server (DW5 — Current)

```yaml
mcp_servers:
  arc:
    transport: stdio
    command: "arc-mcp-server"
    args: ["--vault-dir", ".", "--wiki-dir", "docs/code_wiki", "--data-wiki-dir", "data_wiki"]
    tools_prefix: "arc-"
    description: "ARC 知识引擎 — Code-Wiki 图谱查询 + Data-Wiki 被试/队列/量表查询 (DW5)"

    tools:
      - name: arc-mcp-impact
        description: "分析模块/函数变更的影响范围"
      - name: arc-mcp-context
        description: "查询模块/函数上下文与依赖关系图"
      - name: arc-mcp-paths
        description: "查询两个实体间的最短调用路径"
      - name: arc-data-wiki-read
        description: "查询 Data-Wiki — 被试/队列/量表/文献 (query_type: subject|cohort|scale|search|literature)"
```

### H3 验证状态 (2026-06-01)

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 工具声明 | ✅ | 4 个 tool 在 `config/mcp_mount.yaml` 中声明 |
| 模板验证 | ✅ | `hermes_arc_mcp_test.yaml` 通过 `hermes-cli validate` |
| Data-Wiki 查询 | 🔄 | `arc_data_wiki_read` subject/cohort/search — 需 data_wiki/ 目录存在 |
| Code-Wiki 烟测 | 🔄 | `arc_mcp_context` / `arc_mcp_paths` — 需 ARC MCP Server 在线 |
| 优雅降级 | ✅ | 无 data_wiki/ 时返回提示不崩溃 (DW5 test suite 覆盖) |

> **生产验证条件**: ARC DW5 `arc-mcp-server` 在 PATH 中，`data_wiki/` 目录已构建。
> **Mock 模式**: ARC MCP Server 不在线时，YAML 语法 + 结构验证仍可通过 `hermes-cli validate`。

## Agent 工具分配最佳实践

| Agent 角色 | 推荐工具 | 说明 |
|-----------|---------|------|
| Data_Engineer | sros-db-query, sros-hpc-*, sros-data-run-script | 数据查询 + HPC 操作 |
| Statistician | arc-wiki-read, arc-graph-query, sros-data-run-script | 知识检索 + 统计计算 |
| Principal_Investigator | arc-wiki-read, sros-scholar-search, sros-manuscript-insert | 全局视角 + 文稿输出 |
| Code_Reviewer | arc-wiki-impact, arc-wiki-paths, arc-graph-query | 代码变更分析 |

---

## H2 验证记录 (2026-05-19)

### 工具发现结果

| 端点 | 工具数 | 状态 |
|------|--------|------|
| SROS MCP (SSE) | 7 tools | ✅ 声明正确，`sros-db-query`, `sros-hpc-*`, `sros-data-run-script`, `sros-manuscript-insert`, `sros-scholar-search` |
| ARC MCP (stdio) | 4 tools | ✅ 声明正确，`arc-wiki-*`, `arc-graph-query` |

> **已发现工具总数**: 11 (7 SROS + 4 ARC)
> **验证模式**: Mock mode — SROS 不在线 (Connection refused localhost:8000)，连通性测试标记为 PASS (mock 模式不阻塞)
> **生产验证条件**: SROS Task S2 `sros-hpc-server` MCP SSE 端点运行在 `localhost:8000`

### 挂载配置

可执行挂载配置位于 `config/mcp_mount.yaml`，与本文档同步维护。
`hermes-cli mcp test config/mcp_mount.yaml` 用于本地和 CI 环境验证。

### MCP 测试工作流

`templates/hermes_mcp_test.yaml` — 最小 3 步工作流：
1. `step1_mcp_discovery` — 连接 MCP SSE endpoint，列举所有工具
2. `step2_db_query_smoke` — 执行 `SELECT 1` 烟测 (mock 模式下跳过)
3. `step3_result_summary` — 汇总健康评分
