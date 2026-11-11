#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-memory 工具集的回归测试。

用法：python tests/run_tests.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
FIXTURE = os.path.join(HERE, "tmp")
ASSETS = os.path.join(SKILL, "assets")

CHECK = os.path.join(ASSETS, "check-memory.py")
FIND = os.path.join(ASSETS, "find-memory.py")
INDEX = os.path.join(ASSETS, "index-memory.py")
INDEX_EXP = os.path.join(ASSETS, "index-experiments.py")

results = []


def run(script, root, *args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, script, "--root", root, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )


def check(name, cond, detail=""):
    results.append(bool(cond))
    print(("PASS" if cond else "FAIL"), name)
    if not cond and detail:
        print("     ", detail.replace("\n", "\n      "))


def main():
    work = tempfile.mkdtemp(prefix="check-memory-test-")
    try:
        vault = os.path.join(work, "tmp")
        shutil.copytree(FIXTURE, vault)
        # git 不保留 mtime，孤儿的时间由运行器模拟。
        old = os.path.join(vault, "docs", "research", "forgotten-idea.md")
        past = time.time() - 40 * 86400
        os.utime(old, (past, past))

        r = run(CHECK, vault)
        out = r.stdout

        check("check：退出码为 1", r.returncode == 1, f"exit={r.returncode}")
        check("check：检出断链 missing-note", "missing-note" in out, out)
        check("check：检出歧义链接 [[notes]]", "歧义链接 1" in out, out)
        check("check：检出 docs/ 重名 notes", "notes:" in out, out)
        check("check：孤儿包含 forgotten-idea", "forgotten-idea.md" in out, out)
        check("check：代码块里的 [[also-not-a-link]] 不算断链", "also-not-a-link" not in out, out)

        # 锚点 / 目录 / 大小写：合法的链接形态不应该被误报成断链。
        check(
            "check：带锚点的链接不算断链",
            "#延迟笔记" not in out,
            out,
        )
        check("check：指目录的链接不算断链", "../research/" not in out, out)
        if sys.platform in ("win32", "darwin"):
            check("check：大小写不一致的 wiki 链接能解析", "Cache-Shard" not in out, out)

        # 只追加的历史目录：断链修不了，报出来只会训练人忽略报告。
        check("check：journal 里的断链不报", "journal-broken" not in out, out)
        check("check：归档文档的断链不报", "旧链接" not in out, out)

        check("check：tidy 阈值未触发", "未触发" in out, out)
        check("check：输出整理小节", "整理" in out and "journal 活跃月份 1" in out, out)

        r = run(CHECK, vault, "--limit", "1")
        check(
            "check --limit 截断长列表",
            "其余" in r.stdout and "（--json 取全量）" in r.stdout,
            r.stdout,
        )

        r = run(FIND, vault, "--tag", "bomtest")
        check("BOM 文件的 tag 可查", "bom-tags.md" in r.stdout, r.stdout)

        r = run(FIND, vault, "--tag", "storage")
        check(
            "find --tag 只返回 cache-shard",
            r.stdout.strip() == "docs/memory/cache-shard.md",
            r.stdout,
        )

        r = run(FIND, vault, "--untagged")
        lines = r.stdout.splitlines()
        check("find --untagged 包含 latency-notes", "docs/research/latency-notes.md" in lines)
        check(
            "find --untagged 包含两个 notes",
            sum(1 for x in lines if x.endswith("/notes.md")) == 2,
            r.stdout,
        )

        r = run(FIND, vault, "--orphans")
        lines = r.stdout.splitlines()
        check("find --orphans 包含 forgotten-idea", any("forgotten-idea" in x for x in lines), r.stdout)
        check("find --orphans 不包含被引用的 old-roadmap", not any("old-roadmap" in x for x in lines), r.stdout)

        r = run(CHECK, vault, "--json")
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError as exc:
            data = {}
            check("check --json 可解析", False, f"{exc}\n{r.stdout}")
        else:
            check("check --json 可解析", True)
        check("JSON 记录断链", any(b["target"] == "missing-note" for b in data.get("broken", [])))
        check("JSON 记录孤儿", any("forgotten-idea" in o["path"] for o in data.get("orphans", [])))
        check("JSON 记录重名", "notes" in data.get("duplicates", {}))
        check("JSON 记录 tag", "storage" in data.get("tags", {}))
        check(
            "JSON 记录 tag 规范与整理",
            bool(data.get("tagIssues", {}).get("variants"))
            and "dirs" in data.get("tidy", {}),
            json.dumps(data.get("tagIssues"), ensure_ascii=False),
        )

        cache = os.path.join(vault, ".memory-cache.json")
        check("增量缓存已生成", os.path.isfile(cache))

        shard = os.path.join(vault, "docs", "memory", "cache-shard.md")
        text = open(shard, encoding="utf-8").read().replace(
            "tags: [storage, cache]", "tags: [storage, cache, newtag]"
        )
        with open(shard, "w", encoding="utf-8") as fh:
            fh.write(text)
        r = run(FIND, vault, "--tag", "newtag")
        check("缓存感知 tag 变化", "cache-shard" in r.stdout, r.stdout)

        os.remove(os.path.join(vault, "docs", "plans", "link-check.md"))
        r = run(CHECK, vault)
        check("缓存感知文件删除", "歧义链接 0" in r.stdout, r.stdout)

        r = run(CHECK, vault, "--no-cache")
        check("--no-cache 可用", r.returncode == 1, r.stdout + r.stderr)

        r = run(INDEX, vault)
        index = os.path.join(vault, "docs", "index.md")
        text = open(index, encoding="utf-8").read() if os.path.isfile(index) else ""
        check("index：退出码为 0", r.returncode == 0, r.stdout + r.stderr)
        check("index：含关注面", "正在关注" in text and "**storage**" in text, text)
        check("index：含全量分组", "### storage" in text, text)

        r = run(INDEX_EXP, vault)
        exp_index = os.path.join(vault, "experiments", "INDEX.md")
        exp_text = open(exp_index, encoding="utf-8").read() if os.path.isfile(exp_index) else ""
        check("experiments index：退出码为 0", r.returncode == 0, r.stdout + r.stderr)
        check("experiments index：含 EXP-0001 与结论", "EXP-0001" in exp_text and "线性增长" in exp_text, exp_text)
        check("experiments index：含 EXP-0002 状态", "EXP-0002" in exp_text and "doing" in exp_text, exp_text)
        check("experiments index：归档实验标 archived", "EXP-0003" in exp_text and "archived" in exp_text, exp_text)
        check(
            "experiments index：按 ID 排序",
            exp_text.find("EXP-0001") < exp_text.find("EXP-0002") < exp_text.find("EXP-0003"),
            exp_text,
        )

        # 生成的两个索引都不参与检查，避免它们自己制造入链或误报。
        r = run(CHECK, vault)
        check("生成索引不出现在检查报告里", "INDEX.md" not in r.stdout, r.stdout)

        # 回归：生成索引不能把每篇文档都变成“有入链”，否则孤儿永远查不出来。
        r = run(FIND, vault, "--orphans")
        check("生成 index 后孤儿仍在", "forgotten-idea" in r.stdout, r.stdout)

        r = run(FIND, vault, "--untagged")
        check("生成的 docs/index.md 不计入无 tag", "docs/index.md" not in r.stdout, r.stdout)

        # 整理阈值：条目数到硬阈值时必须提示，否则 SKILL 里的规则没人会去数。
        for i in range(20):
            with open(os.path.join(vault, "docs", "plans", f"bulk-{i:02d}.md"), "w", encoding="utf-8") as fh:
                fh.write(f"---\ntags: [plan]\n---\n\n# 批量样本 {i}\n")
        r = run(CHECK, vault)
        check(
            "check：目录过阈值时提示整理",
            "建议整理一轮" in r.stdout and "硬阈值" in r.stdout,
            r.stdout,
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)

    failed = results.count(False)
    print()
    print(f"{len(results) - failed}/{len(results)} 通过")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
