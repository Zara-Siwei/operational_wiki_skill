# Operational Wiki

Evidence-first operational wiki for mixed research knowledge bases.

维护一个“轻结构、强可读、可操作”的知识库：把教材、论文、长 Markdown、HTML 文档站快照和 API 文档统一收录成可回溯的 `source` 页、`concept` 页及证据链。日常收录以 `source + concept` 为主，`tool` / `api` 页只在确有价值或用户明确要求时补充。

## 文件结构

```text
operational-wiki/
├── SKILL.md
├── SCHEMA.md
├── registries.json              # 公开模板，安装后改成本机知识库路径
├── agents/
│   └── openai.yaml
├── references/
│   └── source-strategies.md
├── scripts/
│   ├── router.py
│   ├── lint.py
│   ├── search.py
│   ├── graph.py
│   ├── stats.py
│   ├── segment_source.py
│   └── requirements.txt
└── workflows/
    ├── init.md
    ├── ingest.md
    ├── query.md
    ├── lint.md
    └── test.md
```

## 安装

1. 安装依赖：

```bash
pip install -r scripts/requirements.txt
```

2. 将整个 `operational-wiki` 文件夹放入 Cherry Studio 的 `Data/Skills/` 目录。

3. 编辑 `registries.json`，把 `YOUR_KB_PATH_HERE` 改成你的知识库根目录，并设置知识库名称、语言和默认库。

## 命令

```text
/opwiki init
/opwiki ingest [文件或目录]
/opwiki query <问题>
/opwiki search <关键词>
/opwiki graph [概念名]
/opwiki lint
/opwiki test
/opwiki help
```

自然语言也可以触发同样的路由，例如“收录这本教材”“整理 raw 里的文档站”“搜索 wiki 里的概念”“画关系图谱”“检查 wiki 健康状态”。

## 核心机制

- `router.py`：将命令或自然语言意图映射到具体 workflow，并返回当前知识库路径。
- `segment_source.py`：对大 Markdown / HTML / 文档站快照分段抽纲，避免一次性读取超长文件。
- `search.py`：全文搜索 wiki 页面，支持类型过滤和 JSON 输出。
- `graph.py`：从 `## Related` 的 typed relations 生成 Mermaid 关系图谱。
- `stats.py`：统计 source / concept / tool / api / analysis、raw 文件、concept maturity 和 evidence 覆盖情况。
- `lint.py`：确定性健康检查，覆盖断链、frontmatter、索引一致性、typed relation、Evidence、raw 指纹、maturity 和 overview 统计。

## 页面类型

| 类型 | 说明 |
|------|------|
| `source` | 原始资料摘要页：教材、论文、HTML、文档站目录、API docs |
| `concept` | 稳定概念页：定义、公式、适用条件、证据、工具映射 |
| `tool` | 工具、包、模块或工作流总览页 |
| `api` | 高价值函数、类、方法页；默认不主动创建 |
| `analysis` | 跨来源综合分析 |
| `overview` | 知识库总览 |
| `conventions` | 当前知识库操作偏好 |

## 默认收录策略

- 先创建或更新 `source` 页，再把精华信息吸收到已有 `concept` 页。
- 教材、综述、论文优先沉淀为稳定概念和证据。
- API 文档默认按“文献模式”处理：保留 source 页，将公式定义、参数约束、适用边界补到 concept 页。
- 大文件或单页大 HTML 先运行 `segment_source.py` 分段，再挑关键 chunk 深读。
- 批量收录时默认保守：先建 source 页骨架，再从最高价值的 3-5 个 source 提取概念和 evidence。

## Evidence

```markdown
## Evidence
- Debye shielding causes exponential screening beyond the Debye length. | source=[[introduction-to-plasma-physics]] | locator=Ch1.3
```

规则：

- Evidence 写成可验证的命题，不复制大段原文。
- `source` 指向 wiki 里的 `source` 页。
- `locator` 尽量精确到章节、标题、函数路径、HTML 标题或锚点。

## Typed Relations

`## Related` 中每行必须使用 typed relation：

```markdown
## Related
- explained_by: [[introduction-to-plasma-physics]]
- implemented_by: [[debye-length]]
- see_also: [[magnetic-reconnection]]
```

允许的 relation：

- `documents`
- `explained_by`
- `implements`
- `implemented_by`
- `documented_in`
- `exposes`
- `uses`
- `depends_on`
- `compares_with`
- `see_also`
- `evidence_for`

## 自检

```bash
python scripts/router.py help
python scripts/router.py ingest
python scripts/lint.py --wiki-dir <KB_ROOT>/wiki --raw-dir <KB_ROOT>/raw --json
python scripts/search.py --wiki-dir <KB_ROOT>/wiki "test" --json
python scripts/graph.py --wiki-dir <KB_ROOT>/wiki
python scripts/stats.py --wiki-dir <KB_ROOT>/wiki --raw-dir <KB_ROOT>/raw --json
```

## 致谢

本技能基于 [ChavesLiu/second-brain-skill](https://github.com/ChavesLiu/second-brain-skill) 的思路改良，重点强化了 research wiki 的 source/concept 分层、证据回溯、typed relations、大文件分段、健康检查和多知识库注册。
