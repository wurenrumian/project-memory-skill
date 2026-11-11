#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""index-experiments — 生成 experiments/INDEX.md（实验状态 / 问题 / 结论）。

  python index-experiments.py             # 写入 experiments/INDEX.md
  python index-experiments.py --root DIR  # 指定 tmp 根

数据来自每个实验 README 的固定小节（状态 / 问题 / 结论），不新增 metadata。
归档的实验（archive/EXP-*）也会列出，状态标 archived。
"""

from __future__ import annotations

import argparse
import os
import re
import sys

from memory_lib import default_root, fmt_date, read_text, rel

EXP_RE = re.compile(r"^EXP-(\d{4})-(.+)$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


def sections(text: str):
    parts = SECTION_RE.split(text)
    out = {}
    for i in range(1, len(parts) - 1, 2):
        out[parts[i].strip()] = parts[i + 1]
    return out


def first_line(body: str) -> str:
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        s = re.sub(r"^[-*]\s+", "", s)
        s = re.sub(r"[*_`]", "", s)
        return s.replace("|", "\\|")[:60]
    return ""


def collect(root: str):
    rows = []
    for base, archived in (
        (os.path.join(root, "experiments"), False),
        (os.path.join(root, "archive"), True),
    ):
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            d = os.path.join(base, name)
            if not os.path.isdir(d) or not EXP_RE.match(name):
                continue
            readme = os.path.join(d, "README.md")
            if not os.path.isfile(readme):
                continue
            sec = sections(read_text(readme))
            exp_id = name.split("-", 2)[0] + "-" + name.split("-", 2)[1]
            status = "archived" if archived else (first_line(sec.get("状态", "")) or "—")
            question = first_line(sec.get("问题", "")) or "—"
            conclusion = first_line(sec.get("结论", "")) or "—"
            link = os.path.splitext(rel(root, readme))[0]
            rows.append((exp_id, name, link, status, question, conclusion, os.path.getmtime(readme)))
    rows.sort(key=lambda r: (int(r[0].split("-")[1]), r[1]))
    return rows


def build(root: str, rows) -> str:
    lines = [
        "# 实验索引",
        "",
        "> 生成文件，勿手改。重新生成：`python tmp/scripts/index-experiments.py`",
        "",
        "| ID | 状态 | 问题 | 结论 | 最后更新 |",
        "|---|---|---|---|---|",
    ]
    if rows:
        for exp_id, name, link, status, question, conclusion, mtime in rows:
            # 与文档链接同一约定：Markdown 链接、路径 ./tmp/ 开头。
            lines.append(
                f"| [{exp_id}](./tmp/{link}.md) | {status} | {question} | {conclusion} | {fmt_date(mtime)} |"
            )
    else:
        lines.append("| — | — | — | — | — |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="index-experiments：生成 experiments/INDEX.md")
    ap.add_argument("--root", default=None, help="tmp 根目录（默认脚本上级目录）")
    args = ap.parse_args(argv)

    root = args.root or default_root(__file__)
    if not os.path.isdir(root):
        print(f"不是目录：{root}", file=sys.stderr)
        return 2

    rows = collect(root)
    target = os.path.join(root, "experiments", "INDEX.md")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(build(root, rows))
    print(f"已生成 {rel(root, target)}（{len(rows)} 个实验）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
