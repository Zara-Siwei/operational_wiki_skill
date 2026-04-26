# Operational Wiki Schema

本文件定义 operational wiki 的页面类型、关系写法与证据格式。所有 workflow 必须遵守。

## 语言设置

每个知识库在 `init` 时设置 `KB_LANG`：
- `zh`: 页面主体用中文；保留英文专有名词、包名、函数名
- `en`: Write pages in English while keeping proper nouns and API names unchanged

规则：
- 新页面统一按 `KB_LANG` 撰写
- 文件名始终使用小写英文加连字符
- `title` 和 `aliases` 跟随知识库语言，但 `api_path`、`module_path` 保留原样

## 页面类型

只维护少量稳定类型：

```yaml
type: source | concept | tool | api | analysis | overview | conventions
```

### 类型说明

- `source`: 原始资料的摘要页；教材、论文、长 Markdown、单页大 HTML、文档站目录都落在这里
- `concept`: 稳定概念页；定义、公式、适用条件、证据、与工具/API的联系
- `tool`: 工具或模块页；包、模块、子系统
- `api`: 高价值函数、类、方法页；只为重要 API 建页
- `analysis`: 跨来源综合分析

## Frontmatter

每个页面必须包含：

```yaml
---
title: Page Title
aliases: [别名1, 别名2]
type: source | concept | tool | api | analysis | overview | conventions
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
sources: [source-page-id]          # source 页面可省略
---
```

按类型补充：

### `source`

```yaml
source_kind: textbook | paper | api_docs | tutorial | reference_manual | notes
raw_path: raw/相对路径
```

### `tool`

```yaml
tool_kind: package | module | workflow
module_path: plasmapy.formulary     # 可选
```

### `api`

```yaml
api_kind: function | class | method
api_path: plasmapy.formulary.lengths.Debye_length
```

## 文件命名

- `sources/`: 与素材根名一致，如 `introduction-to-plasma-physics.md`
- `concepts/`: 用稳定概念名，如 `debye-shielding.md`
- `tools/`: 用包或模块名规范化后命名，如 `plasmapy-formulary.md`
- `apis/`: 用"概念化 API 名"，如 `debye-length.md`
- 文件名尽量控制在 60 字符以内

## 页面结构

### `source` 页

```markdown
# 标题

## Source Profile
- 原始路径
- source_kind
- 语言
- 规模/分段情况

## Scope
[这个资料主要覆盖什么]

## Key Sections
- 段落或章节摘要

## Key Takeaways
- 要点

## Evidence Targets
- 这个 source 支撑了哪些 concept/tool/api 页

## Related
- documents: [[page]]
```

### `concept` 页

```markdown
# 概念名

## Definition

## Key Equations

## Assumptions / Validity

## In Sources

## In Tools

## Evidence
- 命题文本 | source=[[source-page]] | locator=章节/标题/路径

## Related
- explained_by: [[source-page]]
- implemented_by: [[api-page]]
- see_also: [[other-page]]
```

### `tool` 页

```markdown
# 工具或模块名

## What It Covers

## Core Concepts

## Important APIs

## Usage Notes

## Evidence

## Related
- documents: [[source-page]]
- exposes: [[api-page]]
- uses: [[concept-page]]
```

### `api` 页

```markdown
# API 名

## Signature

## Purpose

## Parameters

## Returns

## Physical Meaning

## Evidence

## Related
- documented_in: [[tool-page]]
- implements: [[concept-page]]
- see_also: [[api-page]]
```

## Related 区块写法

`## Related` 中每行必须使用 typed relation：

```markdown
- relation: [[target-page]] — 可选说明
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

不要使用无类型的"相关页面"列表。

## Evidence 区块写法

`## Evidence` 中每行必须能追溯：

```markdown
- 命题文本 | source=[[source-page]] | locator=章节/路径/标题
```

可选增加：

```markdown
- 命题文本 | source=[[source-page]] | locator=... | confidence=high
```

规则：
- 证据写"命题"，不是整段摘抄
- `source` 指向 `source` 页，不直接指向 raw 文件
- `locator` 尽量细到章节、标题、函数路径、HTML 标题或锚点

## 索引格式

`wiki/index.md` 必须包含：

```markdown
## Sources
## Concepts
## Tools
## APIs
## Analyses
```

每页一行，格式：

```markdown
- [标题](concepts/page.md) — 一句话摘要
```

## 矛盾处理

当两个资料源说法冲突时：
1. 保留两边说法
2. 在相关页正文中显式标注 `> ⚠️ 矛盾：...`
3. 在 `Evidence` 中分别给出来源和定位
4. 如冲突影响核心定义，在 `analysis` 页单独比较
