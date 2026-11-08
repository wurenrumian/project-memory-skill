# 远程增量同步

`journal/` 记的是"我方做过什么"；远程仓库（别的机器、别的 agent、同事）发生了什么，它看不见。本文件是把「上次同步 → 现在」这段远程变化拉进 `./tmp/` 的可执行细节。

主文件的规则在这里不重复；冲突时以主文件为准。

**触发**：用户 `pull` / `fetch` 之后，或用户说"同步一下远程 / 看看远程有什么变化"。冷启动只提示，不自动联网。

---

## 0. 先确认能力，再决定档位

```bash
git rev-parse --is-inside-work-tree   # 不是 git 仓库 → 整套不适用，跳过
git remote -v                         # 没有 remote → 只有本地历史，跳过
gh auth status                        # 失败 → 降级为「仅 git」
```

| 档位 | 条件 | 拿到什么 |
|---|---|---|
| 完整 | git + `gh` 可用 | 提交增量 + PR 的合入 / 关闭 / 未决 |
| 降级（仅 git） | 无 `gh`、GitLab、内网 | 只有提交；PR 语义全缺，**摘要头部必须标降级** |

GitLab 用 `glab mr list --merged-after=<date>` 同构替换，规则一致。

---

## 1. 水位 `remote/cursor.json`

```json
{
  "version": 1,
  "remote": "origin",
  "refs": {
    "origin/main": { "sha": "def5678", "synced_at": "2026-09-29T09:12:00+08:00" }
  },
  "prs": { "updated_through": "2026-09-29T09:12:00+08:00" },
  "last_digest": "remote/2026-09-29.md"
}
```

- **`refs.<ref>.sha` 与 `prs.updated_through` 必须分开存。** git 有 sha 可精确切范围，PR 只有时间戳，用 sha 去算 PR 增量是错的。
- `synced_at` / `updated_through` 是 git 侧的兜底基准（见 §2）和 PR 侧的查询起点，两者取同一个时刻，便于对齐。
- 只存**默认分支**的水位。别的分支按需再进 `refs`，别一开头就摊开全部。
- 默认分支名别硬编码 `main`：

```bash
git symbolic-ref --short refs/remotes/origin/HEAD   # → origin/main 或 origin/master
```

- `cursor.json` 是 `./tmp/` 里唯一允许覆盖的文件。它是指针，不是历史；覆盖它不违反"产物不覆盖"。覆盖用「写临时文件再 rename / 移动替换」，别原地改写——半截 JSON 会让下次同步解析挂掉（同 §6.8）。

---

## 2. git 侧：算提交增量

```bash
git fetch --prune origin
OLD=<cursor 里的 sha>                     # 首次同步没有 → 见 §6
NEW=$(git rev-parse origin/main)

if git merge-base --is-ancestor "$OLD" origin/main; then
  git log --no-merges --date=short \
    --format='%h %ad %an %s' "$OLD..origin/main"
  git rev-list --count "$OLD..origin/main"          # 数量
  git diff --stat "$OLD..origin/main"               # 触及了哪些文件（有界）
else
  # 历史被 rebase / force-push 改写，sha 区间不可信
  git log --no-merges --date=short \
    --format='%h %ad %an %s' --since='<synced_at>' origin/main
fi
```

- **`--is-ancestor` 这一步不能省。** 直接用 `$OLD..origin/main` 在历史被改写时会算出一个巨大的错误区间（把公共祖先之前的全部提交算成"新增"）。
- 走了 `--since` 兜底，摘要头部要标 `范围不精确（历史被改写，按时间取）`。
- `--no-merges` 让 squash 仓库和 merge 仓库的产出形态接近：squash 出来的压缩提交本身就带 PR 标题。
- 想看某条提交动了什么：`git show --stat <sha>`，**不要**默认拉全 diff。

---

## 3. PR 侧：三个查询，按时间分类

```bash
SINCE=<cursor.prs.updated_through>   # 进 --search 的时间串截断成 YYYY-MM-DD（见下）

# ① 真正合入的 —— 摘要主体
gh pr list --state merged --search "merged:>=$SINCE" --limit 50 \
  --json number,title,mergedAt,author,url,files

# ② 关闭但没合入的 —— 往往比合入更有信息量（为什么放弃）
gh pr list --state closed --search "closed:>=$SINCE is:unmerged" --limit 50 \
  --json number,title,closedAt,author,url

# ③ 有新动静但还没定的
gh pr list --state open --search "updated:>=$SINCE" --limit 50 \
  --json number,title,updatedAt,author,url
```

分类规则：

| 落哪一节 | 依据 |
|---|---|
| 合入 | 有 `mergedAt` |
| 关闭未合入 | 有 `closedAt` 且无 `mergedAt` |
| 新开 / 有更新（未定） | 只有 `updatedAt` |

- **`updated:` 只是"有动静"，不是"有变化"。** 评论、标签、机器人都会刷 `updatedAt`。所以查询 ③ 只用来提示"这个 PR 有人在动"，别据此下结论，也别把它混进合入。
- **比较边界截断到日期。** gh 的 `--search` 对带时区偏移的时间串（`+08:00`）兼容性不稳，所以进 search 的 `$SINCE` 截断成 `YYYY-MM-DD`。多捞 / 漏掉的一两分钟，靠 cursor 的精确时间戳和摘要范围判重兜底（同 §6.5）。
- **不拉 diff。** 只要 `files` 里的路径列表就够关联，正文按需 `gh pr view <n> --json body` 单独取。
- 选项：仓库用 releases 就补一条 `gh release list --limit 5`；不用就跳过，别为了完整而完整。

---

## 4. 写摘要 `remote/YYYY-MM-DD.md`

一天一份，每次同步**追加**一节 `## HH:MM`，不回头改已写小节（同 `journal/` 的只追加约定）。

```markdown
# 远程增量 2026-09-27 → 2026-09-29

- 范围：`origin/main abc1234..def5678`（12 commits）· 时间 2026-09-27 10:00 → 2026-09-29 09:12 (+08:00)
- 抓取：2026-09-29 09:12
- 降级：无

## 合入（3）

- #124 feat: 缓存分片 — @alice — 2026-09-28 · <url>
  - 触及 `src/cache/shard.ts`、`docs/memory/storage-latency-model.md`
- #125 ...

## 关闭未合入（1）

- #126 refactor: 换存储引擎 — @bob · <url> — 放弃原因见讨论

## 新开 / 有更新（2，未定）

- #127 ...

## 对我方的影响

- `docs/memory/storage-latency-model.md` 被 #124 改动 → 复核数字与「来源」
- STATE「待决」#2（等上游分片方案）已被 #124 解决 → 候选收尾
```

头部三行（范围 / 抓取 / 降级）是**判重依据**：下次同步先看一眼最近一份摘要覆盖到哪，与 cursor 对不上就以 cursor 为准并在摘要里写明差异。

---

## 5. 反向更新本地记忆

摘要写完、cursor 推完，才动本地结论。`## 对我方的影响` 里写的都是**候选**，不是既成事实：

| 远程变化 | 动作 | 落到哪 |
|---|---|---|
| 让「待决 / 阻塞」某条过时 | 改写或移走，别一直挂着 | `STATE.md` |
| 改到某篇 `docs/` 讲的东西 | 复核；过时标 `status: deprecated`，内容变了更新 `updated` + 补「来源」 | `docs/**` |
| 改到实验依赖的代码 / 数据 | 记一句可复现性风险 | 实验 `README.md`「未决」 |
| 只跟别人有关 | 不动 | 留在 `remote/` |

- `journal/` 只记**一行指针**，不抄内容：
  ```markdown
  - 09:12 远程同步 abc1234..def5678：合入 3、关闭 1、新开 2；详见 remote/2026-09-29.md
  ```
- **措辞要重写。** 摘要里可以照抄 PR 标题；进了 `STATE.md` / `docs/` 就得用我们自己的话，否则等于把别人的视角当成事实。
- 远程变化引起的本地改动，本身也是本地改动：要记就记成"因为 #124 复核了 X"，让以后能追回来。

---

## 6. 坑与边界

1. **首次同步没有 cursor。** 不要猜。问用户"从什么时候开始"，或退到 `--since='7 days ago'`，并在摘要里标 `首次同步（范围不精确）`。
2. **rebase / force-push。** `--is-ancestor` 为假就换时间兜底（§2），别硬用 sha 区间。
3. **fork / 外部贡献者的 PR。** 作者不在组织内时额外标一句，可能牵扯许可或安全审查。
4. **大仓库。** 全部查询带 `--limit`；PR 多到列不完时只写数量和区间，细节按需展开。宁可摘要粗，不要一次拉几百个 PR 把自己撑爆。
5. **时区边界。** 全用带偏移的本地时间；`--since` / `>=` 的比较边界可能重叠或漏掉一两分钟，靠 sha 区间和摘要范围判重，别追求零误差。
6. **cursor 是每个 checkout 一份。** `./tmp/` 不进版本库，多 worktree / 多机器各同步各的，同一段范围可能被各记一次。这不冲突，但不自动对齐（同 `multi-agent.md` 的限制）。
7. **原始 JSON 不用存 `outputs/`。** 随手可重取；只有需要留证据（比如事后核对"当时确实合入了"）才落盘。
8. **同步失败不要留半截水位。** 顺序永远是：摘要落盘 → 再推 cursor。中途失败就停在旧水位，下次重算，最坏是重复，不是丢失；推 cursor 本身用「临时文件 + rename」，即使进程写一半被杀，留在盘上的也是完整旧水位，不是坏文件。

## 检查清单

- [ ] `git fetch --prune` 已执行，范围取的是**同步后**的 `origin/main`
- [ ] 摘要头部写了范围、抓取时间、是否降级
- [ ] 合入 / 关闭 / 未定三节按 `mergedAt` / `closedAt` / `updatedAt` 归类，没混
- [ ] `## 对我方的影响` 每条都指到了具体文件或 `STATE.md` 的具体条目
- [ ] cursor 在摘要**之后**才覆盖
- [ ] `journal/` 只加了一行指针
