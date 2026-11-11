# 产物元数据（可选）

> 主文件：`../SKILL.md`；本文件只是 sidecar 字段样例。

`outputs/` 内部不设约定，产物要不要自带来源由程序决定。若希望产物能自证出处，可让程序写一份 sidecar（建议 `<产物名>.meta.json`，与产物同目录，程序写、人不用手填；字段可裁剪，不要求全量）：

```json
{
  "experiment": "EXP-0001",
  "command": "python scripts/run.py --config config.yaml",
  "started_at": "2026-09-27T15:30:12+08:00",
  "duration_s": 123.4,
  "git": { "rev": "abc1234", "dirty": true },
  "inputs": ["config.yaml"],
  "artifacts": [{ "path": "metrics.csv", "bytes": 2048 }],
  "status": "ok"
}
```

`status` 建议记 `ok | failed | interrupted`——失败 / 中断的产物同样值得留。
