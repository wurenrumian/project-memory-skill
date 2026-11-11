#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-memory — 检查 ./tmp 的链接、孤儿、tag 与整理阈值。

  python check-memory.py            # 全部检查：结构 / 引用 / 主题 / 整理
  python check-memory.py --json     # 机器可读
  python check-memory.py --limit 0  # 列表不截断
  python check-memory.py --root DIR # 指定 tmp 根（默认从当前目录往上找 ./tmp/）

结构问题（断链 / 歧义 / 重名）退出码 1；其余是信息报告。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from memory_lib import (
    ORPHAN_DAYS,
    TIDY_HARD,
    TIDY_JOURNAL_MONTHS,
    TIDY_MAX_LISTED,
    TIDY_SOFT,
    TOOLSET_VERSION,
    analyze,
    default_root,
    fmt_date,
    legacy_scripts,
    rel,
    tag_audit,
    tidy_status,
)


def report(a, limit: int = 40) -> str:
    out = []
    add = out.append
    add(f"check-memory · {a.root} · toolset {TOOLSET_VERSION}")
    stale = legacy_scripts(a.root)
    if stale:
        add(f"  注意：{rel(a.root, stale)} 是旧副本；工具现在直接从 skill 的 assets/ 跑，这个目录可以删掉")
    add("")

    add("结构")
    add(f"  断链 {len(a.broken)}")
    for src, target in a.broken[:limit]:
        add(f"    {a.docs[src].relpath} -> {target}")
    if len(a.broken) > limit:
        add(f"    … 其余 {len(a.broken) - limit} 条（--json 取全量）")
    add(f"  歧义链接 {len(a.ambiguous)}（裸 basename 命中多份）")
    for src, target, hits in a.ambiguous[:limit]:
        add(f"    {a.docs[src].relpath} -> [[{target}]]（{len(hits)} 个候选）")
    if len(a.ambiguous) > limit:
        add(f"    … 其余 {len(a.ambiguous) - limit} 条（--json 取全量）")
    add(f"  docs/ 重名 {len(a.duplicates)}")
    for stem, paths in sorted(a.duplicates.items())[:limit]:
        add(f"    {stem}: {', '.join(paths)}")
    if len(a.duplicates) > limit:
        add(f"    … 其余 {len(a.duplicates) - limit} 组（--json 取全量）")

    add("")
    add("引用")
    add(f"  孤儿 {len(a.orphans)}（入链 0 · 超过 {ORPHAN_DAYS} 天，仅复核线索）")
    for d in a.orphans[:limit]:
        add(f"    {d.relpath}  {fmt_date(d.mtime)}")
    if len(a.orphans) > limit:
        add(f"    … 其余 {len(a.orphans) - limit} 条（--json 取全量）")

    add("")
    add("主题")
    add(f"  无 tag 文档 {len(a.untagged)}")
    for d in a.untagged[:limit]:
        add(f"    {d.relpath}")
    if len(a.untagged) > limit:
        add(f"    … 其余 {len(a.untagged) - limit} 条（--json 取全量）")
    summary = ", ".join(
        f"{t}({len(v)})" for t, v in sorted(a.tags.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    )
    add(f"  tag {len(a.tags)} 个：{summary or '（无）'}")

    bad_format, too_many, variants = tag_audit(a.docs)
    if bad_format or too_many or variants:
        add("  tag 规范")
        for path, tag in bad_format[:limit]:
            add(f"    {path}：`{tag}` 不是小写 kebab-case")
        for d in too_many[:limit]:
            add(f"    {d.relpath}：{len(d.tags)} 个 tag（建议 1~3 个）")
        for _stem, tags in sorted(variants.items())[:limit]:
            add(f"    疑似同义变体：{' / '.join(tags)}（优先复用同一个）")

    rows, months = tidy_status(a.root)
    add("")
    add("整理")
    hot = [(name, n) for name, n in rows if n >= TIDY_SOFT]
    for name, n in hot[:limit]:
        level = "硬阈值" if n >= TIDY_HARD else "软阈值"
        add(f"    {name} {n} 项（≥{TIDY_HARD if n >= TIDY_HARD else TIDY_SOFT} {level}）")
    if len(hot) > limit:
        add(f"    … 其余 {len(hot) - limit} 个目录")
    add(f"    journal 活跃月份 {len(months)}（阈值 >{TIDY_JOURNAL_MONTHS}）")
    if hot or len(months) > TIDY_JOURNAL_MONTHS:
        add("    → 建议整理一轮（流程见 SKILL「整理与滚动归档」）")
    else:
        largest = rows[0] if rows else ("—", 0)
        add(f"    → 未触发（最大 {largest[0]} {largest[1]} 项）")

    add("")
    structural = len(a.broken) + len(a.ambiguous) + len(a.duplicates)
    add(f"结论：结构问题 {structural} 处" + ("（退出码 1）" if structural else "，无断链"))
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="check-memory：检查链接、孤儿、tag 与整理阈值")
    ap.add_argument("--root", default=None, help="tmp 根目录（默认从当前目录往上找 ./tmp/）")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--no-cache", action="store_true", help="忽略增量缓存，强制全量解析")
    ap.add_argument(
        "--limit",
        type=int,
        default=TIDY_MAX_LISTED,
        help=f"每类最多列多少条（默认 {TIDY_MAX_LISTED}，0 表示不截断）",
    )
    args = ap.parse_args(argv)

    root = args.root or default_root(__file__)
    if not os.path.isdir(root):
        print(f"不是目录：{root}（未传 --root 时，脚本从当前目录往上找带 STATE.md / docs/ 的 ./tmp/）", file=sys.stderr)
        return 2

    a = analyze(root, use_cache=not args.no_cache)
    failed = bool(a.broken or a.ambiguous or a.duplicates)
    limit = args.limit if args.limit > 0 else 10**9

    if args.json:
        bad_format, too_many, variants = tag_audit(a.docs)
        rows, months = tidy_status(root)
        payload = {
            "root": rel(os.getcwd(), root) if root.startswith(os.getcwd()) else root,
            "toolset": TOOLSET_VERSION,
            "legacyScripts": bool(legacy_scripts(root)),
            "broken": [{"source": a.docs[s].relpath, "target": t} for s, t in a.broken],
            "ambiguous": [
                {"source": a.docs[s].relpath, "target": t, "candidates": h}
                for s, t, h in a.ambiguous
            ],
            "duplicates": a.duplicates,
            "orphans": [{"path": d.relpath, "mtime": fmt_date(d.mtime)} for d in a.orphans],
            "untagged": [d.relpath for d in a.untagged],
            "tags": {t: len(v) for t, v in sorted(a.tags.items())},
            "tagIssues": {
                "badFormat": [{"path": p, "tag": t} for p, t in bad_format],
                "tooMany": [{"path": d.relpath, "count": len(d.tags)} for d in too_many],
                "variants": variants,
            },
            "tidy": {
                "dirs": [{"path": n, "entries": c} for n, c in rows],
                "journalMonths": len(months),
                "suggested": bool(any(c >= TIDY_SOFT for _, c in rows))
                or len(months) > TIDY_JOURNAL_MONTHS,
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(report(a, limit=limit))

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
