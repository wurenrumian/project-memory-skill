# 产物元数据（可选）

`outputs/` 内部不设约定，产物要不要自带来源由程序决定。若希望产物能自证出处，可让程序自己写一份：

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
