# 初始化材料（逐字落到项目里）

初始化 `./tmp/` 时，下面两段是要**原样落盘**的内容，不是可随意改写的建议。

## 1. `./tmp/README.md`

```markdown
# ./tmp — 项目过程性记忆

> **这个目录不是临时垃圾。** 顶层内容（除 `scratch/` 外）是开发与研究探索的过程记忆，**不要用 `git clean`、清理脚本或手工批量删除**。
> 只有 `scratch/` 可以随时删除。

## 这是什么

- 探索中的、失败的、临时的、还没定论的东西都在这里。
- 项目正式文档在 `./docs/`；本目录只保存"过程"。只有稳定且对项目有价值的结论才"毕业"到 `./docs/`。

## 先看哪里

1. `STATE.md` — 当前状态与下一步（唯一入口）
2. `journal/` — 最近的原始记录
3. 其余按需：`docs/`、`experiments/*/README.md`

## 目录

| 目录 | 用途 | 可删？ |
|---|---|---|
| `STATE.md` | 现状 / 进行中 / 下一步 / 待决 / 关键链接 | 否 |
| `journal/` | 追加式时间线 | 否 |
| `docs/{memory,research,plans}/` | 沉淀后的稳定内容 | 否 |
| `experiments/` | 实验的定义与结论（不含产物） | 否 |
| `outputs/` | 程序产物（内部结构自定） | 否 |
| `annotated/` | 代码讲解与带注释的源码片段 | 否 |
| `show/` | 给人展示/讲解的成品 | 否 |
| `scripts/` | 跨实验复用的工具 | 否 |
| `archive/` | 完成 / 废弃的东西 | 否 |
| `scratch/` | 草稿、一次性文件 | **可以** |

## 脚本输出约定

- 程序产物统一写 `outputs/`，内部结构由程序决定，不设约定。
- 跑完在实验 `README.md` 或 `journal/` 记一行产物位置。

## 约定

- 结果不可变：每次运行独立目录，不覆盖历史。
- 只追加 journal，不回头整理；稳定了才写 `docs/`。
- 详细规则见 skill 的 `references/`。
```

## 2. 项目 `.gitignore` 追加

```gitignore
# ./tmp —— 过程性记忆，默认不进版本库
/tmp/*
# 持久部分：保留
!/tmp/README.md
!/tmp/STATE.md
!/tmp/journal/
!/tmp/docs/
!/tmp/experiments/
!/tmp/annotated/
!/tmp/show/
!/tmp/scripts/
!/tmp/archive/
# 产物：整个忽略（`outputs/` 就是往里放东西的地方）
/tmp/outputs/
# 草稿
/tmp/scratch/

# 若要版本化某个具体产物，用 `!` 单独放行，例如
# !/tmp/outputs/EXP-0001/metrics.csv
```
