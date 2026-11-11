# ./tmp — 项目过程性记忆

> **这个目录不是临时垃圾。** 顶层内容（除 `scratch/` 外）是开发与研究探索的过程记忆，**不要用 `git clean`、清理脚本或手工批量删除**。
> `scratch/` 可以随时删；其余内容退役时移进 `archive/`。只有范围具体、依据清楚的程序产物或明确无保留价值的文件才真删。

## 这是什么

- 探索中的、失败的、临时的、还没定论的东西都在这里。
- 项目正式文档在 `./docs/`；本目录只保存"过程"。值得长期查阅的知识才"毕业"到 `./docs/`（不要求完全定论）。

## 先看哪里

1. `STATE.md` — 当前状态与下一步
2. `docs/index.md` — 全量索引 + 近期活跃的 tag（生成文件，不手改）；找具体文档从这里进
3. `experiments/INDEX.md` — 实验状态 / 问题 / 结论（生成文件）；找实验从这里进
4. `archive/INDEX.md` — 退役内容与原因（追加式）
5. `journal/` — 最近的原始记录
6. `remote/` — 上次同步拉到的远程变化（同步过才有）
7. 其余按需：`experiments/*/README.md`、`docs/`、多 agent 时的 `agents/BOARD.md`

## 目录

| 目录 | 用途 | 可删？ |
|---|---|---|
| `STATE.md` | 现状 / 进行中 / 下一步 / 待决 / 关键链接 | 否 |
| `.memory-cache.json` | 检查工具的增量缓存（可随时删） | **可以** |
| `docs/index.md` | 全量索引 + 正在关注（工具生成，会覆盖） | 否 |
| `docs/{memory,research,plans}/` | 沉淀后的稳定内容 | 否 |
| `journal/` | 追加式时间线 | 否 |
| `remote/` | 远程仓库增量：水位 `cursor.json` + 每次同步的摘要 | 否（`cursor.json` 会被覆盖） |
| `experiments/` | 实验的定义与结论（不含产物） | 否 |
| `experiments/INDEX.md` | 生成的实验索引（状态 / 问题 / 结论） | 否（会覆盖） |
| `outputs/` | 程序产物（内部结构自定）；单个过期实验的产物可删，整目录不批量清 | 部分 |
| `annotated/` | 代码讲解与带注释的源码片段 | 否 |
| `agents/` | 多 agent 协作：BOARD.md 任务板 + 各 agent 子目录 | 否 |
| `scripts/` | 跨实验复用的工具（含 check-memory 工具集） | 否 |
| `scratch/` | 草稿、一次性文件 | **可以** |
| `archive/` | 退役内容：`INDEX.md` + `journal/YYYY-MM/`、`remote/YYYY-MM/`、`docs/`、`annotated/`、`EXP-XXXX-slug/` | 否 |

> 目录按需创建：还没出现的目录只是还没用到。

## 文档约定

- `docs/` 文档只有三种手写内容：**H1 标题、正文、`tags`**；没有 status / title / date 字段——位置就是状态（`docs/` 活、`archive/docs/` 退役）。
- `tags` 只写 front-matter，1~3 个，小写 kebab-case，**第一个是主 tag**；没有 tag 就不写 front-matter。
- 引用写成 Markdown 链接、路径 `./tmp/` 开头（如 `[延迟笔记](./tmp/docs/research/latency-notes.md)`；文件相对写法也认；带 `#标题` 锚点、指向目录都行），不写裸 ID；文末可放一节「引用」集中列出。
- `docs/` 内文档文件名不得重复；实验等按目录路径引用的文件可以重名。裸 basename 链接命中多个文件时，检查工具会报歧义。
- `docs/index.md`、`experiments/INDEX.md` 是生成物，不手改；`archive/INDEX.md` 只追加。
- `.memory-cache.json` 是增量缓存，可随时删；`--no-cache` 强制全量解析。

## 检查与索引

在**项目根**执行：

```bash
python tmp/scripts/check-memory.py               # 结构 / 引用 / 主题 / 整理阈值
python tmp/scripts/check-memory.py --json        # 机器可读
python tmp/scripts/check-memory.py --limit 0     # 列表不截断（默认每类 40 条）
python tmp/scripts/find-memory.py --tag storage  # 按 tag 找文件路径（可重复，多个为 AND）
python tmp/scripts/find-memory.py --untagged     # 没有 tag 的文档
python tmp/scripts/find-memory.py --orphans      # 孤儿清单
python tmp/scripts/index-memory.py               # 重新生成 docs/index.md
python tmp/scripts/index-experiments.py          # 重新生成 experiments/INDEX.md
```

- **结构**：断链、裸 basename 歧义、`docs/` 重名——有问题时退出码 1；首行 `toolset N` 是工具集版本，比 skill 里的旧就该重新复制 `tmp/scripts/`；
- **引用**：孤儿 = 入链 0 且 mtime 超过 30 天的 `docs/` 文档，只是复核线索；`journal/`、`remote/`、`archive/`、`scratch/` 既不算入链，也不报断链；
- **主题**：无 tag 文档、tag 计数，以及 tag 规范提示（大写 / 非 kebab / 超过 3 个 / `cache` 与 `caching` 这类变体）；“近期活跃”按 mtime 推算，是启发式指标；
- **整理**：直接给出目录条目数与 `journal/` 活跃月份，过阈值时提示整理一轮。

## 脚本输出约定

- 程序产物统一写 `outputs/`，内部结构由程序决定，不设约定。
- 跑完把产物位置记在一处：有归属实验记实验 `README.md`「运行记录」，没归属记当天 `journal/`。
- 单个过期实验的产物可以删或移 `archive/`（在运行记录里留一行）；但整目录不要用 `git clean`、清理脚本或手工批量删除——只此一个例外，其余顶层内容（除 `scratch/`）不可批量删。

## 约定

- 结果不可变：每次运行独立目录，不覆盖历史。
- 只追加 journal，不回头整理；值得长期查阅的知识才写 `docs/`（不要求完全定论）。
- `remote/cursor.json` 与生成的 `docs/index.md` 是仅有的两处覆盖写：前者是同步水位，后者是派生索引。远程带来的变化只当作原料，结论仍写回本地 `STATE.md` / `docs/`。
- 多 agent 并行时启用 `agents/`：任务上 `BOARD.md` 认领，进展写各自 `agents/<agent-id>/`，全局 `STATE.md` 只在收尾时更新。
- 整理是**提示制**：任一可读目录 ≥16 条、`journal/` 活跃月份 >2 时提示（`check-memory.py` 的「整理」小节会直接给数）；旧整月滚到 `archive/`，退役文档移 `archive/docs/`——移动，不删。
- 每次归档在 `archive/INDEX.md` 追加一行：日期 / 原路径 / 去向 / 原因或取代者。
- 可以把本目录直接当作 Obsidian vault 打开（vault 根 = `./tmp/`）。
- 详细规则见本机安装的 project-memory skill（如 `~/.config/opencode/skills/project-memory/`）；没装它的人以本文件的约定为准。
