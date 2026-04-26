# Ingest Workflow

收录新素材到 operational wiki。目标不是"抽尽所有节点"，而是建立稳定的概念页、工具/API 页和证据链。

## 核心原则

1. 先判断 source 形态，再决定读取策略
2. 优先更新已有页，其次才新建页
3. 教材/论文偏向 `concept`
4. 文档站/API 文档默认按"文献模式"处理（source 页 + 精华信息吸收到 concept 页），不默认建 tool/api 页
5. 大文件允许分段整理，不要求一次读完

## 1. 发现新素材

扫描 `KB_RAW`，找出未在 `wiki/sources/` 中登记的文件或目录。

如果用户指定路径，只处理该对象。

## 2. 识别 source 形态

将素材归类为：
- `textbook`
- `paper`
- `api_docs`
- `tutorial`
- `reference_manual`
- `notes`

然后判断：
- 普通单文件
- 大文件
- 文档站目录

必要时读取 `references/source-strategies.md`。

## 3. 对大文件或超大 HTML 先分段

若文件较大，不要硬读到底。先运行：

```text
python <skill-dir>/scripts/segment_source.py <path>
```

先根据输出的标题和预览决定哪些 chunk 值得深读。

对 `docs-plasmapy-org-en-stable/index.html` 这种单页大 HTML，同样先分段。

## 4. 规划落点

收录后只允许稳定落到以下页面：
- `source`
- `concept`
- `tool`
- `api`
- `analysis`

### 教材/论文

优先：
- 创建/更新一个 `source` 页
- 更新已有 `concept` 页
- 必要时新建 3-5 个核心 `concept`

### API 文档

优先（文献模式）：
- 创建/更新一个 `source` 页，记录文档覆盖范围、核心模块索引与定位方式
- 运行 `segment_source.py` 分段，按主题挑关键段阅读
- 将精华信息（公式定义、参数约束、使用边界）作为 `Evidence` 补充到已有 `concept` 页中
- **不默认创建 `tool` 页或 `api` 页**

以下情况可考虑加一个轻量 `tool` 总览页：
- 该库被反复引用
- 库覆盖多个模块，需要一个总览索引

`api` 页仅当用户明确要求时才建——日常流程不需要。

## 5. 何时询问用户

遇到以下情况再询问：
- 与已有知识明显冲突
- 可能和已有页重复但不能确定
- 预计新建页面超过 8 个

默认优先方案：
- 保守收录
- 先 source + 3-5 个核心页

## 6. 创建/更新页面

### `source` 页

必须包含：
- `source_kind`
- `raw_path`
- `Scope`
- `Key Takeaways`
- `Evidence Targets`
- typed `Related`

### `concept` 页

优先补这些区块：
- `Definition`
- `Key Equations`
- `Assumptions / Validity`
- `In Sources`
- `In Tools`
- `Evidence`

### `tool` 页

优先补这些区块：
- `What It Covers`
- `Core Concepts`
- `Important APIs`
- `Usage Notes`
- `Evidence`

### `api` 页（极少使用）

仅当用户明确要求时才建。日常流程中不默认生成 api 页。

优先补这些区块：
- `Signature`
- `Purpose`
- `Parameters`
- `Returns`
- `Physical Meaning`
- `Evidence`

## 7. 建立 typed 关系

`## Related` 必须写成：

```markdown
- relation: [[target-page]] — 可选说明
```

例如：

```markdown
- explained_by: [[introduction-to-plasma-physics]]
- implemented_by: [[debye-length]]
- documented_in: [[plasmapy-formulary]]
```

## 8. 写 Evidence

每条 evidence 必须可回溯：

```markdown
- Debye shielding causes exponential screening beyond the Debye length. | source=[[introduction-to-plasma-physics]] | locator=Ch1.3
```

不要把整段原文塞进页里；把它压缩成命题。

## 9. 更新索引和日志

更新：
- `wiki/index.md`
- `wiki/overview.md`
- `wiki/log.md`

`index.md` 必须覆盖 `Sources / Concepts / Tools / APIs / Analyses`

## 10. 运行检查

执行：

```text
python <skill-dir>/scripts/lint.py --wiki-dir <KB_WIKI> --raw-dir <KB_RAW>
```

如有 P0 问题，先修复再结束。

## 输出摘要

```text
✅ 收录完成《资料名》
   新建: sources/xx.md, concepts/yy.md, tools/zz.md
   更新: concepts/aa.md
   lint: 通过
```
