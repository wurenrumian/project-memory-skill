# project-memory

在项目根的 `./tmp/` 下维护一份**过程性记忆**：项目记忆、研究讲解、脚本、实验记录、实验结果、当前状态与后续方向。

它**不是**项目文档。`./docs/` 是给项目读者的结论，`./tmp/` 是产生这些结论的过程。

## 何时用

- 用户说"记录一下 / 记一下这个结论 / 维护项目状态 / 当前进度 / 下一步 / 研究记录 / 实验记录 / 开个实验 / 记录实验结果 / 整理探索笔记 / 这些先别放进 docs"
- 用户说"整理一下 tmp / 清理一下文档 / 按 tag 找文档 / 检查断链"
- 提到 project memory、journal、experiment run、文档索引、多 agent 协作
- 用户 pull / fetch 之后要"同步一下远程 / 看看远程有什么变化"

## 核心规则

1. **`./tmp/` 只放过程，项目 `./docs/` 只放结论。** 探索中的、失败的、临时的内容进 `./tmp/`；稳定且对项目有价值的才"毕业"到 `./docs/`。
2. **实验定义与运行产物分开。** 定义在 `experiments/`（小、稳定、人读），产物在 `outputs/`（多、只增、程序写）。
3. **捕获便宜，沉淀才排版。** 日常只往 `journal/` 追加一行；值得长期查阅的知识才写 `docs/`（不要求完全定论）。
4. **产物不覆盖**，也别写进 `experiments/`。
5. **两个入口，各有分工。** 了解现状先读 `./tmp/STATE.md`；查找具体文档先看 `./tmp/docs/index.md`；都不必通读整个 `./tmp/`。
6. **删除是最后手段，移动是常态。** 完成 / 废弃的东西默认移进 `archive/`；`scratch/` 可随时删；只有范围具体、依据清楚的程序产物或明确无保留价值的文件才真删。
7. **初始化是惰性的。** 只读不建；第一次**写入**时才落最小集合（`.gitignore` 规则、`README.md`、`STATE.md`、`scripts/` 工具集）。
8. **多 agent 只动自己的地盘**，任务在 `agents/BOARD.md` 认领（认领即锁）。
9. **远程信息只是原料**：远程的提交 / PR 增量进 `remote/`，再反过来更新本地记忆；`remote/cursor.json` 与生成的 `docs/index.md` 是仅有的两处覆盖写。

## 目录结构

`./tmp/` 是整个目录默认不进版本库的**唯一根**，顶层（除 `scratch/` 外）受"不可随意删"约定保护。目录**按需创建**——下面列的是「该放哪」，不是启动时全建出来。

```
./tmp/
├── README.md            # 这目录是什么、"顶层不可随意删"的约定、入口指引
├── STATE.md             # 【必读】现在 / 进行中 / 下一步 / 待决 / 关键链接
├── .memory-cache.json   # 检查工具的增量缓存（可删）
├── journal/             # 追加式时间线，一天一个文件
├── remote/              # 远程仓库增量：cursor.json 水位 + 每次同步的摘要
├── docs/                # 沉淀后的稳定内容：memory/ research/ plans/
│   └── index.md         # 生成的全量索引 + 正在关注，不手改
├── experiments/         # 实验的「定义与结论」（不含产物）
│   ├── INDEX.md         # 生成的实验索引（状态 / 问题 / 结论）
│   └── EXP-XXXX-slug/   # 每个实验一个目录
├── outputs/             # 所有程序产物；内部结构自定
├── annotated/           # 需着重讲解 / 强调的代码
├── agents/              # 多 agent 协作：BOARD.md + 各 agent 子目录（并行才建）
├── scripts/             # 跨实验复用的工具（含 check-memory 工具集）
├── scratch/             # 真正的草稿，允许随时删
└── archive/             # 退役内容：INDEX.md + journal/ remote/ docs/ EXP-XXXX-slug/
```

## 冷启动协议

1. 读 `./tmp/STATE.md`。不存在说明还没有任何记忆，按空状态继续——**只读不初始化**。
2. 读最新一个 `./tmp/journal/*.md` 的尾部。
3. 看 `./tmp/remote/cursor.json`（存在才看）：与 `origin/main` 对不上或已过一周，提示用户"要不要同步一次远程"——只提示，不自动联网。
4. 按 `STATE.md` 的「关键链接」按需读对应 `docs/` 文档或 `experiments/*/README.md`；找实验状态读 `./tmp/experiments/INDEX.md`，找文档读 `./tmp/docs/index.md`，不扫目录。存在 `./tmp/agents/` 时看一眼 `BOARD.md` 的认领情况。
5. 只在必要时才深入 `outputs/`；怀疑文档过期时跑 `check-memory.py` 看孤儿与断链。

## 其他要点

- **文档约定**：`docs/` 文档只有 H1 + 正文 + `tags` + 引用链接；front-matter 只保留 `tags`（第一个是主 tag）；引用优先 wiki 链接 `[[从 tmp 根的路径]]`（Markdown 相对链接也接受）；`docs/` 内文件名不重复，实验等按路径引用的文件可以重名。
- **索引**：`docs/index.md`（知识）与 `experiments/INDEX.md`（实验状态）是生成物，不手改；`archive/INDEX.md`（退役原因）只追加。索引里的“正在关注”按 mtime 推算，是启发式指标。
- **检查**：`check-memory.py` 一次跑完断链 / 歧义 / 重名 / 孤儿 / 无 tag / tag 规范 / 整理阈值（`--limit 0` 不截断）；`find-memory.py` 查 tag / 无 tag / 孤儿；`index-memory.py`、`index-experiments.py` 生成两个索引。解析结果缓存在 `.memory-cache.json`（按 mtime + size + 活目录归属命中，`--no-cache` 可绕过）。孤儿只是复核线索，不是删除结论。
- **链接判定**：带 `#锚点` 的 Markdown 链接、指向目录的链接、Windows / macOS 上大小写不一致的 wiki 链接都算有效；`journal/`、`remote/`、`archive/`、`scratch/` 里的链接不计入入链，也不报断链。
- **整理**：目录条目 ≥16（软）/ ≥20（硬）、`journal/` 活跃月份 >2 时提示——`check-memory.py` 的「整理」小节直接给数，不用手动数；旧整月滚到 `archive/`，退役文档移 `archive/docs/`，每次归档在 `archive/INDEX.md` 追加一行——移动，不删。
- **写入协议**、**惰性初始化的落盘模板**（`assets/tmp-readme.md`）、**实验 ID / journal 格式**见 `SKILL.md`；多 agent 协作见 `references/multi-agent.md`。
- **毕业 / 接管既有 tmp / 旧版 front-matter 迁移**见 `references/migration.md`。
- **远程增量同步**（`remote/` 的 cursor 字段、`git` / `gh` 命令、摘要模板、坑）见 `references/remote-sync.md`。
- `docs/` 的门槛：进 `docs/` 要同时满足 ① 时间脱钩（不知道上下文也读得懂）、② 有人会来查。拿不准就先留 `journal/`。
- 链接优先用 wiki，Markdown 相对路径也可以；结论指向 `outputs/` 里的实际路径，而不是复制粘贴数字。

## 维护与同步

这个 README 只做快速入口、安全边界和常用命令；详细流程以 `SKILL.md` 为准。改规则时同步这几对文件：

| 改什么 | 同步到 |
|---|---|
| 目录结构 | `SKILL.md` 目录树 ↔ `assets/tmp-readme.md` 目录表 |
| 文档约定（tag / 链接 / 索引 / 检查 / 整理） | `SKILL.md` ↔ `README.md` ↔ `assets/tmp-readme.md` |
| 迁移 / 毕业流程 | `references/migration.md` ↔ `SKILL.md` 常用操作 |
| 脚本行为 | `assets/` 工具集 ↔ `tests/tmp/` 样本 ↔ `tests/run_tests.py` |

改完脚本或规则先跑 `python tests/run_tests.py`，全绿再提交。

## 安装

把本目录复制或软链到 agent 的 skills 目录，目录名须与 frontmatter 的 `name:`（`project-memory`）一致：

```powershell
Copy-Item -Recurse . "$env:USERPROFILE\.config\opencode\skills\project-memory"
```

## 目录内容

- `SKILL.md` — skill 本体。
- `assets/tmp-readme.md` — 首次写入时原样复制到项目的 `./tmp/README.md`。
- `assets/memory_lib.py` — 扫描 / 解析 / 链接解析 / 统计的共享逻辑。
- `assets/check-memory.py` — 检查入口（断链、歧义、重名、孤儿、tag）。
- `assets/find-memory.py` — 查询入口（`--tag`、`--untagged`、`--orphans`）。
- `assets/index-memory.py` — 生成 `docs/index.md`。
- `assets/index-experiments.py` — 生成 `experiments/INDEX.md`。
- `tests/` — 工具集的回归测试与最小样本库，`python tests/run_tests.py`。
- `references/multi-agent.md` — 多 agent 协作的任务板格式与认领规则。
- `references/remote-sync.md` — 远程增量同步：水位、`git` / `gh` 命令、摘要模板、边界。
- `references/migration.md` — 毕业到项目 docs、接管既有 `tmp/`、旧版记忆升级。
- `references/outputs-metadata.md` — 可选的产物 sidecar 字段样例。

## 相关

- `geeklens` — 聚焦代码阅读版，产物落 `./tmp/annotated/`。
- `host-memory` — 主机级、跨项目的记忆。
