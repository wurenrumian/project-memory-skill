# project-memory

在项目根的 `./tmp/` 下维护一份**过程性记忆**：项目记忆、研究讲解、脚本、实验记录、实验结果、当前状态与后续方向。

它**不是**项目文档。`./docs/` 是给项目读者的结论，`./tmp/` 是产生这些结论的过程。

## 何时用

- 用户说"记录一下 / 记一下这个结论 / 维护项目状态 / 当前进度 / 下一步 / 研究记录 / 实验记录 / 开个实验 / 记录实验结果 / 整理探索笔记 / 这些先别放进 docs"
- 提到 project memory、journal、experiment run、多 agent 协作

## 核心规则

1. **`./tmp/` 只放过程，项目 `./docs/` 只放结论。** 探索中的、失败的、临时的内容进 `./tmp/`；稳定且对项目有价值的才"毕业"到 `./docs/`。
2. **实验定义与运行产物分开。** 定义在 `experiments/`（小、稳定、人读），产物在 `outputs/`（多、只增、程序写）。
3. **捕获便宜，沉淀才排版。** 日常只往 `journal/` 追加一行；结论稳定了才写 `docs/`。
4. **产物不覆盖**，也别写进 `experiments/`。
5. **入口唯一。** 需要"了解现状"时先读 `./tmp/STATE.md`，不通读整个 `./tmp/`。
6. **删除是最后手段。** 完成 / 废弃的东西移进 `archive/`。
7. **初始化是惰性的。** 只读不建；第一次**写入**时才落最小集合（`.gitignore` 规则、`README.md`、`STATE.md`）。
8. **多 agent 只动自己的地盘**，任务在 `agents/BOARD.md` 认领（认领即锁）。

## 目录结构

`./tmp/` 是整个目录默认不进版本库的**唯一根**，顶层（除 `scratch/` 外）受"不可随意删"约定保护。目录**按需创建**——下面列的是「该放哪」，不是启动时全建出来。

```
./tmp/
├── README.md            # 这目录是什么、"顶层不可随意删"的约定、入口指引
├── STATE.md             # 【必读】现在 / 进行中 / 下一步 / 待决 / 关键链接
├── journal/             # 追加式时间线，一天一个文件
├── docs/                # 沉淀后的稳定内容：memory/ research/ plans/
├── experiments/         # 实验的「定义与结论」（不含产物）
├── outputs/             # 所有程序产物；内部结构自定
├── annotated/           # 需着重讲解 / 强调的代码
├── agents/              # 多 agent 协作：BOARD.md + 各 agent 子目录（并行才建）
├── scripts/             # 跨实验复用的工具
├── scratch/             # 真正的草稿，允许随时删
└── archive/             # 完成 / 废弃的东西移到这里，不删
```

## 冷启动协议

1. 读 `./tmp/STATE.md`。不存在说明还没有任何记忆，按空状态继续——**只读不初始化**。
2. 读最新一个 `./tmp/journal/*.md` 的尾部。
3. 按 `STATE.md` 的「关键链接」按需读对应 `docs/` 文档或 `experiments/*/README.md`；存在 `./tmp/agents/` 时看一眼 `BOARD.md` 的认领情况。
4. 只在必要时才深入 `outputs/`。

## 其他要点

- **写入协议**、**惰性初始化的逐字落盘文本**、**实验 ID / front-matter / journal 格式**、**多 agent 协作**等完整规则见 `SKILL.md`。
- `docs/` 的门槛：进 `docs/` 要同时满足 ① 时间脱钩（不知道上下文也读得懂）、② 有人会来查。拿不准就先留 `journal/`。
- 链接一律用相对路径；结论指向 `outputs/` 里的实际路径，而不是复制粘贴数字。

## 安装

把本目录复制或软链到 agent 的 skills 目录，目录名须与 frontmatter 的 `name:`（`project-memory`）一致：

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.config\opencode\skills\project-memory"
```

## 目录内容

- `SKILL.md` — skill 本体。

## 相关

- `geeklens` — 聚焦代码阅读版，产物落 `./tmp/annotated/`。
- `host-memory` — 主机级、跨项目的记忆。
