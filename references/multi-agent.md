# 多 agent 协作

多个 agent **同时**在同一个项目里干活才启用；单 agent 时整个 `agents/` 目录不存在。根 `STATE.md` 仍是唯一入口，全局视角不碎成 N 份。本节与主文件的默认流程冲突时，以本节为准：工作期间的状态只进 BOARD 与自己的子目录，全局文件只在收尾写回。（若各 agent 在各自的 git worktree 里，`./tmp/` 互不共享，本节约定不适用。）

```
./tmp/agents/
├── BOARD.md           # 共享任务板：任务 / 认领人 / 状态 / 产物链接
└── <agent-id>/        # 每个 agent 一份（id 认法见规则 1）
    ├── STATE.md       # 该 agent 自己的现状 / 下一步
    └── journal/       # 该 agent 自己的时间线，一天一个文件（约定同全局 journal）
        └── 2026-10-12.md
```

`BOARD.md` 一行一条（任务或文件占用都算）：

| 任务 / 占用 | 认领人 | 状态 | 产物 / 备注 |
|---|---|---|---|
| EXP-0003 结果分析 | claude-1 | 进行中 | outputs/exp-0003/ |
| 编辑 `docs/memory/缓存策略.md` | codex-2 | 占用中 | 完成即释放 |

规则：

1. **先认 id，再认任务。** agent-id 优先用用户或环境指定的名字；同名 agent 多会话并发时加序号（`claude-1`、`claude-2`）。建目录前先扫 `agents/`，不撞名。
2. **认领即锁。** 接任务，或要动 `docs/`、`experiments/` 等共享区的某个文件，先往 `BOARD.md` 加/改一行登记；完成的行标 `done`，别人的行不动。
3. **只写自己的地盘。** 每个 agent 只写自己的 `agents/<agent-id>/` 和 BOARD 里自己那几行；根 `STATE.md` 和全局 `journal/` 工作期间不动。
4. **收尾写回全局。** 会话收尾时，把"值得全局知道"的一句话写进根 `STATE.md`（现在/进行中/下一步），细节留在自己子目录。
5. **BOARD 只放状态和链接**，不放任务详情——详情放任务自己的文档或 journal，BOARD 一行链过去。
