#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""工具集性能基准：造一个合成 tmp/，测四个命令的耗时。

  python tests/bench.py                # 默认 2000 篇
  python tests/bench.py --docs 10000   # 大规模
  python tests/bench.py --repeat 3     # 取中位数（更稳，也更慢）

不参与 run_tests.py：它只验证行为，不验证速度，跑一次要读上千个文件。
首跑含建缓存；缓存命中的数字才是日常开销。
"""

from __future__ import annotations

import argparse
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")

CHECK = os.path.join(ASSETS, "check-memory.py")
FIND = os.path.join(ASSETS, "find-memory.py")
INDEX = os.path.join(ASSETS, "index-memory.py")
INDEX_EXP = os.path.join(ASSETS, "index-experiments.py")

TOPICS = 20


def build(root: str, n: int) -> None:
    topics = [f"topic-{i}" for i in range(TOPICS)]
    for i in range(n):
        topic = topics[i % TOPICS]
        d = os.path.join(root, "docs", topic)
        os.makedirs(d, exist_ok=True)
        j = (i * 7) % n
        other = topics[j % TOPICS]
        with open(os.path.join(d, f"note-{i}.md"), "w", encoding="utf-8") as fh:
            fh.write(
                "---\n"
                f"tags: [{topic}, shared]\n"
                "---\n\n"
                f"# 笔记 {i}\n\n"
                f"第 {i} 篇笔记的正文首句，模拟真实文档的摘要长度。\n\n"
                f"见 [[docs/{other}/note-{j}]] 与 [邻居](../{other}/note-{j}.md#笔记)。\n"
            )

    os.makedirs(os.path.join(root, "journal"), exist_ok=True)
    for month in (1, 2, 3):
        with open(os.path.join(root, "journal", f"2026-{month:02d}-01.md"), "w", encoding="utf-8") as fh:
            fh.write("- 09:00 记录一行\n")

    for exp in range(20):
        d = os.path.join(root, "experiments", f"EXP-{exp + 1:04d}-bench")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as fh:
            fh.write(f"# EXP-{exp + 1:04d}\n\n## 状态\n\ndoing\n\n## 问题\n\n基准问题。\n\n## 结论\n\n尚未定论。\n")

    with open(os.path.join(root, "STATE.md"), "w", encoding="utf-8") as fh:
        fh.write("# STATE\n\n## 关键链接\n\n- [[docs/topic-0/note-0]]\n")


def run(script: str, root: str, *args: str) -> float:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    start = time.perf_counter()
    subprocess.run(
        [sys.executable, script, "--root", root, *args],
        capture_output=True,
        env=env,
    )
    return (time.perf_counter() - start) * 1000


def timed(label: str, script: str, root: str, repeat: int, *args: str) -> None:
    samples = [run(script, root, *args) for _ in range(repeat)]
    value = statistics.median(samples) if repeat > 1 else samples[0]
    print(f"  {label:<28} {value:8.0f} ms")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="工具集性能基准")
    ap.add_argument("--docs", type=int, default=2000, help="文档数（默认 2000）")
    ap.add_argument("--repeat", type=int, default=2, help="每项跑几次取中位数（默认 2）")
    ap.add_argument("--keep", action="store_true", help="保留合成目录，便于手动排查")
    args = ap.parse_args(argv)

    work = tempfile.mkdtemp(prefix="memory-bench-")
    root = os.path.join(work, "tmp")
    try:
        print(f"生成 {args.docs} 篇文档…", flush=True)
        build(root, args.docs)

        print(f"\n首跑（含建缓存，受杀软 / 首次读盘影响）：")
        first = run(CHECK, root)
        print(f"  {'check':<28} {first:8.0f} ms")

        print(f"\n缓存命中（日常开销，每项 {args.repeat} 次取中位数）：")
        timed("check", CHECK, root, args.repeat)
        timed("find --tag", FIND, root, args.repeat, "--tag", "topic-3")
        timed("find --untagged", FIND, root, args.repeat, "--untagged")
        timed("find --orphans", FIND, root, args.repeat, "--orphans")
        timed("index docs", INDEX, root, args.repeat)
        timed("index experiments", INDEX_EXP, root, args.repeat)

        cache = os.path.join(root, ".memory-cache.json")
        if os.path.isfile(cache):
            print(f"\n缓存体积 {os.path.getsize(cache) / 1048576:.2f} MB")
    finally:
        if args.keep:
            print(f"\n保留：{root}")
        else:
            shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
