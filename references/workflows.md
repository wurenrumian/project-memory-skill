# 逐步流程

结构约定在 `references/conventions.md`，逐字落盘的材料在 `references/bootstrap.md`——没有单独的模板文件，按约定直接写。

## 1. 初始化项目记忆

当项目根没有 `./tmp/STATE.md`：

1. 确认当前目录是项目根（`./tmp/` 应建在这里，不是子目录）。
2. 按 `references/layout.md` 建目录：
   `journal/`、`docs/{memory,research,plans}/`、`experiments/`、`outputs/`、`annotated/`、`show/`、`scripts/`、`scratch/`、`archive/`。
3. `./tmp/README.md` ← `references/bootstrap.md` 第 1 段（逐字）。
4. `./tmp/STATE.md` ← 按 `references/conventions.md` 的「STATE.md」结构。
5. 项目 `.gitignore` 按 `references/bootstrap.md` 第 2 段追加（先看是否已有 `tmp` 规则）。
6. 告诉用户：已建好，`scratch/` 可随意删，其余顶层受"不可删"约定保护。

## 2. 开一个新实验

1. 扫 `experiments/` 与 `archive/` 取下一个 `EXP-XXXX`。
2. 建 `experiments/EXP-XXXX-slug/`，含 `README.md`、`config.yaml`、`scripts/`。
   **不要在这里建产物目录**——产物去 `outputs/`。
3. `README.md` 初期只填「状态 / 问题 / 假设 / 方法」，结论留空，跑完再补。
4. 在 `STATE.md` 的「进行中」加一行，链到该实验；当天 journal 记一行。

## 3. 跑脚本 / 记录产物

1. 让程序把产物写进 `outputs/`——**内部结构由程序决定，skill 不做任何规定**。
2. 在实验 `README.md` 的「运行记录」加一行，或当天 `journal/` 记一行，指出产物位置。
3. **不要覆盖历史产物。** 重跑就让程序新建（怎么组织由它决定）。
4. 想记来源就让程序写（可选，参考 `conventions.md` 的「产物元数据」）。
5. 归档实验时，对应产物一起移走或删（`outputs/` 整体默认不进版本库）。

## 4. 写下代码讲解

1. 看内容选形态：纯讲解 → `annotated/<topic-slug>.md`；带注释的源码片段 → `annotated/<topic-slug>.<ext>`；要放讲解+代码+变体 → `annotated/<topic-slug>/` 目录。详见 `references/conventions.md`。
2. 摘来的源码记好来源（原路径 + commit / 日期）。
3. 关键是**围绕代码讲**，区别于 `docs/research/`（正文是文档、代码只是佐证）。

## 5. 做展示材料

1. 建 `show/<topic-slug>/`。
2. 放成品（slides / 图 / demo 脚本 / 一页纸），必要时带一个 `README.md` 说明给谁看、怎么用。
3. 展示完：稳定结论走正常「毕业」到 `docs/`；`show/` 本身当素材留着或归档。

## 6. 沉淀成文档

当某个结论稳定、以后还会被引用：

1. 判断类型：记忆/决策 → `docs/memory/`；研究讲解/分析 → `docs/research/`；方案/路线 → `docs/plans/`。
2. 按 `references/conventions.md` 的对应结构写，填好 front-matter，`status: stable`。
3. 在 `STATE.md` 的「关键链接」挂上。
4. 把 journal 里相关行的时间范围写进文档的"来源"一节，便于回溯。
5. 相关实验 `README.md` 的「结论」也要更新。

## 7. 毕业到项目 `./docs/`

`./tmp/` 的内容**默认不进入项目文档**。只有当它同时满足：

- 结论稳定（不再变）；
- 对项目读者（不只是你）有价值；
- 不依赖探索过程就能读懂；

才提议毕业：

1. **先问用户**，不要擅自写项目 `docs/`。
2. 用户同意后，按项目 docs 自己的格式重写（不是复制 `./tmp/` 的排版）。
3. 在 `STATE.md` 记一行：`已毕业：<tmp 路径> → <docs 路径>`。
4. `./tmp/` 里的原件保留，`status` 标 `deprecated` 或移到 `archive/`，指向 docs 的新位置。

## 8. 收尾

一次会话 / 一段工作结束：

1. 更新 `STATE.md`「现在 / 进行中 / 下一步」，删掉已完成的。
2. 当天 journal 里散落的结论索引化（写 docs 或挂链接）。
3. 有实验完成 → 补 `README.md` 结论，可选移到 `archive/`。
4. 遗留的阻塞写进「待决 / 阻塞」。

## 9. 归档

- 完成或废弃的实验：`experiments/EXP-XXXX-slug/` → `archive/EXP-XXXX-slug/`；对应产物一起移走或删除（`outputs/` 整体默认不进版本库）。
- 过时文档：`status: deprecated` 优先；确实无参考价值再移 `archive/`。
- **删除是最后手段。** 记忆的价值常在"想起当初为什么放弃"。
