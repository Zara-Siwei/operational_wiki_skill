---
name: operational-wiki
description: |
  Evidence-first operational wiki for textbooks, papers, large Markdown/HTML files, and software documentation snapshots. Use when Codex needs to ingest or query a mixed research knowledge base that should stay readable while becoming slightly more structured: stable concept pages, tool/api pages, typed relations, explicit evidence, and traceable raw sources. Trigger for requests like "收录资料", "整理文档站", "把教材和库文档联系起来", "查询知识库里某概念在工具里怎么落地", "检查 wiki 结构", or "把大文件分段整理成中文知识页".
---

# Operational Wiki

维护一个"轻结构、强可读、可操作"的知识库。支持命令式调用（`/opwiki <cmd>`）和自然语言触发。

## 自然语言路由

当 skill 被自然语言触发时，先判断意图再映射子命令：

| 用户意图 | 映射子命令 | 示例 |
|---------|-----------|------|
| 初始化知识库 | `init` | "创建一个新的 operational wiki" |
| 收录素材 | `ingest` | "收录这本教材""整理 raw 里的 PlasmaPy 文档" |
| 查询/桥接概念与工具 | `query` | "Debye length 在 PlasmaPy 里怎么实现？" |
| 检查结构 | `lint` | "检查这个 wiki 是否乱了" |
| 验证工作流 | `test` | "测试一下这个 skill 能否跑通" |
| 帮助 | `help` | "这个 skill 怎么用？" |

确定子命令后，将用户原始输入作为 `args`，进入下方步骤。

## 执行步骤

### 1. 运行路由脚本

运行 `python <skill-dir>/scripts/router.py <子命令> [参数]` 获取路由结果 JSON。

### 2. 根据路由结果执行

若 `status` 为 `ok`：
1. 若 `schema` 非空，先读取 `<skill-dir>/<schema>`
2. 若 `<kb.wiki>/conventions.md` 存在，读取它作为当前知识库的额外约束
3. 读取 `<skill-dir>/<workflow>`
4. 如需处理大文件、单页超长 HTML、文档站目录，再读取 `references/source-strategies.md`
5. 按工作流执行，`kb.root`、`kb.wiki`、`kb.raw`、`kb.lang` 即当前知识库路径和语言

若 `status` 为 `select`：
- 告知用户有多个知识库，并让用户选择一个继续

若 `status` 为 `no_kb` 或 `error`：
- 直接输出错误信息

## 关键约束

- 保持知识库可读，不把所有东西都拆成页面
- 优先维护 `concept`、`tool`、`api` 三类核心页面
- 所有跨页面联系都要能回溯到原始资料
- 默认按知识库语言整理；`zh` 知识库输出中文，但保留英文专有名词
- 面对大文件或大 HTML，不要硬读到底；优先分段、抽纲、逐段整合

## 帮助输出

当子命令为 `help` 时输出：

```text
Operational Wiki — 轻结构、可操作、可回溯的知识库技能

命令:
  /opwiki init
  /opwiki ingest [文件或目录]
  /opwiki query <问题>
  /opwiki lint
  /opwiki test
  /opwiki help

适用场景:
  - 教材 / 论文 / 长 Markdown
  - 文档站快照（单页 HTML 或目录）
  - 概念与工具/API 对齐
  - 中文整理与证据回溯
```
