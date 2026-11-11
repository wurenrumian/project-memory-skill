#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check-memory 工具集的共享逻辑：扫描、解析、链接解析、统计、增量缓存。

只被同目录的 check-memory.py / find-memory.py / index-memory.py / index-experiments.py 导入，不直接运行。
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import unquote

ORPHAN_DAYS = 30
FOCUS_DAYS = 30
ACTIVE_DIRS = ("docs", "experiments", "annotated")
SKIP_DIRS = {"outputs", ".git", ".obsidian", "node_modules", "__pycache__"}
# 生成文件不参与检查：否则它列出的每条链接都会变成入链，孤儿永远不会被报出来。
EXCLUDE_FILES = {"docs/index.md", "experiments/INDEX.md", "archive/INDEX.md"}

# 整理阈值（SKILL「整理与滚动归档」）：目录条目数、journal 活跃月份。
TIDY_SOFT = 16
TIDY_HARD = 20
TIDY_JOURNAL_MONTHS = 2
TIDY_WATCH = (
    "experiments",
    "annotated",
    "scripts",
)
TIDY_MAX_LISTED = 40

CACHE_FILE = ".memory-cache.json"
CACHE_VERSION = 2  # 解析逻辑 / 缓存字段变了就 +1，旧缓存自动失效
TOOLSET_VERSION = 1  # tmp/scripts/ 里的副本可能比 skill 旧；check 首行会打印

CASE_INSENSITIVE = os.name == "nt" or sys.platform == "darwin"

FENCE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
WIKI_RE = re.compile(r"\[\[([^\[\]\n]+?)\]\]")
MD_RE = re.compile(r"!?\[[^\]\n]*\]\(\s*([^)\s]+)(?:\s+[^)]*)?\)")
TAG_LINE_RE = re.compile(r"^\s*tags\s*:\s*(.*)$")
LIST_ITEM_RE = re.compile(r"^\s*-\s+")

SCHEMES = ("http://", "https://", "mailto:", "obsidian:", "file:", "#")


def norm(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def default_root(script_file: str) -> str:
    """脚本位于 tmp/scripts/，默认根就是 tmp/。"""
    return norm(os.path.dirname(os.path.dirname(os.path.abspath(script_file))))


def rel(root: str, path: str) -> str:
    return os.path.relpath(path, root).replace(os.sep, "/")


def walk_md(root: str):
    """一次遍历，返回 (绝对路径, 相对路径, stat)。

    用 os.scandir 的目录项缓存拿 stat，避免再对每个文件调用 os.stat。
    """
    prefix = root.rstrip(os.sep) + os.sep
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            entries = os.scandir(d)
        except OSError:
            continue
        with entries:
            for e in sorted(entries, key=lambda x: x.name):
                try:
                    if e.is_dir(follow_symlinks=False):
                        if e.name not in SKIP_DIRS:
                            stack.append(e.path)
                        continue
                    if not e.name.endswith(".md") or not e.is_file(follow_symlinks=False):
                        continue
                    full = os.path.normpath(e.path)
                    rp = (
                        full[len(prefix):].replace(os.sep, "/")
                        if full.startswith(prefix)
                        else rel(root, full)
                    )
                    if rp in EXCLUDE_FILES:
                        continue
                    yield full, rp, e.stat(follow_symlinks=False)
                except OSError:
                    continue


def read_text(path: str) -> str:
    # utf-8-sig：Windows 编辑器常写 BOM，用 utf-8 读会让首行变成 \ufeff---，front-matter 直接失效。
    try:
        with open(path, "r", encoding="utf-8-sig", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def parse_tags(front: str):
    tags = []
    lines = front.splitlines()
    i = 0
    while i < len(lines):
        m = TAG_LINE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        rest = m.group(1).strip()
        if rest.startswith("["):
            for part in rest.strip("[]").split(","):
                t = part.strip().strip("'\"")
                if t:
                    tags.append(t)
        elif rest:
            for part in re.split(r"[,\s]+", rest):
                t = part.strip().strip("'\"")
                if t:
                    tags.append(t)
        else:
            i += 1
            while i < len(lines) and LIST_ITEM_RE.match(lines[i]):
                t = lines[i].split("-", 1)[1].strip().strip("'\"")
                if t:
                    tags.append(t)
                i += 1
            continue
        i += 1
    return tags


def first_sentence(body: str) -> str:
    body = FENCE_RE.sub("", body)
    picked = []
    for line in body.splitlines():
        s = line.strip()
        if not s:
            if picked:
                break
            continue
        if s.startswith("#"):
            if picked:
                break
            continue
        picked.append(s)
        if sum(len(x) for x in picked) > 160:
            break
    text = " ".join(picked)
    text = re.sub(r"\[\[([^\]\|]+)(?:\|[^\]]*)?\]\]", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`>#]+", "", text).strip()
    m = re.match(r"^(.{8,120}?[。.!?！？；;])", text)
    return (m.group(1) if m else text[:80]).strip()


def parse_file(path: str, active: bool):
    """解析一个文件，返回可进缓存的原始数据。

    非活目录（journal / remote / archive / scratch）的内容只作为“链接目标”存在：
    它们是只追加、不回头整理的，断链修不了，tag 也不进统计——所以干脆不读盘。
    """
    if not active:
        return {"tags": [], "links": [], "summary": ""}

    text = read_text(path)
    fm = FM_RE.match(text)
    front = fm.group(1) if fm else ""
    body = text[fm.end():] if fm else text
    clean = FENCE_RE.sub("", body)
    clean = INLINE_CODE_RE.sub("", clean)
    links = [["wiki", m.group(1).strip()] for m in WIKI_RE.finditer(clean)]
    links += [["md", m.group(1).strip()] for m in MD_RE.finditer(clean)]
    links = [x for x in links if x[1] and not x[1].lower().startswith(SCHEMES)]
    return {
        "tags": parse_tags(front),
        "links": links,
        "summary": first_sentence(body),
    }


class Doc:
    __slots__ = ("path", "relpath", "active", "tags", "raw_links", "mtime", "summary")

    def __init__(self, path, relpath, active, tags, raw_links, mtime, summary):
        self.path = path
        self.relpath = relpath
        self.active = active
        self.tags = tags
        self.raw_links = raw_links
        self.mtime = mtime
        self.summary = summary


def cache_path(root: str) -> str:
    return os.path.join(root, CACHE_FILE)


def load_cache(root: str):
    try:
        with open(cache_path(root), "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("version") != CACHE_VERSION:
        return {}
    files = data.get("files")
    return files if isinstance(files, dict) else {}


def save_cache(root: str, files) -> None:
    """原子写：临时文件 + rename，避免并发 / 中断留下半截 JSON。

    临时文件名带 pid：多个 agent 同时跑检查时不会互相截断。
    """
    path = cache_path(root)
    tmp = f"{path}.{os.getpid()}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"version": CACHE_VERSION, "files": files}, fh, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def scan(root: str, use_cache: bool = True):
    """遍历 + 解析；命中缓存的文件不重新读盘。返回 (docs, changed)。"""
    cache = load_cache(root) if use_cache else {}
    files = {}
    docs = {}
    changed = False

    for p, rp, st in walk_md(root):
        top = rp.split("/", 1)[0] if "/" in rp else rp
        active = rp == "STATE.md" or top in ACTIVE_DIRS

        ent = cache.get(rp)
        if (
            use_cache
            and isinstance(ent, dict)
            and ent.get("mtime_ns") == st.st_mtime_ns
            and ent.get("size") == st.st_size
            # 移动会保留 mtime，但会让“活 / 非活”翻转，解析结果随之不同。
            and ent.get("active") == active
            and "tags" in ent
            and "links" in ent
        ):
            data = ent
            files[rp] = ent
        else:
            parsed = parse_file(p, active)
            data = {
                "mtime_ns": st.st_mtime_ns,
                "size": st.st_size,
                "active": active,
                "tags": parsed["tags"],
                "links": parsed["links"],
                "summary": parsed["summary"],
            }
            files[rp] = data
            changed = True

        docs[p] = Doc(
            p,
            rp,
            active,
            data.get("tags", []),
            [tuple(x) for x in data.get("links", [])],
            st.st_mtime,
            data.get("summary", ""),
        )

    if use_cache and (changed or len(files) != len(cache)):
        save_cache(root, files)

    return docs, changed


def resolve_all(root: str, docs):
    """返回 (broken, ambiguous, inbound)。全部用字典，避免 O(n²)。"""
    stem_map = {}
    for p, d in docs.items():
        stem = os.path.splitext(os.path.basename(d.relpath))[0]
        stem_map.setdefault(stem, []).append(p)
    # Windows / macOS 文件系统不区分大小写，Obsidian 默认也不区分；Linux 上保持严格。
    stem_lower = {}
    if CASE_INSENSITIVE:
        for stem, paths in stem_map.items():
            stem_lower[stem.lower()] = paths

    broken, ambiguous = [], []
    inbound = {p: 0 for p in docs}

    for src, doc in docs.items():
        for kind, target in doc.raw_links:
            target = target.strip()

            if kind == "wiki":
                t = target.split("|", 1)[0].split("#", 1)[0].strip().lstrip("/")
                if not t:
                    continue
                has_ext = bool(os.path.splitext(t)[1])
                if "/" in t or has_ext:
                    cand = os.path.normpath(os.path.join(root, t if has_ext else t + ".md"))
                    if cand in docs or os.path.isfile(cand) or os.path.isdir(cand):
                        if cand in inbound and doc.active:
                            inbound[cand] += 1
                        continue
                    if "/" in t and not has_ext:
                        cand2 = os.path.normpath(os.path.join(root, t))
                        if cand2 in docs or os.path.isdir(cand2):
                            if doc.active:
                                inbound[cand2] += 1
                            continue
                    broken.append((src, target))
                    continue
                hits = stem_map.get(t, [])
                if not hits and CASE_INSENSITIVE:
                    hits = stem_lower.get(t.lower(), [])
                if len(hits) == 1:
                    if doc.active:
                        inbound[hits[0]] += 1
                elif len(hits) > 1:
                    ambiguous.append((src, target, [docs[h].relpath for h in hits]))
                else:
                    broken.append((src, target))
            else:
                if target.startswith("<") and target.endswith(">"):
                    target = target[1:-1]
                # `[x](note.md#小节)` / `[x](note.md?x=1)`：锚点不是路径的一部分。
                path_part = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not path_part:
                    continue
                cand = os.path.normpath(os.path.join(os.path.dirname(src), path_part))
                # 先查字典：链接到的 md 文档本来就在 docs 里，不必再问一次文件系统。
                if cand not in docs and not os.path.exists(cand):
                    alt = os.path.normpath(os.path.join(root, path_part))
                    cand = alt if (alt in docs or os.path.exists(alt)) else ""
                if not cand:
                    broken.append((src, target))
                elif cand in inbound and doc.active:
                    inbound[cand] += 1

    return broken, ambiguous, inbound


def duplicate_stems(docs):
    """只关心 docs/ 内的重名；实验目录的 README 靠路径寻址，不算问题。"""
    seen = {}
    for d in docs.values():
        if d.relpath.startswith("docs/"):
            stem = os.path.splitext(os.path.basename(d.relpath))[0]
            seen.setdefault(stem, []).append(d.relpath)
    return {k: v for k, v in seen.items() if len(v) > 1}


def orphan_list(docs, inbound):
    now = time.time()
    result = []
    for d in docs.values():
        if not d.relpath.startswith("docs/"):
            continue
        if inbound.get(d.path, 0) > 0:
            continue
        if (now - d.mtime) > ORPHAN_DAYS * 86400:
            result.append(d)
    result.sort(key=lambda d: d.mtime)
    return result


def untagged_list(docs):
    return sorted(
        (d for d in docs.values() if d.relpath.startswith("docs/") and not d.tags),
        key=lambda d: d.relpath,
    )


def tag_map(docs):
    tags = {}
    for d in docs.values():
        top = d.relpath.split("/", 1)[0] if "/" in d.relpath else ""
        if top not in ACTIVE_DIRS:
            continue
        for t in d.tags:
            tags.setdefault(t, []).append(d)
    return tags


def docs_only(docs):
    return [d for d in docs.values() if d.relpath.startswith("docs/")]


TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _tag_stem(tag: str) -> str:
    """把 cache / caching / caches 归到同一个词干，用来提示同义变体。"""
    s = re.sub(r"[-_.\s]", "", tag.lower())
    for suffix in ("ing", "ed", "es", "s"):
        if len(s) > 4 and s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    return s[:-1] if len(s) > 4 and s.endswith("e") else s


def tag_audit(docs):
    """tag 规范自查：返回 (格式不合规, 超过 3 个的文档, 近似变体)。

    格式与词干只对“去重后的 tag”算一次：一篇文档几个 tag、几万篇文档也只有几十个 tag 名。
    """
    bad_format, too_many, seen, valid = [], [], set(), {}
    for d in docs_only(docs):
        if len(d.tags) > 3:
            too_many.append(d)
        for t in d.tags:
            good = valid.get(t)
            if good is None:
                good = valid[t] = bool(TAG_RE.match(t))
            if not good:
                bad_format.append((d.relpath, t))
            seen.add(t)

    by_stem = {}
    for t in seen:
        by_stem.setdefault(_tag_stem(t), set()).add(t)
    variants = {k: sorted(v) for k, v in by_stem.items() if len(v) > 1}
    return bad_format, too_many, variants


def tidy_status(root: str):
    """整理阈值自查：返回 (目录条目数 [(相对路径, 数量)], journal 活跃月份)。

    阈值写在 SKILL 里，但没人愿意手动数目录——这里把它变成一行输出。
    """
    targets = list(TIDY_WATCH)
    # docs/ 与 archive/ 按子目录逐个算：主题分目录时，看的是每个主题的厚度，不是根目录。
    for parent in ("docs", "archive"):
        base = os.path.join(root, parent)
        try:
            targets += [
                f"{parent}/{e.name}" for e in os.scandir(base) if e.is_dir()
            ]
        except OSError:
            pass

    rows = []
    for name in targets:
        path = os.path.join(root, *name.split("/"))
        try:
            rows.append((name, sum(1 for _ in os.scandir(path))))
        except OSError:
            continue
    rows.sort(key=lambda r: (-r[1], r[0]))

    months = set()
    journal = os.path.join(root, "journal")
    try:
        for e in os.scandir(journal):
            m = re.match(r"^(\d{4}-\d{2})-\d{2}\.md$", e.name)
            if m:
                months.add(m.group(1))
    except OSError:
        pass
    return rows, sorted(months)


def fmt_date(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else "—"


@dataclass
class Analysis:
    root: str
    docs: dict
    broken: list
    ambiguous: list
    inbound: dict
    duplicates: dict
    orphans: list
    untagged: list
    tags: dict


def analyze(root: str, use_cache: bool = True, resolve: bool = True) -> Analysis:
    """resolve=False 只解析 front-matter 与 tag：查 tag / 无 tag 用不到链接解析。"""
    root = norm(root)
    docs, _ = scan(root, use_cache=use_cache)
    if not resolve:
        return Analysis(
            root=root,
            docs=docs,
            broken=[],
            ambiguous=[],
            inbound={},
            duplicates={},
            orphans=[],
            untagged=untagged_list(docs),
            tags=tag_map(docs),
        )
    broken, ambiguous, inbound = resolve_all(root, docs)
    return Analysis(
        root=root,
        docs=docs,
        broken=broken,
        ambiguous=ambiguous,
        inbound=inbound,
        duplicates=duplicate_stems(docs),
        orphans=orphan_list(docs, inbound),
        untagged=untagged_list(docs),
        tags=tag_map(docs),
    )
