# ./tmp — 项目过程性记忆

> **这个目录不是临时垃圾。** 顶层内容（除 `scratch/` 外）是开发与研究探索的过程记忆，**不要用 `git clean`、清理脚本或手工批量删除**。
> 只有 `scratch/` 可以随时删除。

## 这是什么

- 探索中的、失败的、临时的、还没定论的东西都在这里。
- 项目正式文档在 `./docs/`；本目录只保存"过程"。只有稳定且对项目有价值的结论才"毕业"到 `./docs/`。

## 先看哪里

1. `STATE.md` — 当前状态与下一步（唯一入口）
2. `journal/` — 最近的原始记录
3. `remote/` — 上次同步拉到的远程变化（同步过才有）
4. 其余按需：`docs/`、`experiments/*/README.md`、多 agent 时的 `agents/BOARD.md`

## 目录

| 目录 | 用途 | 可删？ |
|---|---|---|
| `STATE.md` | 现状 / 进行中 / 下一步 / 待决 / 关键链接 | 否 |
| `journal/` | 追加式时间线 | 否 |
| `remote/` | 远程仓库增量：水位 `cursor.json` + 每次同步的摘要 | 否（`cursor.json` 会被覆盖） |
| `docs/{memory,research,plans}/` | 沉淀后的稳定内容 | 否 |
| `experiments/` | 实验的定义与结论（不含产物） | 否 |
| `outputs/` | 程序产物（内部结构自定） | 否 |
| `annotated/` | 代码讲解与带注释的源码片段 | 否 |
| `agents/` | 多 agent 协作：BOARD.md 任务板 + 各 agent 子目录 | 否 |
| `scripts/` | 跨实验复用的工具 | 否 |
| `archive/` | 完成 / 废弃的东西 | 否 |
| `scratch/` | 草稿、一次性文件 | **可以** |

> 目录按需创建：还没出现的目录只是还没用到。

## 脚本输出约定

- 程序产物统一写 `outputs/`，内部结构由程序决定，不设约定。
- 跑完把产物位置记在一处：有归属实验记实验 `README.md`「运行记录」，没归属记当天 `journal/`。

## 约定

- 结果不可变：每次运行独立目录，不覆盖历史。
- 只追加 journal，不回头整理；稳定了才写 `docs/`。
- `remote/cursor.json` 是**唯一**会被覆盖的文件（同步水位）。远程带来的变化只当作原料，结论仍写回本地 `STATE.md` / `docs/`。
- 多 agent 并行时启用 `agents/`：任务上 `BOARD.md` 认领，进展写各自 `agents/<agent-id>/`，全局 `STATE.md` 只在收尾时更新。
- 详细规则见 project-memory skill。
