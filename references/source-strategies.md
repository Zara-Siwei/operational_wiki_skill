# Source Strategies

在收录前先判断 raw 素材形态，再选择读取策略。目标是"读得完、读得稳、能回溯"。

## 1. 素材形态分类

### A. 普通单文件

适用：
- `*.md`
- `*.txt`
- `*.pdf`
- `*.html`

策略：
- 文件较小则直接读
- 先创建一个 `source` 页，再决定是否拆 concept/tool/api

### B. 大文件

任一条件满足即视为大文件：
- 超过 200 KB
- 超过 4000 行
- 超过 120000 字符

策略：
1. 运行 `python <skill-dir>/scripts/segment_source.py <raw-file>`
2. 先读 segment 清单，不直接通读全文
3. 按主题挑关键 segment 继续读
4. 在 `source` 页记录这是"分段整理"

### C. 文档站目录

适用：
- Sphinx/Docs 目录
- 离线站点快照
- API 文档 bundle

策略：
1. 先看根目录文件结构
2. 若只有一个超大 `index.html`，按"大文件"处理
3. 若有多页 HTML，则先抽取目录/索引页，再选高价值页面
4. 默认仅创建一个 `source` 页，记录文档覆盖范围和模块索引
5. 精华信息（公式、参数约束）通过 `Evidence` 吸收到已有 `concept` 页
6. 除非用户明确要求，不创建 `tool` 页或 `api` 页

## 2. 文档源类型建议

### `textbook`

优先提取：
- 稳定概念
- 关键公式
- 适用条件
- 经典定义

常见落点：
- `source`
- `concept`
- `analysis`

### `paper`

优先提取：
- 论点
- 方法
- 数据/结论
- 与现有概念的补充或矛盾

常见落点：
- `source`
- 少量 `concept`
- `analysis`

### `api_docs`

函数库文档的价值在于其中包含的精确公式定义、参数约束、使用边界——这些与教材中的概念知识属于同一层级，应吸收到 concept 页而非孤立在 api 页中。

优先提取：
- 包/模块结构（方便定位）
- 每个概念对应的公式与参数范围
- 参数单位与边界条件
- 与教材定义一致或矛盾之处

常见落点：
- `source`（必建）
- `concept` → `Evidence` + `Key Equations` / `Assumptions / Validity`（精华吸收）
- `tool`（仅当被反复引用时，可建一个轻量总览页）
- `api`（仅用户明确要求，日常不建）

## 3. 分段读取原则

- 不需要把每段都读完
- 先用 segment 清单识别主题分布
- 只深读与当前目标有关的段落
- 长文整理允许分多轮完成，不要求一次 ingest 抽干净

## 4. 中文整理规则

当 `KB_LANG=zh`：
- source 页、concept 页、tool/api 页主体用中文写
- 包名、模块名、函数名保留英文原文
- 页面标题可中文化，但 `api_path`、`module_path` 保留英文
- 概念页中首次出现 API 时写成 `PlasmaPy 的 \`Debye_length\`` 这种形式

## 5. 控制混乱的规则

- `api` 页仅当用户明确要求时才建；日常流程不默认生成 api 页
- 新资料若只是为已有概念补证据，优先更新旧页，不新建页
- 如果一个 source 预计新建页面超过 8 个，先缩成"source + 3-5 个核心页"
- 对工具文档，默认建 source 页即可，不拆 tool/api 页
