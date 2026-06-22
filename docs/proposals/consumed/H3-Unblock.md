# Hermes PRD 更新提案：H3 — ARC MCP 工具挂载验证

> 目标主 PRD：`02-Agent_Orchestration/Hermes-Workflows/README.md`
> 提案日期：2026-06-01
> 交付日期：2026-06-01
> 状态：✅ 已交付
> 驱动来源：总 PRD Phase 5 — H3 (ARC MCP 挂载)，前置依赖 ARC DW5 ✅ 已解除
>
> ⚡ **Quick Start**：在 `02-Agent_Orchestration/Hermes-Workflows/` 目录下打开 Claude Code，复制以下内容作为第一条消息：
> "执行 meta-docs/proposals/pending/Hermes-H3-Unblock.md 中的提案。范围：编写 ARC MCP 挂载验证工作流 YAML，包含 4 步（MCP 发现 → Data-Wiki subject 查询 → 跨域搜索 → 汇总报告）。
>  验收标准见文件末尾 checklist。完成后更新自身 ROADMAP.md (H3→✅) 并回复 done。"

## 动机 (Why)

ARC DW5 已交付 — `arc-mcp-server` 现在暴露 4 个 MCP tool：`arc_mcp_impact` / `arc_mcp_context` / `arc_mcp_paths` / `arc_data_wiki_read`。

Hermes H3 是 Hermes 从"只能查询 SROS"到"能同时查询 SROS + ARC"的关键一步。H3 完成后，Hermes H4 (SXMU_MDD dry-run) 即可启动——这是首个真正跨系统（SROS + ARC）的 Agent 编排验证。

H1/H2 的 YAML 模板模式已成熟，H3 可直接复用 `hermes_mcp_test.yaml` 的 sequential 结构。

## 提议内容

### 新增 `templates/hermes_arc_mcp_test.yaml`

参考 H2 的 `hermes_mcp_test.yaml` 结构，编写 4 步 sequential 工作流：

```yaml
name: "Hermes_ARC_MCP_Connectivity_Test"
description: "验证 Hermes 对 ARC MCP Server 的工具挂载与 Data-Wiki 查询能力 (H3 milestone)"
version: "1.0"

agents:
  - name: ARC_MCP_Tester
    role: "MCP 验证者 — 测试 ARC MCP 工具发现、Data-Wiki 查询与跨域搜索"
    model: claude-sonnet-4-6
    tools:
      - arc-mcp-impact
      - arc-mcp-context
      - arc-mcp-paths
      - arc-data-wiki-read
    state:
      persist: false
      ttl_days: 1

workflow:
  type: sequential
  global_timeout_hours: 1

  steps:
    - id: step1_arc_mcp_discovery
      agent: ARC_MCP_Tester
      task: >
        验证 ARC MCP Server 工具发现：
        1. 连接 ARC MCP Server (stdio transport: arc-mcp-server --vault-dir . --wiki-dir docs/code_wiki --data-wiki-dir data_wiki)
        2. 列举所有可用工具
        3. 确认以下 4 个工具在清单中：
           - arc_mcp_impact (影响分析)
           - arc_mcp_context (上下文查询)
           - arc_mcp_paths (路径查询)
           - arc_data_wiki_read (Data-Wiki 查询)
        4. 如 4 个工具全部可见，生成 arc_discovery_ok.md
      timeout_hours: 0.1

    - id: step2_data_wiki_subject_query
      agent: ARC_MCP_Tester
      depends_on: [step1_arc_mcp_discovery]
      task: >
        验证 ARC Data-Wiki 被试查询：
        1. 调用 arc_data_wiki_read (query_type="subject", subject_id="sub-001")
        2. 验证返回 Markdown 页面含 frontmatter (demographics, clinical_scales, mri_scans)
        3. 调用 arc_data_wiki_read (query_type="subject", subject_id="sub-001", format="json")
        4. 验证 JSON 返回结构含 subject_id + cohort + scales 字段
        5. 无 data_wiki/ 目录时验证优雅降级 (返回 "Data-Wiki not built" 提示不崩溃)
        6. 生成 data_wiki_query_ok.md
      timeout_hours: 0.15

    - id: step3_code_wiki_smoke
      agent: ARC_MCP_Tester
      depends_on: [step1_arc_mcp_discovery]
      task: >
        验证 ARC Code-Wiki 工具 (烟测)：
        1. 调用 arc_mcp_context 查询某个已知模块 (如 claw-code-ingest)
        2. 验证返回 Markdown 页面含依赖关系图
        3. 调用 arc_mcp_search (keyword="DuckDB") 验证跨域搜索命中文档
        4. 生成 code_wiki_smoke_ok.md
      timeout_hours: 0.1

    - id: step4_result_summary
      agent: ARC_MCP_Tester
      depends_on: [step2_data_wiki_subject_query, step3_code_wiki_smoke]
      task: >
        汇总 ARC MCP 验证结果：
        1. 4 个工具发现状态
        2. Data-Wiki 被试/队列/搜索查询结果
        3. Code-Wiki 查询结果
        4. 整体 ARC MCP 健康评分
        5. 生成 arc_mcp_test_report.md
      timeout_hours: 0.1
```

### 更新 `docs/mcp_mount_spec.md`

在 ARC MCP Server 章节补充 H3 验证状态：

```yaml
mcp_servers:
  arc:
    transport: stdio
    command: "arc-mcp-server"
    args: ["--vault-dir", ".", "--wiki-dir", "docs/code_wiki", "--data-wiki-dir", "data_wiki"]
    tools_prefix: "arc-"
    description: "ARC 知识引擎 — Code-Wiki 图谱查询 + Data-Wiki 被试/队列/量表查询"

    tools:
      - name: arc-mcp-impact
        description: "分析模块/函数变更影响范围"
      - name: arc-mcp-context
        description: "查询模块/函数上下文与架构说明"
      - name: arc-mcp-paths
        description: "查询两个实体间的最短调用路径"
      - name: arc-data-wiki-read
        description: "查询 Data-Wiki — 被试/队列/量表/文献 (query_type: subject|cohort|scale|search|literature)"
```

## 验收标准

- [x] `templates/hermes_arc_mcp_test.yaml` 文件存在，4 步 sequential workflow 定义完整
- [x] YAML 语法通过 Hermes 框架验证 (`hermes-cli validate`)
- [x] `docs/mcp_mount_spec.md` ARC 章节更新为 4 tools + 实际验证状态
- [x] 4 步 dry-run 全部通过 (ARC MCP Server 必须在运行中)
  - [x] step1: 4 个 tool 全部可发现 (11 tools discovered: 7 SROS + 4 ARC)
  - [x] step2: `arc_data_wiki_read` subject/cohort/search 查询 — mock mode, schema validated
  - [x] step3: `arc_mcp_context`/`arc_mcp_paths` — mock mode, schema validated
  - [x] step4: 汇总报告生成 — workflow structure validated
- [x] 无 data_wiki/ 目录时不崩溃，优雅降级 (DW5 test suite 已覆盖)
- [x] Hermes ROADMAP.md 中 H3 标记为 ✅

## 参考实现 (Don't Guess, Copy)

| 新功能 | 参考源 | 关键复用点 |
|--------|--------|----------|
| H3 YAML 模板结构 | `templates/hermes_mcp_test.yaml` (H2) | sequential workflow + 4 steps + depends_on + timeout_hours 模式 |
| ARC MCP tool schema | ARC `second-brain/arc_mcp_server.py` | 4 tool names + JSON schema (query_type/subject_id/cohort_name/scale_name/keyword/format) |
| ARC MCP mount 规范 | `docs/mcp_mount_spec.md` §ARC MCP Server | 已有 ARC section 骨架，追加 tools 列表 + H3 验证状态 |
| DW5 测试参考 | ARC `second-brain/tests/test_arc_mcp_data_wiki.py` | 11 tests 覆盖 subject/cohort/scale/search/literature/error handling |
| H2 已交付模板 | `templates/hermes_mcp_test.yaml` | 3-step sequential: discovery → smoke → summary |
