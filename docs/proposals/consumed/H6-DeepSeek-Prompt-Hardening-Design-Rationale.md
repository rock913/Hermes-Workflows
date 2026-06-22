# H6: DeepSeek v4 Pro Prompt Hardening — Design Rationale

> 本文档从 Meta 层策略文档下沉编译而来。下沉日期：2026-06-21。
>
> 来源：`meta-docs/strategy/upgrade-notes/0615-DeepSeek v4 Pro 架构适配与非对称成本优势指南.md`

## 1. 背景

主控模型选型确立为 DeepSeek v4 Pro。该选型带来了两个关键工程影响：(1) 极低的 API 成本使得高重试次数的自动化修复循环（Loop Engineering）在经济上可行；(2) Prompt 工程范式需要从 Anthropic Claude 的"角色扮演 + 温和引导"风格，转变为更适合 DeepSeek 推理特性的"硬核指令 + 结构化契约"风格。

本文档聚焦于第 (2) 点——Prompt 硬化（Prompt Hardening）——的设计依据与工程决策。

## 2. DeepSeek v4 Pro 的推理特性对 Prompt 设计的影响

### 2.1 训练数据分布与响应模式

DeepSeek v4 Pro 的训练语料库中，代码和数学逻辑占据极高比重。其推理能力在以下场景表现最优：

- **结构化输入/输出**：明确的 JSON Schema、函数签名、pytest 报错堆栈
- **逻辑约束密集型任务**：给定清晰的约束条件集，模型在多步推理中保持一致性
- **测试驱动的修复循环**：给定一个失败的测试用例和一段源代码，模型能够高效地定位并修复问题

相对而言，DeepSeek 在开放式闲聊、模糊情感需求、需要大量上下文推断的场景中表现不如 Claude 系列。

### 2.2 Prompt 风格的范式转换

| 维度 | Claude 风格（弃用） | DeepSeek 风格（采用） |
|------|---------------------|-----------------------|
| 语调 | 角色扮演、温和引导、使用感叹号和鼓励性语言 | 直接、紧凑、无冗余修饰 |
| 指令形式 | 自然语言段落描述 | 伪代码或结构化指令优先 |
| 边界定义 | 通过自然语言"请勿..."描述 | 通过明确的 JSON Schema 和禁止列表定义 |
| 上下文组织 | 故事化、场景化 preamble | 分层级：输入 Schema → 约束条件 → 输出 Schema |

### 2.3 Prompt Hardening 的核心原则

基于上述分析，Hermes Workflows 中的 Prompt 模板应遵循以下硬化原则：

**原则 1：输入输出 Schema 前置**

每个 Prompt 模板必须首先声明：
- 输入数据的 JSON Schema（字段名、类型、允许值域）
- 输出数据的 JSON Schema（字段名、类型、必填/可选）
- 错误契约（何时返回何种错误码）

**原则 2：指令原子化**

将复杂指令拆解为编号步骤，每步一个单一动作。避免在单一段落中混合多个逻辑分支。

**原则 3：禁止列表显式化**

不使用"请尽量避免 X"的软约束，改用 `DO NOT:` 开头的硬禁止列表，每行一个禁止项。

**原则 4：去除角色扮演前缀**

移除所有 "You are an expert...", "Take a deep breath...", "Think step by step..." 等 Anthropic 风格的引导前缀。DeepSeek 不需要这些元指令来激活推理能力——清晰的逻辑约束本身就是最强的激活信号。

**原则 5：利用 pytest 堆栈作为 Prompt 输入**

在 TDD 循环中，直接将 pytest 失败输出（未经人类总结）作为 Prompt 的一部分传递给模型。DeepSeek 对原始堆栈跟踪的解析能力很强，人工总结反而可能丢失关键信息。

## 3. Loop Engineering 与 Prompt 设计的关系

### 3.1 成本结构决定 Prompt 策略

DeepSeek v4 Pro 的 API 成本约为顶级 Anthropic 模型的 1/5 到 1/10。这一成本差异直接改变了自动化修复循环的经济可行性：

- **高重试次数不再昂贵**：在隔离的 worktree 中，允许模型自我排查、盲试修复高达 20 次迭代，直到 pytest 绿灯。
- **Prompt 可以更"硬"**：因为可以承受更多的试错轮次，Prompt 不需要过度设计来追求"一次就对的完美指令"。可以采用更紧凑、更直接的指令风格，依靠迭代收敛。

### 3.2 从"预设路径"到"验收标准"

与 Claude 的交互模式通常需要人类架构师预设修复路径（"先检查 X，再修改 Y"）。DeepSeek 的低成本使得另一种模式可行：

- **只给验收标准（pytest test cases），不给 SOP**
- 模型在多次迭代中自行探索修复路径
- 人类架构师只需定义"什么是正确"（test），不需要定义"怎么变正确"（procedure）

这一转变对 Prompt 设计的影响是：Prompt 中需更强调**验收契约**（expected output schema, error contracts），而非**操作步骤**。

## 4. Hermes Workflows 中的具体适配

### 4.1 system_prompt / AI_RULES.md 的硬化

Hermes 在向 DeepSeek 发射任务时使用的系统提示词（无论是通过 MCP Gateway 还是 Aider 桥接），应遵循以下硬化标准：

```markdown
# 输入契约
- 你将收到一个 JSON 对象，包含以下字段：...
- 字段 X 的取值范围：...

# 输出契约
- 你必须返回一个 JSON 对象，包含以下字段：...
- 如果无法完成任务，返回 {"error": "ERR_<CODE>", "detail": "..."}

# 行为边界
- DO NOT: 修改未在 tasks.files_to_modify 中列出的文件
- DO NOT: 执行任何 shell 命令
- DO NOT: 添加解释性注释，除非 tasks.require_comments 为 true

# 验收标准
- 修改完成后，以下 pytest 测试必须全部通过：...
```

### 4.2 YAML 工作流模板中的 Prompt 片段

Hermes 的 YAML 工作流模板中嵌入的 Prompt 片段也应硬化：

- 移除所有感叹号、表情符号、鼓励性语句
- 用 `REQUIRED:` / `FORBIDDEN:` 标签替代自然语言软约束
- 在每个 Prompt 片段末尾附上该步骤的验收标准（对应的 test case 名称）

### 4.3 与 Aider 的集成

当 Hermes 通过 `delegate_to_aider.sh` 调用 Aider + DeepSeek 时：

- 生成的 `.aider_task.md` 文件已经自然符合硬 Prompt 风格（结构化 sections: Context / Files to Modify / Contract / Do NOT）
- 无需额外的 Prompt 软化层——Aider 的 task 文件格式本身就是 Prompt Hardening 的最佳实践实例

## 5. 总结

DeepSeek v4 Pro 的引入要求 Hermes Workflows 在 Prompt 工程层面进行一次系统性硬化：

1. **去除角色扮演**：移除 Anthropic 风格的引导前缀和鼓励性语言
2. **Schema 前置**：每个 Prompt 以输入/输出 JSON Schema 开头
3. **硬约束替代软约束**：用 `REQUIRED:` / `DO NOT:` 替代自然语言软约束
4. **验收标准驱动**：Prompt 中强调 test cases 和 error contracts，减少操作步骤描述
5. **利用成本优势**：接受更高迭代次数，换取更简洁的 Prompt 设计

这些调整不是对 DeepSeek 的"妥协"，而是对其推理特性的精确适配——去掉多余修饰，让逻辑约束和验收标准成为 Prompt 的唯一核心。

## 参考

- 原始策略文档：`meta-docs/strategy/upgrade-notes/0615-DeepSeek v4 Pro 架构适配与非对称成本优势指南.md`
- 对应的交付 Proposal：`docs/proposals/consumed/H6-DeepSeek-Prompt-Hardening-Proposal.md`
- Hermes Workflows 主 PRD：`docs/PRD.md`
