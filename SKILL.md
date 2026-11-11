---
name: project-memory
description: 在项目根的 ./tmp/ 下维护项目记忆、实验记录与当前状态（过程进 ./tmp/，结论进 ./docs/）。当用户要记录一下、记个结论、维护项目状态 / 当前进度 / 下一步、写研究记录或实验记录、整理探索笔记、整理 / 清理 tmp、按 tag 找文档、检查文档断链与孤儿、这些先别放进 docs，或提到 project memory、journal、experiment run、文档索引、多 agent 协作时使用。Maintain project memory, research notes, experiment records and current state under ./tmp/.
---

# Project Memory

在项目根的 `./tmp/` 下维护一份**过程性记忆**：项目记忆、研究讲解、脚本、实验记录、实验结果、当前状态与后续方向。

它**不是**项目文档，也**不是**随时可清的临时目录：`./docs/` 是给项目读者的结论，`./tmp/` 是产生这些结论的过程——失败的、没定论的、以及“当初为什么放弃”的记录都在这里。

## 核心规则

1. **过程进 `./tmp/`，结论进 `./docs/`。** 毕业时在 `STATE.md` 记一笔，说明从哪来、到哪去。
2. **实验定义与运行产物分开。** 定义在 `experiments/`（小、稳定、人读），产物在 `outputs/`（多、只增、程序写）。
3. **捕获便宜，沉淀才排版。** 日常只追加 `journal/` 一行；值得长期查阅才升级到 `docs/`（门槛见下）。
4. **产物不覆盖。** 每次运行写独立目录，`outputs/` 内部结构由程序决定。
5. **两个入口。** 看现状读 `./tmp/STATE.md`，找文档看 `./tmp/docs/index.md`；不必通读整个 `./tmp/`。
6. **移动是常态，删除是例外。** 退役内容进 `archive/`，`scratch/` 随时可删；不做批量删除，真删只限范围具体、依据清楚的可重建产物（如 `outputs/` 单个过期实验，在实验 `README.md`「运行记录」留一行）。
7. **初始化是惰性的。** 只读不建；第一次写入才落 `.gitignore`、`README.md`、`STATE.md`（有 Python 时加 `scripts/` 工具集），其余目录用到再建。
8. **多 agent 只动自己的地盘。** 并行才开 `agents/`：`BOARD.md` 认领即锁，进展写自己的子目录，收尾才写回全局。
9. **远程是原料。** 增量只进 `remote/`，再反向更新 `STATE.md` / `docs/` / 实验；`cursor.json` 与 `docs/index.md` 是仅有的两处覆盖写。

## 目录结构

`./tmp/` 是这份记忆的唯一根，**整个目录默认不进版本库**；顶层（除 `scratch/` 外）受“不可随意删”约定保护。目录**按需创建**：下面列的是「该放哪」，不是「启动时就要全建出来」。

```
./tmp/
├── README.md            # 这目录是什么、约定与入口指引（人读一次）
├── STATE.md             # 【必读】现在 / 进行中 / 下一步 / 待决 / 关键链接
├── .memory-cache.json   # 检查工具的增量缓存（可删，不参与检查）
├── journal/
│   └── 2026-09-27.md    # 追加式时间线，一天一个文件
├── remote/              # 远程仓库增量（同步过才有）
│   ├── cursor.json      # 水位；覆盖写（指针）
│   └── 2026-09-29.md    # 每次同步追加一节，只增不改
├── docs/                # 沉淀后的内容；演示材料等也放这，形式自由
│   ├── index.md         # 生成的全量索引 + 近期活跃；不手改
│   ├── memory/          # 决策、架构、约定、踩过的坑
│   ├── research/        # 研究讲解 / 分析长文 / 论文笔记
│   └── plans/           # 不动手验证的方案、路线图、想法（动手验证就开实验）
├── experiments/         # 实验的「定义与结论」——小、稳定、人读
│   ├── INDEX.md         # 生成的实验索引（状态 / 问题 / 结论）
│   └── EXP-0001-slug/
│       ├── README.md    # 问题/假设/方法/结果/结论/未决
│       ├── config.yaml  # 该实验固定参数
│       └── scripts/     # 实验专属脚本（可复用时才提升到顶层 scripts/）
├── outputs/             # 所有程序产物；内部结构自定
├── annotated/           # 需着重讲解 / 强调的代码
├── agents/              # 多 agent 协作：BOARD.md + 各 agent 子目录（并行才建）
├── scripts/             # 跨实验复用的工具（含 check-memory 工具集）
├── scratch/             # 真正的草稿，允许随时删
└── archive/             # 退役内容
    ├── INDEX.md         # 追加式归档索引（原路径 / 去向 / 原因）
    ├── journal/YYYY-MM/ # 滚动归档的旧日志
    ├── remote/YYYY-MM/  # 滚动归档的旧同步摘要
    ├── docs/            # 退役文档
    ├── annotated/       # 退役的阅读版（geeklens 的产物）
    └── EXP-XXXX-slug/   # 归档的实验
```

产物**不进 `experiments/`**：定义少而稳、产物多而只增，分开后大文件集中在一处，归档实验时不会漏带数据。产物位置只记**一处**——有归属实验的记进实验 `README.md`「运行记录」，没归属的记当天 `journal/`。

`assets/tmp-readme.md` 是这份目录表的落盘版（首次写入时原样复制）；改目录结构时两处一起改。

## 写入协议

默认**只追加 `journal/`**；值得长期查阅时才升级到 `docs/`（门槛见「`docs/` 的门槛」）。

| 生命周期 | 什么时候 | 写到哪 | 装什么 |
|---|---|---|---|
| 入口 | 会话收尾 | `STATE.md` | 现在 / 进行中 / 下一步 / 待决 / 关键链接；覆盖更新，<150 行 |
| 入口 | 首次写入 | `README.md` | 声明这是记忆、列目录与约定 |
| 只增 | 任意观察 / 想法 / 进展 | `journal/YYYY-MM-DD.md` | 一行一条，不排版 |
| 只增 | 同步远程增量 | `remote/YYYY-MM-DD.md` | 范围、合入与关闭的 PR、“对我方的影响” |
| 指针 | 每次同步收尾 | `remote/cursor.json` | 新水位；覆盖写，不做历史 |
| 只增 | 程序产生产物 | `outputs/` | 内部结构自定，不覆盖历史产物 |
| 只增 | 实验完成 / 文档与阅读版退役 | `archive/` | 移动不删；退役文档加「被 X 取代」链接 |
| 少而稳定 | 开新实验 | `experiments/EXP-XXXX-slug/` | 定义与结论；不装运行产物 |
| 少而稳定 | 工具第二次复用 | `scripts/` | 跨实验复用的工具，不放实验专属脚本 |
| 生成 | 实验开始 / 结论更新 / 整理后 | `experiments/INDEX.md` | ID / 状态 / 问题 / 结论 / 更新；`index-experiments.py` 生成 |
| 只增 | 每次归档 | `archive/INDEX.md` | 日期 / 原路径 / 归档到 / 原因或取代者 |
| 稳定后沉淀 | 决策 / 约定 / 架构 / 坑 | `docs/memory/` | 背景 → 决定 → 理由与代价 → 引用 |
| 稳定后沉淀 | 研究讲解 / 分析 / 论文笔记 | `docs/research/` | 一句话 → 正文 → 证据 → 未决 |
| 稳定后沉淀 | 不动手验证的方案 / 路线图 | `docs/plans/` | 目标 → 方案 → 备选与取舍 → 验证方式 |
| 稳定后沉淀 | 讲清某段代码 | `annotated/<slug>` | 围绕代码讲；摘来的代码记来源（路径 + commit/日期） |
| 生成 | 写完文档 / 整理后 | `docs/index.md` | 全量索引 + 近期活跃；`index-memory.py` 生成，不手改 |
| 并行协作 | 多个 agent 同时干活 | `agents/` | 任务在 `BOARD.md` 认领（认领即锁），进展写各自子目录 |
| 可丢 | 随手草稿 | `scratch/` | 唯一可任意删除的区域 |

两条容易混的分界：

- **`docs/` 文档 = H1 + 正文 + `tags` + 引用链接**；没有 status / title / date 字段，位置即状态。
- **`docs/` 与 `annotated/`**：前者是随时查的参考（演示、成品、讲稿也放这），后者围着代码讲实现。

## 冷启动协议

需要了解项目当前状态、或继续之前的工作时：

1. 读 `./tmp/STATE.md`。不存在说明还没有记忆，按空状态继续——**只读不初始化**。
2. 读最新一个 `./tmp/journal/*.md` 的尾部。
3. 看 `./tmp/remote/cursor.json`（存在才看）：与 `git log -1 --format=%h origin/main` 对不上、或 `synced_at` 已过一周，就**提示**用户同步——只提示，不自动 `fetch` / `gh`。
4. 按「关键链接」按需读文档；找实验状态读 `./tmp/experiments/INDEX.md`，找文档读 `./tmp/docs/index.md`，不扫目录。存在 `agents/` 时看一眼 `BOARD.md`。
5. 只在必要时深入 `outputs/`；怀疑文档过期时跑 `check-memory.py` 看孤儿与断链，不凭印象判断。

## 远程增量同步

**什么时候做**：用户 `pull` / `fetch` 之后，或用户说“同步一下远程”；冷启动只提示不执行。

**三步，顺序不能换**（命令、PR 分类、摘要模板与坑见 `references/remote-sync.md`）：

1. **算增量**：`git fetch --prune` 后取 git / PR 增量；没有 `gh` / 非 GitHub 就只做 git 侧，摘要头部标**降级**。
2. **写摘要** `remote/YYYY-MM-DD.md`：头部写清范围（sha 区间 + 时间区间），每次同步追加一节。
3. **推水位** `remote/cursor.json`：写临时文件再 rename，避免半截 JSON。

> **先写摘要、后推水位。** 反过来，中途失败会让那段增量永久丢失。

**然后反向更新本地记忆**：按摘要里的 `## 对我方的影响` 收过时待决、复核被改到的 `docs/`、更新实验「未决」；无关的别人进展留在 `remote/`。`journal/` 只记一行指针。

两条纪律：**远程的措辞不等于我们的结论**——进 `STATE.md` / `docs/` 必须用自己的话重写；**cursor 是每个 checkout 一份**——多 worktree / 多机器各同步各的，不冲突，但不自动对齐。

## 索引与检验

**为什么**：文档一多，靠目录和记忆找东西必然失效。生成式索引 + 检查脚本让“有哪些文档、哪些没人用、哪些链接断了”变成可查的数字。

**`docs/index.md`（生成，不手改）**：

- 「正在关注」：近 30 天有**文件活动**的 tag，按最近活跃排序，带文档数、最近日期、入链数——工作区最近在碰什么的启发式视图；
- 「全部文档」：按主 tag（第一个 tag）分组，每篇一行：wiki 链接 + 首段首句 + 入链数 + 最后更新。

> mtime 受复制、解压、checkout 影响，所以“正在关注”是启发式，不代表主题重要性或人工关注状态。

**`experiments/INDEX.md`（生成）**：从每个实验 README 的 `状态 / 问题 / 结论` 小节生成，一行一个；归档实验标 `archived`；由 `index-experiments.py` 维护。

**`archive/INDEX.md`（追加）**：每次归档追加一行——日期、原路径、归档到、原因 / 被谁取代。它是“当初为什么放弃”的检索入口，不做生成器。

**`scripts/` 工具集（Python 3 标准库；共享逻辑在 `memory_lib.py`）**：

```bash
python tmp/scripts/check-memory.py               # 结构 / 引用 / 主题 / 整理阈值
python tmp/scripts/check-memory.py --json        # 机器可读
python tmp/scripts/check-memory.py --limit 0     # 列表不截断（默认每类 40 条）
python tmp/scripts/find-memory.py --tag storage  # 按 tag 找路径（可重复，多个为 AND）
python tmp/scripts/find-memory.py --untagged     # 没有 tag 的文档
python tmp/scripts/find-memory.py --orphans      # 孤儿清单
python tmp/scripts/index-memory.py               # 生成 docs/index.md
python tmp/scripts/index-experiments.py          # 生成 experiments/INDEX.md
```

首行的 `toolset N` 是工具集版本，当前是 **toolset 1**；与 `assets/` 里 `memory_lib.py` 的 `TOOLSET_VERSION` 不一致，说明项目里的 `tmp/scripts/` 是旧副本，重新复制一次。

**增量缓存**：解析结果存在 `tmp/.memory-cache.json`，按 `mtime + size + 活目录归属` 命中，三个命令共享；可随时删，`--no-cache` 强制全量解析。缓存文件不参与检查。

报告分四类：**结构**（断链、裸 basename 歧义、`docs/` 重名，退出码 1）、**引用**（孤儿）、**主题**（无 tag 文档、tag 计数与 tag 规范）、**整理**（目录条目数、journal 活跃月份）。四条判定规则：

- 入链只算活引用（`docs/`、`experiments/`、`annotated/`、`STATE.md`）；`journal/`、`remote/`、`archive/`、`scratch/` 既不算入链，也不报断链——它们只追加、不回头整理，报出来也修不了；
- **孤儿** = 入链 0 且 mtime 超过 30 天的 `docs/` 文档，只是复核线索，不是“该删”的结论；
- `docs/index.md` 自身不参与检查（否则它列出的每条链接都会变成入链）；
- 链接按文件系统语义判定：Markdown 链接的 `#锚点` / `?query` 不算路径；指向目录的链接、大小写不一致的 wiki 链接（Windows / macOS）都算有效。

有 Obsidian 1.12+ CLI 的人可以用 `obsidian unresolved` / `orphans` / `backlinks` 人工复核；它需要 app 在运行，脚本是无头等价物。

## 整理与滚动归档

**触发是提示，不是自动**：收尾时跑 `check-memory.py`，「整理」小节会直接给出目录条目数与 journal 活跃月份（不用手动数），满足任一就提示用户“要不要整理一轮”：

- 任一可读目录（`docs/{memory,research,plans}/`、`experiments/`、`annotated/`、`scripts/`、`archive/` 子目录）条目数 ≥ 16（软）/ ≥ 20（硬）；
- `journal/` 活跃月份超过 2 个；
- 用户主动说“整理一下”。

`outputs/` 不适用目录长度规则。流程：

1. **滚动归档**：`journal/`、`remote/` 里结束超过 60 天的整月整体移到 `archive/journal/YYYY-MM/`、`archive/remote/YYYY-MM/`；只移动、不重写，`cursor.json` 留在原地。
2. **跑检查**：修断链；孤儿与无 tag 文档是候选清单，处理前由用户判断（合并 / 移 `archive/docs/`）；`docs/` 内重名先改名再改引用。
3. **归档完成实验**：状态 done 且「未决」已清空的 → `archive/EXP-XXXX-slug/`，并在 `archive/INDEX.md` 追加一行（日期 / 原路径 / 去向 / 原因或取代者）。
4. **重生成索引**：`index-memory.py` 与 `index-experiments.py`。
5. **记一笔**：当天 journal 一行，写清搬了哪些、退役了哪些、修了几条链接。

**淘汰是移动，不是删除**：合并 = 内容进新篇 + 旧篇留「被 X 取代」链接；退役 = 整篇移 `archive/docs/`，阅读版移 `archive/annotated/`。不重写正文、不替用户做合并决定、不动别人进行中的工作。

## 常用操作

| 任务 | 动作 |
|---|---|
| 收尾 | 更新 `STATE.md` 的「现在 / 进行中 / 下一步」，删掉过期的「关键链接」；索引化当天 `journal/` 结论；实验完成 → 补「结论」；遗留阻塞写进「待决」；顺手看整理阈值 |
| 开新实验 | 取下一个 `EXP-XXXX`（规则见「格式约定」）；建 `experiments/EXP-XXXX-slug/{README.md,config.yaml,scripts/}`（**不建产物目录**）；`README.md` 先填到「方法」；`STATE.md` 与当天 journal 各记一行（多 agent 时中途只记 BOARD 与自己那份） |
| 沉淀成文档 | 判类型 → `docs/{memory,research,plans}/`；按对应结构写；`STATE.md`「关键链接」挂上；相关实验「结论」同步；跑 `index-memory.py` |
| 毕业到项目 `./docs/` | 见 `references/migration.md`：先问用户 → 按项目格式**重写** → `STATE.md` 记一行 → 原件保留或移 `archive/docs/` |
| 检验 / 生成索引 | `check-memory.py` 检查（`--json` 可机读，`--limit` 控制列表长度）；`find-memory.py` 查 tag / 无 tag / 孤儿；`index-memory.py`、`index-experiments.py` 生成索引；语义见「索引与检验」 |
| 整理 | 见「整理与滚动归档」；只提示不自动 |
| 归档 | 实验 / 退役文档移入 `archive/`，并在 `archive/INDEX.md` 追加一行（日期 / 原路径 / 去向 / 原因或取代者） |
| 同步远程 | 见「远程增量同步」：摘要在前、水位在后，再做反向更新 |

## 多 agent 协作

多个 agent **同时**在同一个项目里干活才启用；单 agent 时 `agents/` 不存在，根 `STATE.md` 仍是全局入口。工作期间只写 BOARD 与自己子目录，收尾才写回全局。各 worktree 的 `./tmp/` 互不共享、**不会自动合并**——重要结论要在收尾时显式同步到共享位置，不能假设 BOARD 或本地 `STATE.md` 跨 worktree 可见。任务板格式与认领规则见 `references/multi-agent.md`。

## 格式约定

- **时间戳**：journal 文件名 `YYYY-MM-DD.md`；文档日期看 mtime（需要时正文写 `YYYY-MM-DD`）；行内时间 `HH:MM`。用本地时间。
- **链接**：文档间引用优先 wiki 形式 `[[从 tmp 根的路径]]`（免 `.md`，可带 `|别名` 与 `#标题`），Markdown 相对链接也接受；两种都由 `check-memory.py` 解析。结论指向 `outputs/` 里的实际路径，不复制粘贴数字。
- **basename 唯一（限于 `docs/`）**：`docs/` 内文件名不得重复；实验等按路径引用的文件可以重名。裸 basename 命中多份时检查工具报歧义。
- **实验 ID**：`EXP-0001`，四位零填充、单调递增、**永不复用**（含归档）。目录名 `EXP-0001-<slug>`，slug 小写 kebab-case、≤5 词。新建时扫 `experiments/` 与 `archive/` 取最大编号 +1。
- **文件命名**：文档用英文 kebab-case（`storage-latency-model.md`）；标题可以中文，文件名保持跨平台稳定。
- **`remote/`**：一天一份摘要，每次追加 `## HH:MM` 小节；头部必备**范围**、**抓取时间**、**是否降级**三行。

### 各类文件的结构

结构的价值是**扫一眼就知道去哪找**；字段名不硬性，但小节顺序尽量保持。

- `STATE.md`：`## 现在` → `## 进行中` → `## 下一步` → `## 待决 / 阻塞` → `## 关键链接` → `## 已毕业`（骨架见「惰性初始化」）。
- 实验 `README.md`：`状态` → `问题` → `假设` → `方法` → `结果` → `结论` → `未决` → `运行记录`（每行指向 `outputs/` 实际产物）。初期只填到「方法」，跑完再补结论。
- `annotated/<topic-slug>`：形态不限——`<slug>.md` 纯讲解、`<slug>.<ext>` 带注释的源码片段、`<slug>/` 主题目录（**默认单文件，多份文件才建目录**；geeklens 产出的阅读版走这一格）。**硬要求**：`tags` 写在 front-matter（第一个是主 tag，`find-memory.py --tag` 靠它找到），从项目源码摘来的代码记来源（路径 + commit/日期），放文件顶部或同目录 README。
- `docs/` 的演示类内容无独立形态要求——slides、一页纸、demo 脚本、html 成品放文档旁或同目录 `assets/` 即可。

### 文档 front-matter（极简）

只留一个字段，没有 tag 的文档**不写 front-matter**：

```yaml
---
tags: [storage, cache-eviction]
---
```

原来的 `type` / `status` / `title` / `created` / `related` 字段都不要了：分别看子目录、位置（`docs/` 活、`archive/docs/` 退役）、正文 H1、mtime / git、正文链接。

- **tag 只写 front-matter**，不用行内 `#tag`（代码块里会误报）；小写 kebab-case，一篇 1~3 个，第一个是**主 tag**。
- **优先复用已有 tag**，避免 `cache` / `caching` / `缓存` 这类同义变体。`check-memory.py` 的「tag 规范」小节会提示大写、非 kebab、超过 3 个、以及词干相近的变体。
- **退役不靠字段**：正文留一条「被 [[…]] 取代」链接，再整篇移 `archive/docs/`；链接断了下一次检查会报出来。

### journal 条目

```markdown
- 15:30 做了什么 / 观察到什么 / 为什么
```

一行一条，不要求完整句子或排版；一个文件对应一天，只追加，不回头整理。

### `docs/` 的门槛

`docs/` 和 `scratch/` 的区别不是“沉淀程度”，而是**是否值得留**：

| | 想留吗 | 组织方式 | 时间性 |
|---|---|---|---|
| `scratch/` | 不想（丢了不心疼） | 无 | 当下草稿 |
| `journal/` | 想留（作为**记录**） | 无，按时间 | 强——“哪天发生的” |
| `docs/` | 想留（作为**知识**） | 有，按主题 | 弱——与时间脱钩 |

进 `docs/` 要同时满足两点：① **时间脱钩**——不知道当时上下文也读得懂；② **有人会来查**——未来的决定 / 实验会回头指向它。不要求完全定论：未成熟可先写并说明局限；拿不准是否值得留的观察先记 `journal/`。

### 产物元数据（可选）

`outputs/` 不要求自带元数据。若希望产物能自证出处，让程序写一份 sidecar；字段样例见 `references/outputs-metadata.md`。

## 惰性初始化（首次写入时）

**没有独立的「初始化」步骤**：只读（冷启动、查资料）不创建任何东西。触发条件：第一次要**写入** `./tmp/`，且 `./tmp/README.md` 不存在。此时只做这套最小动作：

1. 确认当前目录是项目根（`./tmp/` 建在这里，不是子目录）。
2. 若 `./tmp/` 已存在但没有 `README.md`，先按 `references/migration.md` §2 接管：问用户、并入 `tmp/scratch/` 或挪走，不要默默接手。
3. 确保 `.gitignore` 有 `/tmp/`；已有规则就不重复加。
4. 复制 `assets/tmp-readme.md` 成 `./tmp/README.md`。
5. `./tmp/STATE.md` 落一个最小骨架（见下）。
6. 复制 `assets/` 下的工具集到 `./tmp/scripts/`（`memory_lib.py` + `check-memory.py` / `find-memory.py` / `index-memory.py` / `index-experiments.py`；有 Python 3 才需要，没有就跳过并在当天 journal 记一句）。skill 更新后 `check-memory.py` 首行的 `toolset N` 会与新版不一致——那说明副本旧了，重新复制即可。
7. **只创建这次要写的路径**（加上面的入口文件）；其余目录用到再建。

第 3、4 步是**不可逆保护**：少了 `.gitignore`，过程记忆会被提交进版本库、以后 `git clean -fdx` 会连它一起清掉；少了 `README.md`，以后没人知道这个目录不是垃圾。

### 1. 项目 `.gitignore` 追加

```gitignore
# ./tmp —— 过程性记忆，默认不进版本库（整个目录）
/tmp/
```

### 2. `./tmp/STATE.md`（最小骨架）

入口文件，覆盖式更新；初期就是空的，有内容再填：

```markdown
# STATE

## 现在

## 进行中

## 下一步

## 待决 / 阻塞

## 关键链接

## 已毕业
```
