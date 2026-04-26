# Init Workflow

初始化一个新的 operational wiki，并注册到 `registries.json`。

## 1. 收集信息

需要：
- 知识库路径
- 知识库名称
- 语言：`zh` 或 `en`

## 2. 创建目录

在 `KB_ROOT` 下创建：

```text
KB_ROOT/
├── raw/
│   └── assets/
└── wiki/
    ├── sources/
    ├── concepts/
    ├── tools/
    ├── apis/
    └── analyses/
```

## 3. 初始化核心文件

### `wiki/index.md`

```markdown
# Operational Wiki Index

## Overview
- [Overview](overview.md) — Wiki 总览
- [使用约定](conventions.md) — 当前知识库的操作偏好

## Sources

## Concepts

## Tools

## APIs

## Analyses
```

### `wiki/log.md`

```markdown
# Operational Wiki Log
```

### `wiki/overview.md`

```markdown
---
title: Overview
aliases: [总览]
type: overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [overview]
---

# 知识库总览

## 统计

| 指标 | 数量 |
|------|------|
| 原始素材 | 0 |
| Sources | 0 |
| Concepts | 0 |
| Tools | 0 |
| APIs | 0 |
| Analyses | 0 |

## Scope

_待补充_

## Recent Activity

- [YYYY-MM-DD] 初始化 knowledge base
```

### `wiki/conventions.md`

```markdown
---
title: 使用约定
aliases: [约定]
type: conventions
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [meta]
---

# 使用约定

## Query

（暂无）

## Ingest

（暂无）

## Lint

（暂无）

## 通用

（暂无）
```

## 4. 更新 `registries.json`

写入：

```json
{
  "default": "<kb-id>",
  "registries": {
    "<kb-id>": {
      "name": "知识库名称",
      "path": "KB_ROOT",
      "language": "zh",
      "created": "YYYY-MM-DD"
    }
  }
}
```

## 5. 输出

```text
✅ 已初始化 operational wiki: <知识库名称>
   路径: KB_ROOT
   语言: zh
   已创建: raw/, wiki/, sources/, concepts/, tools/, apis/, analyses/
```
