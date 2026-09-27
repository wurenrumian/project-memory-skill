---
name: project-memory
description: 在项目根的 ./tmp/ 下维护开发与研究探索的项目记忆、实验记录与状态（项目记忆、研究讲解、脚本、实验记录、实验结果、当前状态与后续方向）。当用户要"记录一下/记一下这个结论/维护项目状态/当前进度/下一步/研究记录/实验记录/开个实验/记录实验结果/整理探索笔记/这些先别放进 docs"，或提到 project memory、journal、experiment run 时使用。Maintain project memory, research notes, experiment records and current state under ./tmp/.
---

# Project Memory

在项目根的 `./tmp/` 下维护一份**过程性记忆**：项目记忆、研究讲解、脚本、实验记录、实验结果、当前状态与后续方向。

它**不是**项目文档。`./docs/` 是给项目读者的结论，`./tmp/` 是产生这些结论的过程。

## 核心规则

1. **`./tmp/` 只放过程，项目 `./docs/` 只放结论。** 探索中的、失败的、临时的、还没定论的内容一律进 `./tmp/`；只有稳定且对项目有价值的内容才"毕业"到 `./docs/`，并在 `STATE.md` 记一笔。
2. **实验定义与运行产物分开。** 定义在 `experiments/`（小、稳定、人读），产物在 `outputs/`（多、只增、程序写）。
3. **捕获便宜，沉淀才排版。** 日常只往 `journal/` 追加一行；只有结论稳定了才写 `docs/`。不要边做边写文档。
4. **产物不覆盖。** 程序产物写进 `outputs/`，内部结构由程序决定，skill 不限制；但别覆盖历史产物。
5. **入口唯一。** 任何需要"了解现状"的场合，先读 `./tmp/STATE.md`，不要通读整个 `./tmp/`。

## 冷启动协议

需要了解项目当前状态、或继续之前的工作时：

1. 读 `./tmp/STATE.md`（不存在就先初始化，见下）。
2. 读最新一个 `./tmp/journal/*.md` 的尾部。
3. 按 `STATE.md` 的「关键链接」按需读对应 `docs/` 文档或 `experiments/*/README.md`。
4. 只在必要时才深入 `outputs/`。

## 写入协议

| 情况 | 动作 | 位置 |
|---|---|---|
| 任何"以后可能有用"的观察 / 想法 / 进展 | 追加一行 | `journal/YYYY-MM-DD.md` |
| 一个决策、约定、架构、坑定下来了 | 写一篇 | `docs/memory/` |
| 写完研究讲解 / 分析 / 论文笔记 | 写一篇 | `docs/research/` |
| 有新方案 / 路线 / 待验证想法 | 写一篇 | `docs/plans/` |
| 开新实验 | 建目录 | `experiments/EXP-XXXX-slug/` |
| 程序产生产物 | 往 `outputs/` 写，并在实验或 journal 记一行位置 | `outputs/`（内部自定） |
| 写下代码讲解 / 带注释的源码 | 建文件或主题目录 | `annotated/<topic-slug>(.md | /)` |
| 做要展示/讲给他人的成品 | 建主题目录 | `show/<topic-slug>/` |
| 会话收尾 / 换任务 | 更新 STATE | `STATE.md` |
| 实验做完 / 想法废弃 | 移动，不删 | `archive/` |

> **产物永远不写进 `experiments/`，一律进 `outputs/`。** 内部结构由程序决定，但要在实验 `README.md` 或 journal 记一行产物位置。实验定义与运行产物生命周期相反，必须分开（理由见 `references/layout.md`）。

**默认只追加 journal。** 升级到 `docs/` 的前提是内容已稳定、以后还会被引用（门槛见 `references/conventions.md`）。写之前先看该文件里对应的结构约定。

## 初始化

项目里第一次使用，把骨架铺到项目根 `./tmp/`：

```
./tmp/README.md            <- references/bootstrap.md 第 1 段（逐字）
./tmp/STATE.md             <- references/conventions.md「STATE.md」结构
./tmp/journal/
./tmp/docs/memory/  ./tmp/docs/research/  ./tmp/docs/plans/
./tmp/experiments/  ./tmp/outputs/  ./tmp/annotated/  ./tmp/show/
./tmp/scripts/  ./tmp/scratch/  ./tmp/archive/
```

项目 `.gitignore` 按 `references/bootstrap.md` 第 2 段追加。完整定义见 `references/layout.md`。

## 收尾协议

一次会话 / 一段工作结束时：

1. 更新 `STATE.md` 的「现在 / 进行中 / 下一步」，已完成的移走或移入 `archive/`。
2. 把当天 `journal/` 里散落的结论**索引化**：写进 `docs/`，或在 `STATE.md` 挂链接。
3. 若某个结论已稳定且对项目有价值 → **提议**"毕业"到 `./docs/`（先问用户，不要擅自改项目 docs）。

## 详细定义

- 目录结构：`references/layout.md`
- 命名 / 元数据 / 时间戳 / 各类文件结构：`references/conventions.md`
- 逐步流程（初始化、建实验、记录 run、沉淀、毕业、归档）：`references/workflows.md`
- 初始化材料（逐字落盘）：`references/bootstrap.md`
