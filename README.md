# Operational Wiki

**Evidence-first operational wiki for mixed research knowledge bases.**

维护一个"轻结构、强可读、可操作"的知识库——把教材、论文、长 Markdown、API 文档快照统一收录成可回溯的概念页、工具页和证据链。

---

## 文件结构

```
operational-wiki/
├── SKILL.md                      ← 技能定义（Skill 文件）
├── SCHEMA.md                     ← 页面类型、Frontmatter、Evidence、Related 规范
├── registries.json               ← ⚠️ 模板文件，首次使用需复制并填写路径
├── scripts/
│   ├── router.py                 ← 子命令路由（init/ingest/query/lint/test/help）
│   ├── lint.py                   ← 确定性健康检查（P0/P1/P2）
│   ├── segment_source.py         ← 大文件/大 HTML 分段工具
│   └── requirements.txt          ← 依赖：PyYAML>=6.0
├── workflows/
│   ├── init.md                   ← 创建新知识库
│   ├── ingest.md                 ← 收录素材
│   ├── query.md                  ← 查询与桥接
│   ├── lint.md                   ← 健康检查
│   └── test.md                   ← 技能自检
├── references/
│   └── source-strategies.md       ← 素材形态判断与读取策略
└── agents/
    └── openai.yaml               ← Agent interface 配置
```

---

## 首次安装

### 1. 安装依赖

```bash
pip install PyYAML
```

### 2. 填写 registries.json

```bash
cd operational-wiki
copy registries.json registries.json.bak   # 备份模板
# 用编辑器打开 registries.json，修改：
#   - "path": "YOUR_KB_PATH_HERE" → 填入你的知识库根路径（如 D:\my-wiki）
#   - "name": "我的知识库" → 填入知识库名称
#   - "language": "zh" 或 "en"
#   - "created": "YYYY-MM-DD"
```

### 3. 在 CherryStudio 中安装技能

1. 将整个 `operational-wiki` 文件夹复制到 `cherrystudio\Data\Skills\` 下
2. 在 CherryStudio 界面中搜索并安装 `operational-wiki` 技能
3. 或让 agent 执行：将文件夹路径传给 `mcp__skills__skills` 的 `register` action

---

## 初始化知识库

### 方式一：命令式

```
/opwiki init
```

### 方式二：手动创建目录结构

```text
KB_ROOT/
├── raw/
│   └── assets/
└── wiki/
    ├── index.md
    ├── overview.md
    ├── log.md
    ├── conventions.md
    ├── sources/
    ├── concepts/
    ├── tools/
    ├── apis/
    └── analyses/
```

初始化完成后，手动编辑 `registries.json` 中的 `default` 和 `registries` 字段填入知识库信息。

---

## 命令参考

| 命令 | 说明 |
|------|------|
| `/opwiki init` | 初始化新知识库 |
| `/opwiki ingest [文件]` | 收录素材（不指定则收录 raw/ 下全部新文件） |
| `/opwiki query <问题>` | 基于知识库回答问题 |
| `/opwiki lint` | 知识库健康检查 |
| `/opwiki test` | 技能自检 |
| `/opwiki help` | 显示帮助 |

---

## 页面类型

| 类型 | 说明 |
|------|------|
| `source` | 原始素材摘要页（教材、论文、文档快照） |
| `concept` | 稳定概念：定义、公式、适用条件、证据 |
| `tool` | 工具/包/模块总览页 |
| `api` | 高价值函数、类、方法页 |
| `analysis` | 跨来源综合分析 |
| `overview` | 知识库总览（自动生成） |
| `conventions` | 操作偏好与约定 |

---

## Typed Relations

所有 `## Related` 必须使用 typed relation：

- `documents` / `explained_by` / `implements` / `implemented_by`
- `documented_in` / `exposes` / `uses` / `depends_on`
- `compares_with` / `see_also` / `evidence_for`

示例：
```markdown
## Related
- explained_by: [[introduction-to-plasma-physics]]
- implemented_by: [[debye-length]]
- see_also: [[magnetic-reconnection]]
```

---

## Evidence 格式

```markdown
## Evidence
- Debye shielding causes exponential screening beyond λ_D. | source=[[introduction-to-plasma-physics]] | locator=Ch1.3
```

规则：
- 写"命题"，不抄原文
- `source` 指向 `source` 页，不直接指向 raw 文件
- `locator` 精确到章节、标题、函数路径或 HTML 锚点

---

## Lint 检查级别

| 级别 | 含义 | 处理方式 |
|------|------|----------|
| P0 | 断链、缺 frontmatter、索引不一致 | 必须修复 |
| P1 | Typed relation 格式、Evidence 格式 | 建议修复 |
| P2 | 语义问题、重复页 | 视情况优化 |


---

## 致谢

本技能基于 [ChavesLiu/second-brain-skill](https://github.com/ChavesLiu/second-brain-skill) 改良而来。在原版基础上，针对个人知识库的实际使用场景做了以下扩展：

- **结构化分层**：引入 `source / concept / tool / api / analysis` 五类页面类型，明确每类页面的角色与边界
- **Typed Relations**：所有跨页关系强制使用带类型的关系标签（`explained_by`、`implemented_by` 等），提升知识图谱可用性
- **证据追溯**：引入 `Evidence` 区块，要求每条证据包含 `source` + `locator`，确保可回溯到原始资料
- **大文件分段读取**：新增 `segment_source.py`，支持对超大 Markdown / HTML 文件按标题分段抽纲，避免一次性塞入上下文
- **lint 健康检查**：新增 P0/P1/P2 三级审计，覆盖断链、frontmatter、索引一致性、关系格式、证据格式等维度
- **约定管理**：引入 `conventions.md`，记录用户在查询/收录/lint 时的偏好设置
- **多知识库支持**：`registries.json` 支持多库注册 + default 指定

