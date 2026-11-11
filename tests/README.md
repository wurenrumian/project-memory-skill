# check-memory 工具集测试

`assets/` 下四个入口脚本（`check-memory.py`、`find-memory.py`、`index-memory.py`、`index-experiments.py`）的回归测试与样本库；共享逻辑在 `assets/memory_lib.py`。

## 怎么跑

```bash
python tests/run_tests.py
```

运行器会把 `tests/tmp/` 复制到系统临时目录再跑，**不会改动仓库里的样本**。`git` 不保留 mtime，所以孤儿样本“40 天前修改”这个条件由运行器用 `os.utime` 模拟。

## 性能基准

```bash
python tests/bench.py                # 默认 2000 篇
python tests/bench.py --docs 10000   # 大规模
```

它造一个合成 `tmp/` 再测四个命令，不属于 `run_tests.py`。看两个数：**缓存命中**才是日常开销；**首跑**含建缓存，受杀软与首次读盘影响，同一规模上下能差两三倍，不适合横向比较。

## 样本库 `tests/tmp/`

它是一个最小可用的 `./tmp/` 记忆：`STATE.md` + `docs/` + `experiments/` + `journal/`。

| 文件 | 验证什么 |
|---|---|
| `STATE.md` | 热链接算入链 |
| `docs/memory/cache-shard.md` | 正常 wiki 链接（路径 / 别名 / 标题锚点）、断链、代码块里的 `[[...]]` 不算链接 |
| `docs/memory/link-forms.md` | 带锚点的 Markdown 链接、从项目根写（`./tmp/…`）的 Markdown / wiki 链接、指向目录的链接、大小写不一致的 wiki 链接都算有效 |
| `docs/research/bom-tags.md` | 带 BOM 的文件（Windows 编辑器常见）front-matter 仍能解析 |
| `docs/plans/tag-hygiene.md` | tag 规范提示：大写、非 kebab、同义变体、超过 3 个 |
| `docs/research/latency-notes.md` | 无 tag 文档；被引用后不算孤儿 |
| `docs/memory/notes.md`、`docs/research/notes.md` | `docs/` 内重名 → 歧义链接 `[[notes]]` |
| `docs/plans/link-check.md` | 裸 basename 歧义、带路径链接、md 相对链接 |
| `docs/plans/old-roadmap.md` | 被引用的旧文档不是孤儿（对照） |
| `docs/research/forgotten-idea.md` | 孤儿：入链 0 + mtime 40 天前 |
| `experiments/EXP-000*/README.md` | 实验目录 README 重名不算问题（按路径寻址）；实验索引的状态 / 问题 / 结论来源 |
| `archive/EXP-0003-legacy/` | 归档实验在索引里标 `archived` |
| `archive/INDEX.md` | 追加式归档索引，不参与检查 |
| `journal/2026-11-01.md` | journal 里的链接不计入入链，也不报断链（只追加、修不了） |

## 断言

- `check`：退出码 1，报出断链、歧义、重名、孤儿，且不误报代码块内容；`--json` 四类结果可解析；
- `check` 不误报：带锚点 / 指目录 / `./tmp/` 开头 / 大小写不一致的链接；也不报 `journal/`、`archive/` 里的断链；
- `check --limit 1` 会截断长列表并提示用 `--json`；
- `check` 的「整理」小节给出目录条目数与 journal 活跃月份，样本未到阈值时显示未触发；运行器再往 `docs/plans/` 塞 20 个文件，验证过阈值时提示整理；
- `find --tag storage`：只返回 `docs/memory/cache-shard.md`；
- `find --untagged`：包含两个 `notes.md` 与 `latency-notes.md`；
- `find --orphans`：包含 `forgotten-idea.md`，不包含被引用的 `old-roadmap.md`；
- `index`：生成 `docs/index.md`，文档链接写成 `./tmp/…` 开头的 Markdown 链接，含“正在关注”和按主 tag 分组；**生成后孤儿仍然存在**（防止索引自己制造入链）；
- `index-experiments`：生成 `experiments/INDEX.md`，链接写成 `./tmp/…` 开头的 Markdown 链接，含状态 / 问题 / 结论，归档实验标 `archived`，按 ID 排序；
- 生成的两个索引不出现在检查报告里；
- 生成的 `docs/index.md` 不出现在 `find --untagged` 里；
- 增量缓存：能感知 tag 变化与文件删除，`--no-cache` 可用。

新增检查项时，先往 `tests/tmp/` 加一个最小样本，再在 `run_tests.py` 里加一条断言；样本要能一眼看出是干什么用的。
