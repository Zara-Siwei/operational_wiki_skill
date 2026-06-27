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

## 4. 测试新增脚本

```text
python <skill-dir>/scripts/search.py --wiki-dir <kb>/wiki "test" --json
python <skill-dir>/scripts/graph.py --wiki-dir <kb>/wiki --focus "plasma"
python <skill-dir>/scripts/stats.py --wiki-dir <kb>/wiki --raw-dir <kb>/raw --json
```

检查：
- search.py 返回合法 JSON，含 file/title/type/score/matches
- graph.py 输出合法 Mermaid 图
- stats.py 返回正确计数，含 maturity 和 orphan 统计

## 5. 测试典型场景

至少走通两个场景：
- 教材/论文 source -> concept
- API docs source -> tool/api -> concept bridge

## 6. 测试新 lint 检查项

验证 lint.py 的扩展检查：
- `check_source_freshness`：raw_hash 缺失和过期检测
- `check_concept_maturity`：maturity 字段和建议
- `check_overview_stats`：统计同步

## 7. 汇总

输出通过项与剩余风险。
