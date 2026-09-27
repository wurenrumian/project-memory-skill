# 命名与元数据约定

## 时间戳

| 用途 | 格式 | 示例 |
|---|---|---|
| journal 文件名 | `YYYY-MM-DD.md` | `2026-09-27.md` |
| 文档 front-matter 日期 | `YYYY-MM-DD` | `2026-09-27` |
| 行内时间 | `HH:MM` | `15:30` |

用本地时间。（`outputs/` 内部的命名由程序决定，不在此约定内。）

## outputs/ 落点（无内部约定）

程序产物**只写** `outputs/` 固定根，**内部结构不设约定**——分组、命名、放什么文件，全由产生它的程序决定。

skill 只要求一件事：**在实验 `README.md` 或当天 `journal/` 记一行产物位置**，这样以后找得到、也知道对应哪个实验。别回头去维护 `outputs/` 内部。

**不写进 `experiments/`。**

## 实验 ID

- 格式 `EXP-0001`，**四位零填充，单调递增，永不复用**（即使实验被删/归档）。
- 目录名 `EXP-0001-<slug>`，slug 为小写 kebab-case、≤5 个词、能望文生义，例如 `EXP-0007-gpu-latency-baseline`。
- 新建时扫描 `experiments/` 取当前最大编号 +1；同时检查 `archive/`，避免复用编号。

## 文件命名

- 文档用英文 kebab-case：`storage-latency-model.md`。
- 标题可以中文，文件名保持可跨平台稳定。

## annotated 主题

`annotated/` 收"需要着重讲解 / 强调的代码"。**形态不限**，按内容挑最省事的一种：

- `annotated/<topic-slug>.md` — 纯讲解，代码用代码块嵌在文档里
- `annotated/<topic-slug>.<ext>` — 带注释的源码片段，注释本身就是讲解
- `annotated/<topic-slug>/` — 主题目录：讲解与代码各一份，或再加几个变体 / diff

- 命名用 kebab-case 的主题词，例如 `annotated/zero-copy-path.md`。
- **唯一硬要求**：凡是从项目源码摘来的代码，都要记来源（原文件路径 + commit / 日期）——放文件顶部注释或同目录 README。否则会悄悄和真实源码漂移。
- 摘来的代码是副本不是真源，改动请回项目源码。

## show 主题

```
show/<topic-slug>/
├── README.md      # 给谁看、什么时候、怎么看（可选但推荐）
└── <成品>          # slides / 图 / demo 脚本 / 一页纸 / html
```

- 用途：面向**展示/讲解给他人**的成品（组会、评审、答辩、demo），不一定进版本库。
- 与 `docs/` 区别：`docs/` 是给项目读者自己读的**参考**；`show/` 是为某个展示**场合**做的成品。
- 与 `annotated/` 区别：`annotated/` 是**围绕某段代码**展开的讲解（讲解 md 或带注释源码均可）；`show/` 是面向展示场合的成品，重心在"讲给人听"。
- 展示完：其中稳定的结论走正常"毕业"到 `docs/`；`show/` 本身当素材留着或归档。

## 各类文件的结构

结构的价值在于**扫一眼就知道去哪找**。以下是推荐小节，字段名不是硬性的，但顺序和存在的小节尽量保持。

`STATE.md`（覆盖式更新，<150 行）：

```
# STATE
## 现在          # 一句话：当前在解决什么
## 进行中        # - EXP-0001 slug：进度一句话
## 下一步        # - 具体到可执行
## 待决 / 阻塞
## 关键链接      # - docs/... / experiments/.../README.md
## 已毕业        # - <./tmp 路径> → <./docs 路径>（日期）
```

实验 `README.md`：`状态` → `问题` → `假设` → `方法` → `结果` → `结论` → `未决` → `运行记录`（表格，每行指向 `outputs/` 里的实际产物位置）。
初期只填到「方法」，跑完再补结论——先开张。

`docs/` 文档：
- `memory`：背景 → 决定 → 理由与代价 → 来源
- `research`：一句话 → 正文 → 证据 → 未决
- `plan`：目标 → 方案 → 备选 / 取舍 → 验证方式

## docs/ 的门槛

`docs/` 与 `scratch/` 的区别不是"沉淀程度"，而是**你想不想留**：

| | 想留吗 | 组织方式 | 时间性 |
|---|---|---|---|
| `scratch/` | 不想（丢了不心疼） | 无 | 当下草稿 |
| `journal/` | 想留（作为**记录**） | 无，按时间 | 强——"哪天发生的" |
| `docs/` | 想留（作为**知识**） | 有，按主题 | 弱——与时间脱钩 |

进 `docs/` 要同时满足两点：

1. **时间脱钩**——不知道当时上下文也读得懂，不是流水账。
2. **有人会来查**——未来的某个决定 / 实验会回头指向它。

成熟度用 `status: draft → stable` 表达，**不必等到完全定论**。拿不准就先留 `journal/`；写 `docs/` 是主动的"升级"动作，有成本，因此自然稀缺。

## 文档 front-matter

所有 `docs/**/*.md` 必带：

```yaml
---
title: 标题
type: memory | research | plan
status: draft | stable | deprecated
created: 2026-09-27
updated: 2026-09-27
tags: []
related: [EXP-0001]
---
```

- `status` 从 `draft` 起步，内容稳定后改 `stable`，过时改 `deprecated`（不直接删）。
- `related` 用实验 ID 或相对路径，串起"哪些实验产生了这篇结论"。

## journal 条目

```markdown
- 15:30 做了什么 / 观察到什么 / 为什么
```

- 一行一条，不要求完整句子，不要求排版。
- 一个文件对应一天；跨天就新建文件。只追加，不回头整理。

## 产物元数据（可选）

`outputs/` 内部不设约定，产物要不要自带来源由程序决定。如果你希望产物能自证出处，可以让程序自己写一份，下面是**可参考、非必须**的字段：

```json
{
  "experiment": "EXP-0001",
  "command": "python scripts/run.py --config config.yaml",
  "started_at": "2026-09-27T15:30:12+08:00",
  "duration_s": 123.4,
  "git": { "rev": "abc1234", "dirty": true },
  "inputs": ["config.yaml"],
  "artifacts": [{ "path": "metrics.csv", "bytes": 2048 }],
  "status": "ok"
}
```

- 有它，从产物反查实验最省事；没有也能用，靠实验 / journal 里的位置记录。
- `status` 建议记 `ok | failed | interrupted`——失败 / 中断的产物同样值得留。

## 链接与引用

- 文档之间用相对路径链接，保证在编辑器/渲染器里可点。
- 结论指向证据：`docs/` 里引用 `outputs/` 中的实际路径，而不是复制粘贴数字。
