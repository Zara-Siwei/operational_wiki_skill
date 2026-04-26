# Test Workflow

验证 operational wiki skill 的基本可用性。

## 1. 测试路由

运行：

```text
python <skill-dir>/scripts/router.py help
python <skill-dir>/scripts/router.py init
python <skill-dir>/scripts/router.py ingest
python <skill-dir>/scripts/router.py query "test"
python <skill-dir>/scripts/router.py lint
```

检查：
- JSON 合法
- `subcommand` 正确
- 有知识库时能返回 `kb`

## 2. 测试分段脚本

对一个大 Markdown 或 HTML 运行：

```text
python <skill-dir>/scripts/segment_source.py <large-file>
```

检查：
- 能输出 chunk 清单
- chunk 标题和预览合理
- 不需要把全文塞进上下文

## 3. 测试 lint 脚本

```text
python <skill-dir>/scripts/lint.py --wiki-dir <kb>/wiki --raw-dir <kb>/raw --json
```

检查：
- JSON 合法
- 能发现 frontmatter / typed relation / evidence 格式问题

## 4. 测试典型场景

至少走通两个场景：
- 教材/论文 source -> concept
- API docs source -> tool/api -> concept bridge

## 5. 汇总

输出通过项与剩余风险。
