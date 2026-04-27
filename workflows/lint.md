# Lint Workflow

对 operational wiki 做结构检查和语义审计。

## 1. 运行确定性脚本

首先运行：

```text
python <skill-dir>/scripts/lint.py --wiki-dir <KB_WIKI> --raw-dir <KB_RAW> --json
```

脚本覆盖：
- 断链
- `[[raw/...]]` 误用
- 指向 `raw/` 的不规范相对 Markdown 链接
- 非受管目录中的 Markdown 文件
- frontmatter 缺失
- `source/tool/api` 元数据缺失
- `index.md` 与实际页面不一致
- `Related` 关系未 typed
- `Evidence` 缺少 `source` 或 `locator`

## 2. LLM 补充检查

重点补以下语义问题：
- 页面语言是否符合 `KB_LANG`
- `concept` 与 `tool/api` 是否缺少明显桥接
- 是否存在"应该更新旧页却新建了重复页"
- API 页是否过多、过碎
- 是否有 `source` 页没有被 concept/tool/api 消化
- 是否有重要概念缺 `Evidence`

## 3. 输出报告

```markdown
## Operational Wiki 健康检查报告 (YYYY-MM-DD)

### 统计
- Sources: N
- Concepts: N
- Tools: N
- APIs: N
- Analyses: N

### P0
- 需要立即修复的问题

### P1
- 结构改进与证据补全建议

### P2
- 可选优化
```

## 4. 修复策略

- P0：直接修复或先告知用户
- P1：通常逐项确认
- P2：只给建议，不强行改
