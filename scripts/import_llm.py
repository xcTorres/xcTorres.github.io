#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import the study notes from learn-llm-from-scratch into the `llm` collection.

The notes live in a separate repo and are written for reading on GitHub. This
turns them into blog documents: it adds front matter, drops the sections that
are working notes rather than published material, and fixes the several places
where GitHub-flavoured markdown and kramdown disagree.

    python3 scripts/import_llm.py [path-to-learn-llm-from-scratch]
    python3 scripts/import_llm.py --check    # report what a re-import would change

The import is destructive (`_llm/` is rebuilt from scratch) and lossy (the
source's interview section and appendices are dropped), so an edit made on the
blog side cannot be recovered from the source and disappears on the next run.
Use --check before importing if there is any chance of local edits.

`_llm/` is rewritten from scratch on every run, so edit the source repo and
re-import — never edit `_llm/*.md` by hand.

The English bodies in `_llm_en/` are translated by hand and are never
generated. To keep the in-page language switch honest, every run compares each
Chinese entry against a hash recorded in `_llm_en/.sync.json` and names the
entries that have moved since the English was last brought in line. The loop is:

    1. edit the Chinese source
    2. python3 scripts/import_llm.py          -> lists the entries that changed
    3. translate just those entries in _llm_en/
    4. python3 scripts/import_llm.py --synced-en   -> record the new baseline

`_llm_en/` also bypasses every markdown fix below, so it is linted instead:
bare pipes inside math, tables with no blank line before them, and bare URLs.
"""

import hashlib
import json
import os
import re
import shutil
import sys

DEFAULT_SOURCE = os.path.expanduser("~/Downloads/learn-llm-from-scratch")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(REPO, "_llm")

TOPICS = {"llm", "agent"}   # add "vlm" when that tab is ready to publish
CATEGORIES = {"summary"}  # paper deep-dives and code reports stay in the repo
# published one summary per tab; the rest stay in the repo and are linked there
SKIP = {"/vlm/detection/", "/vlm/3d/"}

GITHUB = "https://github.com/xcTorres/learn-llm-from-scratch/blob/main/"

# source file, permalink, topic, category, title, subtitle, order, highlights,
# title_en, subtitle_en, highlights_en
DOCS = [
    (
        "LLM知识总结.md", "/llm/summary/", "llm", "summary",
        "LLM 知识总结", "基础架构 · 训练对齐 · 推理优化", 1,
        "交叉熵与 KL 散度 · Transformer 与 self-attention · RoPE · KV Cache 与 MQA/GQA · MoE · "
        "RLHF 与 DPO · LoRA/QLoRA · 量化 · Flash Attention · 推测解码 · Prefill 与 Decode · Scaling Law",
        "LLM Notes", "Architecture · Training &amp; Alignment · Inference",
        "Cross-entropy and KL divergence · Transformer and self-attention · RoPE · KV cache, MQA/GQA · "
        "MoE · RLHF and DPO · LoRA/QLoRA · Quantization · FlashAttention · Speculative decoding · "
        "Prefill vs. decode · Scaling laws",
    ),
    (
        "VLM知识总结.md", "/vlm/summary/", "vlm", "summary",
        "VLM 知识总结", "视觉语言模型 · 扩散生成 · 视频理解", 1,
        "CLIP 与 SigLIP · 视觉如何接入 LLM · LLaVA 两阶段训练 · 视觉 token 压缩 · 扩散模型与 "
        "Stable Diffusion · DiT 与 Flow Matching · 视频 token 爆炸 · M-RoPE 时序编码 · 流式视频理解",
        "VLM Notes", "Vision-Language Models · Diffusion · Video Understanding",
        "CLIP and SigLIP · Attaching vision to an LLM · LLaVA's two stages · Visual-token compression · "
        "Diffusion and Stable Diffusion · DiT and flow matching · Video token explosion · M-RoPE · "
        "Streaming video understanding",
    ),
    (
        "Agent知识总结.md", "/agent/summary/", "agent", "summary",
        "Agent 知识总结", "规划 · 工具 · 记忆 · 多智能体", 1,
        "Agent 核心组成 · ReAct 与规划 · 工具调用 · 短期与长期记忆 · 反思与自我纠错 · "
        "多智能体协作 · 评测与失败模式",
        "Agent Notes", "Planning · Tools · Memory · Multi-Agent",
        "What an LLM agent is · ReAct and planning · Tool use · Short- and long-term memory · "
        "Reflection and self-correction · Multi-agent collaboration · Evaluation and failure modes",
    ),
    (
        "检测与分割知识总结.md", "/vlm/detection/", "vlm", "summary",
        "目标检测与图像分割", "两阶段与单阶段 · DETR · 语义与实例分割 · SAM", 2,
        "R-CNN 系列 · YOLO · anchor-free · DETR · FPN · NMS · 语义/实例/全景分割 · SAM",
        "Object Detection & Segmentation", "Two-stage & one-stage · DETR · Segmentation · SAM",
        "The R-CNN line · YOLO · anchor-free · DETR · FPN · NMS · semantic/instance/panoptic "
        "segmentation · SAM",
    ),
    (
        "三维重建知识总结.md", "/vlm/3d/", "vlm", "summary",
        "三维重建知识总结", "SfM / MVS · NeRF · 3D Gaussian Splatting", 3,
        "SfM 与 MVS · 深度估计 · 3D 表示方式 · NeRF · 3D Gaussian Splatting · 动态 4D 重建 · "
        "前馈式几何大模型",
        "3D Reconstruction Notes", "SfM / MVS · NeRF · 3D Gaussian Splatting",
        "SfM and MVS · Depth estimation · 3D representations · NeRF · 3D Gaussian Splatting · "
        "Dynamic 4D reconstruction · Feed-forward geometry models",
    ),
]

# whole sections to drop: private working notes and reference appendices,
# neither of which belongs in the published notes
DROP_HEADINGS = (
    re.compile(r"^#\s*第七部分：面试表达技巧"),
    re.compile(r"^#\s*附录"),
)

BARE_URL = re.compile(r'https?://[^\s<>\[\]()"\'`，。、；：｜）】]+')
PROTECTED = re.compile(r'\[[^\]]*\]\([^)]*\)|`[^`]*`')
TABLE_DELIM = re.compile(r"^\s*\|[\s:|-]+\|\s*$")

LINK_MAP = {}
for _src, _permalink, _topic, _cat, *_rest in DOCS:
    LINK_MAP[_src] = (_permalink if (_topic in TOPICS and _permalink not in SKIP)
                      else GITHUB + _src)


# The source is a study/interview prep repo; the blog presents the same material
# as notes, so interview framing is stripped. Anything that slips through is
# reported at the end of a run rather than published silently.
DEINTERVIEW = (
    ("面试常被追问", ""),
    ("面试中常被追问", ""),
    ("面试官", "读者"),
)
INTERVIEW_WORDS = re.compile(r"面试|背题|考官")


def deinterview(text):
    for old, new in DEINTERVIEW:
        text = text.replace(old, new)
    return text


def strip_intro(lines):
    """Drop the source's own H1 and the blurb under it; the layout renders a
    header from the front matter instead."""
    i = 0
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    i += 1
    while i < len(lines) and not lines[i].startswith("# "):
        i += 1
    return lines[i:]


def drop_sections(lines):
    out, skipping = [], False
    for line in lines:
        if line.startswith("# "):
            skipping = any(p.match(line) for p in DROP_HEADINGS)
        if not skipping:
            out.append(line)
    return out


def fix_tables(lines):
    """kramdown needs a blank line on *both* sides of a table.

    Without one before, the pipe rows are read as a lazy continuation of the
    paragraph above; without one after, the following line is swallowed as a
    continuation of the table. Either way the whole block falls back to a
    paragraph and the `---` delimiter even gets typographed into em-dashes."""
    out = []
    in_table = False
    for i, line in enumerate(lines):
        is_row = line.lstrip().startswith("|")
        starts_table = (is_row and i + 1 < len(lines)
                        and TABLE_DELIM.match(lines[i + 1]))
        if starts_table and out and out[-1].strip() != "":
            out.append("")
        if in_table and not is_row and line.strip() != "":
            out.append("")
        in_table = is_row
        out.append(line)
    return out


def protect_math(text):
    r"""kramdown eats `\|` inside math, and reads a bare `|` as a table column
    separator — the DPO derivation used to be shredded into a five-cell table."""
    def fix(m):
        out = m.group(0).replace(r"\|", r"\Vert ")
        return re.sub(r"(?<!\\)\|", r"\\mid ", out)

    text = re.sub(r"\$\$.*?\$\$", fix, text, flags=re.S)
    return re.sub(r"\$[^$\n]+\$", fix, text)


def autolink(text):
    """kramdown's GFM parser leaves bare URLs as plain text, and the notes cite
    papers as `Name — https://arxiv.org/abs/...`, so none of them were clickable."""
    out, in_fence = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        stash = []

        def hide(m):
            stash.append(m.group(0))
            return "\x00%d\x00" % (len(stash) - 1)

        tmp = PROTECTED.sub(hide, line)

        def link(m):
            url, trail = m.group(0), ""
            # a sentence-ending period or comma is punctuation, not part of the URL
            while url and url[-1] in ".,;:":
                trail = url[-1] + trail
                url = url[:-1]
            return "[%s](%s)%s" % (url, url, trail)

        tmp = BARE_URL.sub(link, tmp)
        out.append(re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], tmp))
    return "\n".join(out)


def rewrite_links(text):
    """Point cross-document links at the published page when there is one, and
    at GitHub when there is not, so nothing dead-ends."""
    for name, target in LINK_MAP.items():
        text = text.replace("](%s)" % name, "](%s)" % target)
        text = text.replace("](./%s)" % name, "](%s)" % target)
    return text


def build_intro(permalink, subtitle):
    siblings = [(t, p) for src, p, topic, cat, t, *_ in DOCS
                if cat == "summary" and topic in TOPICS
                and p not in SKIP and p != permalink]
    lines = [
        "> **定位**：%s。每个条目按 **核心答案 → 深入原理 → 权衡 / 追问 → 参考** 组织，"
        "⭐ 标记值得重点深挖的地方。" % subtitle,
    ]
    if siblings:
        links = " · ".join("[%s](%s)" % (t, p) for t, p in siblings)
        lines += ["> ", "> **配套**：%s" % links]
    return "\n".join(lines)


def yaml_quote(s):
    return '"%s"' % s.replace('"', '\\"')


def convert(source_dir, doc):
    (src, permalink, topic, category, title, subtitle, order,
     highlights, title_en, subtitle_en, highlights_en) = doc

    with open(os.path.join(source_dir, src), encoding="utf-8") as f:
        lines = f.read().split("\n")

    lines = fix_tables(drop_sections(strip_intro(lines)))
    body = "\n".join(lines).strip()
    body = protect_math(body)
    body = autolink(rewrite_links(deinterview(body)))
    # dropping a trailing appendix leaves the rule that preceded it
    body = re.sub(r'\n+---\s*$', '', body)

    pair = os.path.splitext(os.path.basename(permalink.strip("/").replace("/", "-")))[0]
    has_math = "$$" in body or re.search(r"\$[^$\n]+\$", body) is not None

    front = [
        "---",
        "layout: llm-doc",
        "title: %s" % yaml_quote(title),
        "subtitle: %s" % yaml_quote(subtitle),
        "topic: %s" % topic,
        "category: %s" % category,
        "order: %d" % order,
        "permalink: %s" % permalink,
        "lang: zh",
        "pair: %s" % pair,
        "source: %s" % yaml_quote(src),
        "highlights: %s" % yaml_quote(highlights),
        "title_en: %s" % yaml_quote(title_en),
        "subtitle_en: %s" % yaml_quote(subtitle_en),
        "highlights_en: %s" % yaml_quote(highlights_en),
    ]
    if has_math:
        front.append("mathjax: true")
    front.append("---")

    parts = ["\n".join(front), "", "* TOC", "{:toc .llm-toc-list}", "",
             build_intro(permalink, subtitle), "", "---", "", body, ""]
    return pair + ".md", "\n".join(parts), has_math, body.count("\n") + 1




SYNC_FILE = os.path.join(REPO, "_llm_en", ".sync.json")


def sections_of(path):
    """Split a note into its `### ` entries, keyed by position."""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    marks = [i for i, l in enumerate(lines) if l.startswith("### ")]
    out = []
    for n, i in enumerate(marks):
        end = marks[n + 1] if n + 1 < len(marks) else len(lines)
        out.append((lines[i][4:].strip(), "\n".join(lines[i:end]).strip()))
    return out


def translation_status():
    """Report which Chinese entries have moved since the English was last synced.

    The English notes are translated by hand, so nothing can regenerate them.
    What this can do is say exactly which entries drifted, so a sync is a short
    targeted job rather than a diff of the whole document.
    """
    try:
        with open(SYNC_FILE, encoding="utf-8") as f:
            recorded = json.load(f)
    except (IOError, ValueError):
        recorded = {}

    report = {}
    for name in sorted(os.listdir(DEST)) if os.path.isdir(DEST) else []:
        if not name.endswith(".md"):
            continue
        en_path = os.path.join(REPO, "_llm_en", name)
        if not os.path.exists(en_path):
            report[name] = [("missing", "no English document at all")]
            continue

        zh = sections_of(os.path.join(DEST, name))
        en = sections_of(en_path)
        recorded_doc = recorded.get(name, {})
        rows = []
        seen = set()
        for heading, body in zh:
            seen.add(heading)
            digest = hashlib.sha1(body.encode("utf-8")).hexdigest()[:12]
            was = recorded_doc.get(heading)
            if was is None:
                rows.append(("new", heading))
            elif was != digest:
                rows.append(("changed", heading))
        for gone in sorted(set(recorded_doc) - seen):
            rows.append(("removed", gone))
        if len(en) != len(zh):
            rows.append(("count", "%d Chinese entries vs %d English" % (len(zh), len(en))))
        if rows:
            report[name] = rows
    return report


def record_sync():
    recorded = {}
    for name in sorted(os.listdir(DEST)):
        if not name.endswith(".md"):
            continue
        # keyed by heading, not position: inserting an entry must not report
        # every entry after it as changed
        recorded[name] = {
            heading: hashlib.sha1(body.encode("utf-8")).hexdigest()[:12]
            for heading, body in sections_of(os.path.join(DEST, name))
        }
    with open(SYNC_FILE, "w", encoding="utf-8") as f:
        json.dump(recorded, f, indent=2, sort_keys=True)
        f.write("\n")
    return recorded


def lint_english():
    """`_llm_en/` is hand-written and bypasses every fix above, so the same
    kramdown traps have to be checked for rather than repaired."""
    en_dir = os.path.join(REPO, "_llm_en")
    if not os.path.isdir(en_dir):
        return []
    problems = []
    for name in sorted(os.listdir(en_dir)):
        if not name.endswith(".md"):
            continue
        path = os.path.join(en_dir, name)
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
        in_fence = False
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            # a bare pipe inside math is read as a table column separator
            for m in re.finditer(r"\$[^$\n]+\$", line):
                if re.search(r"(?<!\\)\|", m.group(0)):
                    problems.append("%s:%d  bare | inside math -> kramdown "
                                    "will split the line into table cells: %s"
                                    % (name, i, m.group(0)[:50]))
            # a table needs a blank line before it
            if (line.lstrip().startswith("|") and i < len(lines)
                    and TABLE_DELIM.match(lines[i]) and lines[i - 2].strip()):
                problems.append("%s:%d  table with no blank line before it"
                                % (name, i))
            # and one after it, or the next line is swallowed into the table
            if (line.lstrip().startswith("|") and i < len(lines)
                    and not lines[i].lstrip().startswith("|")
                    and lines[i].strip()):
                problems.append("%s:%d  table with no blank line after it"
                                % (name, i))
            # bare URLs are not autolinked by kramdown
            stash = PROTECTED.sub("", line)
            if BARE_URL.search(stash):
                problems.append("%s:%d  bare URL will not be linked: %s"
                                % (name, i, BARE_URL.search(stash).group(0)[:50]))
    return problems


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_only = "--check" in sys.argv[1:]
    accept_en = "--synced-en" in sys.argv[1:]
    source_dir = args[0] if args else DEFAULT_SOURCE
    if not os.path.isdir(source_dir):
        sys.exit("source repo not found: %s" % source_dir)

    published = [d for d in DOCS
                 if d[2] in TOPICS and d[3] in CATEGORIES and d[1] not in SKIP]
    if check_only:
        import difflib
        clean = True
        for doc in published:
            name, text, _, _ = convert(source_dir, doc)
            path = os.path.join(DEST, name)
            current = ""
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    current = f.read()
            if current == text:
                print("%-42s unchanged" % name)
                continue
            clean = False
            print("%-42s WOULD CHANGE" % name)
            for line in difflib.unified_diff(
                    current.split("\n"), text.split("\n"),
                    fromfile="%s (on disk)" % name,
                    tofile="%s (from source)" % name, lineterm="", n=1):
                print("  " + line)
        for orphan in sorted(os.listdir(DEST)) if os.path.isdir(DEST) else []:
            if orphan not in [convert(source_dir, d)[0] for d in published]:
                clean = False
                print("%-42s WOULD BE DELETED" % orphan)
        print("\nno changes" if clean else "\nre-importing would apply the above")
        return

    if os.path.isdir(DEST):
        shutil.rmtree(DEST)
    os.makedirs(DEST)

    print("%-42s %-6s %s" % ("file", "math", "lines"))
    for doc in published:
        name, text, has_math, n = convert(source_dir, doc)
        with open(os.path.join(DEST, name), "w", encoding="utf-8") as f:
            f.write(text)
        print("%-42s %-6s %d" % (name, "yes" if has_math else "-", n))

    leftovers = []
    for doc in published:
        name, text, _, _ = convert(source_dir, doc)
        for i, line in enumerate(text.split("\n"), 1):
            if INTERVIEW_WORDS.search(line):
                leftovers.append("%s:%d  %s" % (name, i, line.strip()[:70]))

    print("\n%d docs -> %s" % (len(published), DEST))
    if leftovers:
        print("warning: interview framing survived into the output:")
        for row in leftovers:
            print("  " + row)
    en_dir = os.path.join(REPO, "_llm_en")
    if os.path.isdir(en_dir):
        stale = sorted(os.listdir(en_dir))
        if stale:
            print("reminder: %s is hand-written and was NOT regenerated (%s)"
                  % (os.path.basename(en_dir), ", ".join(stale)))
    problems = lint_english()
    if problems:
        print("\n_llm_en lint:")
        for row in problems:
            print("  " + row)

    if accept_en:
        record_sync()
        print("\nrecorded the current Chinese entries as translated")
        return
    status = translation_status()
    if status:
        print("\nEnglish out of sync — these Chinese entries moved:")
        for name, rows in status.items():
            for kind, what in rows:
                print("  %-11s %s  (%s)" % (kind, what, name))
        print("  after translating, run: python3 scripts/import_llm.py --synced-en")


if __name__ == "__main__":
    main()
