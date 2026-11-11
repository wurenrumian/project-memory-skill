#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""find-memory — 按 tag / 无 tag / 孤儿查找 ./tmp 里的文档路径。

  python find-memory.py --tag storage        # 按 tag 找路径（可重复，多个为 AND）
  python find-memory.py --untagged           # 没有 tag 的文档
  python find-memory.py --orphans            # 孤儿（入链 0 且超过 30 天）
  python find-memory.py --root DIR ...       # 指定 tmp 根

只输出路径，方便管道给编辑器或 rg。
"""

from __future__ import annotations

import argparse
import os
import sys

from memory_lib import analyze, default_root, fmt_date


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="find-memory：按 tag / 无 tag / 孤儿查找文档")
    ap.add_argument("--root", default=None, help="tmp 根目录（默认从当前目录往上找 ./tmp/）")
    ap.add_argument("--no-cache", action="store_true", help="忽略增量缓存，强制全量解析")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--tag", action="append", help="按 tag 列路径，可重复（多个为 AND）")
    mode.add_argument("--untagged", action="store_true", help="列出没有 tag 的文档")
    mode.add_argument("--orphans", action="store_true", help="列出孤儿")
    args = ap.parse_args(argv)

    root = args.root or default_root(__file__)
    if not os.path.isdir(root):
        print(f"不是目录：{root}（未传 --root 时，脚本从当前目录往上找带 STATE.md / docs/ 的 ./tmp/）", file=sys.stderr)
        return 2

    a = analyze(root, use_cache=not args.no_cache, resolve=bool(args.orphans))

    if args.tag:
        wanted = [t.lower() for t in args.tag]
        hits = [
            d for d in a.docs.values()
            if all(t.lower() in {x.lower() for x in d.tags} for t in wanted)
        ]
        hits.sort(key=lambda d: d.relpath)
        for d in hits:
            print(d.relpath)
    elif args.untagged:
        for d in a.untagged:
            print(d.relpath)
    else:
        for d in a.orphans:
            print(f"{d.relpath}\t{fmt_date(d.mtime)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
