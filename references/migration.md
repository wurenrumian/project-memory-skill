# 迁移与毕业

三种“搬家”都走本文件：把 `./tmp/docs/` 的结论搬进项目 `./docs/`（毕业）、接管一个已存在的 `./tmp/`、把旧版记忆升级到当前极简格式。主文件的规则不在这里重复；冲突时以主文件为准。

## 1. 毕业：`./tmp/docs/` → 项目 `./docs/`

**触发**：用户说“毕业 / 沉淀到项目文档 / 这份可以进 docs 了”。**先问，不要擅自写项目 `docs/`。**

1. **先看目标**：项目 `docs/` 是否已有同类文档？有就合并进现有文档，不新建平行的一篇。
2. **重写，不复制**：按项目 `docs/` 自己的格式与语气重写（标题层级、术语、示例）；`./tmp/` 的 journal 口吻与实验表格不进入项目文档。
3. **去掉过程痕迹**：未决推测、失败路径、内部短链改成项目内可用的链接；引用产物写实际路径。
4. `STATE.md` 记一行：`- 已毕业：tmp/docs/research/xxx.md → docs/xxx.md`。
5. **原件不删**：保留原文，或加一条「已毕业到 `docs/xxx.md`」链接后移到 `archive/docs/`。
6. `docs/index.md` 不参与毕业——它是 `./tmp/` 的派生索引。

> 毕业不是同步：两处内容不会自动一致；项目文档是权威版本，`./tmp/` 原件只作历史。

## 2. 接管已存在的 `./tmp/`

首次写入时，如果 `./tmp/` 已存在但**没有 `README.md`**（可能是旧工具、旧流程或别人的临时目录）：

1. **先问用户**，不要默默接手；
2. 三个选项：并入 `tmp/scratch/` 后接管、整体挪到别处、用户自己处理；
3. 选择并入时只移动内容，不批量改写；当天 journal 记一行“接管了哪个目录、多少文件、怎么处理”；
4. 之后再按「惰性初始化」落 `.gitignore`、`README.md`、`STATE.md`。

## 3. 旧版记忆升级（7 字段 front-matter → 极简 `tags`）

旧文档的 front-matter 是 `title / type / status / created / updated / tags / related`。一次性迁移：

| 旧字段 | 处理 |
|---|---|
| `tags` | 保留；重排成 1~3 个，第一个是主 tag |
| `type` | 删；看它所在的子目录 |
| `status: deprecated` | 删；正文加一条「被 … 取代」的 Markdown 链接（`./tmp/…`），整篇移 `archive/docs/` |
| `status: draft / stable` | 删；位置即状态 |
| `title` | 删；保留正文 H1 |
| `created / updated` | 删；mtime / git 承担 |
| `related: [EXP-0001, …]` | 展开成正文「引用」节的 Markdown 链接（`./tmp/…`），裸 ID 不留 |

迁移后：

1. 跑 `python tmp/scripts/check-memory.py`，逐条修断链、`docs/` 重名、歧义链接；
2. 跑 `python tmp/scripts/index-memory.py` 与 `python tmp/scripts/index-experiments.py` 重建索引；
3. 当天 journal 记一行“迁移了 N 篇，修了 M 条链接”。

**只在用户同意时动既有文档，不批量重写正文。** 先迁一小批（如 `docs/memory/`），确认检查和索引正常，再迁其余。

## 4. 从别的工具搬进来

- **Obsidian / SilverBullet / Logseq（md 系）**：wiki 链接 `[[…]]` 与 `tags` 基本可直接用；Logseq 的块缩进与 `property::` 语法需要手动清掉。
- **zk**：`zk list --format json` 可导出路径与 tag，但不要把 `./tmp/` 改成 zk 的索引语义。
- 搬进来后按第 3 节跑一遍检查与索引。

## 检查清单

- [ ] 毕业前问过用户，目标文档已按项目格式重写
- [ ] `STATE.md` 有「已毕业」记录
- [ ] 原件保留或移入 `archive/docs/`，没有删除
- [ ] 迁移后 `check-memory.py` 无结构错误，两个 index 脚本已重跑
- [ ] 只迁了用户同意的范围
