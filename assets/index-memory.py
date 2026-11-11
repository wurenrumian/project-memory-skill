#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""index-memory — 生成 ./tmp/docs/index.md（近期活跃 tag + 全量文档）。

  python index-memory.py             # 写入 docs/index.md
  python index-memory.py --root DIR  # 指定 tmp 根

生成物不手改；检查工具会跳过它，避免它自己制造入链。
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime

from memory_lib import FOCUS_DAYS, analyze, default_root, docs_only, fmt_date, rel


def build_index(a) -> str:
    now = time.time()
    docs = docs_only(a.docs)
    by_tag = {}
    for d in docs:
        for t in d.tags:
            by_tag.setdefault(t, []).append(d)

    focus = []
    for tag, items in by_tag.items():
        recent = [d for d in items if (now - d.mtime) <= FOCUS_DAYS * 86400]
        if not recent:
            continue
        latest = max(d.mtime for d in recent)
        links = sum(a.inbound.get(d.path, 0) for d in recent)
        focus.append((tag, len(recent), latest, links))
    focus.sort(key=lambda x: (x[2], x[1]), reverse=True)

    groups = {}
    for d in docs:
        primary = d.tags[0] if d.tags else "未分类"
        groups.setdefault(primary, []).append(d)
    for items in groups.values():
        items.sort(key=lambda d: d.mtime, reverse=True)

    lines = [
        "# 索引",
        "",
        "> 生成文件，勿手改。重新生成：`python tmp/scripts/index-memory.py`",
        "",
        f"*生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        "",
        "## 正在关注（近 30 天有文件活动的 tag）",
        "",
        "> 启发式：按 mtime 推算，复制 / 解压 / checkout 都可能影响结果。",
        "",
    ]
    if focus:
        for tag, count, latest, links in focus:
            lines.append(f"- **{tag}** · {count} 篇 · 最近 {fmt_date(latest)} · 入链 {links}")
    else:
        lines.append("- （暂无）")
    lines += ["", "## 全部文档（按主 tag 分组）", ""]
    for tag in sorted(groups):
        lines.append(f"### {tag}")
        lines.append("")
        for d in groups[tag]:
            # 约定写法：从项目根看，路径以 ./tmp/ 开头；解析器两种都认。
            link = f"[{os.path.splitext(d.relpath)[0]}](./tmp/{d.relpath})"
            extra = f" · 入链 {a.inbound.get(d.path, 0)} · {fmt_date(d.mtime)}"
            lines.append(f"- {link} — {d.summary}{extra}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="index-memory：生成 docs/index.md")
    ap.add_argument("--root", default=None, help="tmp 根目录（默认脚本上级目录）")
    ap.add_argument("--no-cache", action="store_true", help="忽略增量缓存，强制全量解析")
    args = ap.parse_args(argv)

    root = args.root or default_root(__file__)
    if not os.path.isdir(root):
        print(f"不是目录：{root}", file=sys.stderr)
        return 2

    a = analyze(root, use_cache=not args.no_cache)
    target = os.path.join(root, "docs", "index.md")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(build_index(a))
    print(f"已生成 {rel(root, target)}（{len(docs_only(a.docs))} 篇）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
