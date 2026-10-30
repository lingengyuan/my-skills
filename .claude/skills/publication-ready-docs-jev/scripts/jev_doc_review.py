#!/usr/bin/env python3
"""Jev 驱动的文档发布稿扫描（publication-ready-docs skill 的判定层）。

用法:
    python jev_doc_review.py <input.md> [--out-prefix <report路径前缀>] [--doc-type 详细设计]

流程:
  1. 解析 markdown：按标题栈记录章节路径，提取正文句子、表格单元和已知语言的代码注释。代码执行语句只作上下文，不进入审查单元。未闭合代码块和无法识别的语言记入 skipped。
  2. 阶段一：分块并行向 Jev 提问（每单元 6 个 Noul + 1 个 Choice + 1 个 Score，共 8 问）。
  3. 阶段二：对阶段一标记为疑似重复的单元，全文比对判定重复与权威定义位置。
  4. 阈值门控（代码内）：输出 markdown 报告 + JSON 明细。

需要环境变量 TYPESAFE_API_KEY。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from typesafe_sdk import Choice, Noul, RetryPolicy, Score, TypeSafeClient

MODEL = "jev-latest"
CHUNK = 8  # 每请求单元数；8 问/单元 → 64 问/请求

# 阈值（需在目标文档上校准后固化）
T_DELETE = 0.80   # 非 dup 坏味道 noul >= 此值 且 action=delete 才建议删除
T_REVIEW = 0.50   # 非 dup 坏味道 noul >= 此值进入复核
T_ACTION_CONF = 0.65
T_DUP = 0.70      # 阶段二重复判定置信度
T_DUP_ADMIT = 0.75  # 阶段一 dup noul 准入阶段二的门槛（仅做粗筛，阶段二才是真判别）

KIND_PROSE = "prose"
KIND_TABLE = "table_cell"
KIND_COMMENT = "code_comment"


# ---------- markdown 解析 ----------

@dataclass
class Unit:
    sid: str
    text: str
    section: str
    line: int  # 源文件行号
    kind: str = KIND_PROSE
    context: str = ""  # 表格表头/同行字段，或注释相邻代码
    flags: list[str] = field(default_factory=list)


@dataclass
class Comment:
    text: str
    line: int
    end_line: int
    inline_code: str


SENT_SPLIT = re.compile(r"(?<=[。；!?？！])")

SQL_LANGS = {"sql", "plsql", "oracle", "mysql", "postgresql", "psql", "tsql"}
CSS_LANGS = {"css"}
C_LANGS = {
    "java", "js", "javascript", "ts", "typescript", "c", "cpp", "c++", "cs",
    "csharp", "go", "kotlin", "kt", "scala", "rust", "swift", "php", "jsonc",
    "css", "scss",
}
HASH_LANGS = {
    "python", "py", "sh", "bash", "shell", "zsh", "yaml", "yml", "ruby", "rb",
    "perl", "pl", "r", "toml", "makefile", "dockerfile", "properties",
}
HTML_LANGS = {"html", "xml", "svg", "xhtml"}
JSON_LANGS = {"json"}


def comment_markers(lang: str) -> dict:
    if lang in JSON_LANGS:
        return {"line": [], "block": []}
    if lang in CSS_LANGS:
        # url(https://...) 中的 // 不是注释，CSS 只识别块注释。
        return {"line": [], "block": [("/*", "*/")]}
    if lang in SQL_LANGS:
        return {"line": ["--"], "block": [("/*", "*/")]}
    if lang in HASH_LANGS:
        return {"line": ["#"], "block": []}
    if lang in HTML_LANGS:
        return {"line": [], "block": [("<!--", "-->")]}
    if lang in C_LANGS:
        return {"line": ["//"], "block": [("/*", "*/")]}
    return {"line": ["//", "#"], "block": [("/*", "*/"), ("<!--", "-->")]}


def is_known_lang(lang: str) -> bool:
    return lang in SQL_LANGS | C_LANGS | HASH_LANGS | HTML_LANGS | JSON_LANGS


def _append_units(
    units: list[Unit],
    text: str,
    section: str,
    line: int,
    kind: str,
    context: str,
    counter: int,
    *,
    min_len: int = 4,
    strip_markers: bool = False,
) -> int:
    for piece in SENT_SPLIT.split(text):
        piece = piece.strip()
        if strip_markers:
            piece = piece.lstrip("-*· ").strip()
        if len(piece) < min_len:
            continue
        counter += 1
        units.append(
            Unit(
                sid=f"s{counter:03d}",
                text=piece,
                section=section,
                line=line,
                kind=kind,
                context=context,
            )
        )
    return counter


def split_table_row(row: str) -> list[str]:
    """按未转义的 | 切分表格行；保留单元格内的 \\| 字面值和 inline code 中的 |。"""
    text = row.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|") and not text.endswith("\\|"):
        text = text[:-1]
    cells: list[str] = []
    buf: list[str] = []
    code_ticks = 0  # 当前 inline code 的反引号长度，0 表示不在 code span 内
    i = 0
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text) and text[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if text[i] == "`":
            j = i
            while j < len(text) and text[j] == "`":
                j += 1
            run = j - i
            if code_ticks == 0:
                code_ticks = run
            elif code_ticks == run:
                code_ticks = 0
            buf.append(text[i:j])
            i = j
            continue
        if text[i] == "|" and code_ticks == 0:
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(text[i])
        i += 1
    cells.append("".join(buf).strip())
    return cells


def is_separator_row(cells: list[str]) -> bool:
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells)


def parse_table(
    rows: list[tuple[int, str]],
    section: str,
    units: list[Unit],
    counter: int,
    skipped: list[str],
) -> int:
    """表格单元独立成审查单元；表头和同行字段写入 context。"""
    if not rows:
        return counter
    header = split_table_row(rows[0][1])
    start = 2 if len(rows) >= 2 and is_separator_row(split_table_row(rows[1][1])) else 1
    header_text = " | ".join(header)
    skipped.append(f"L{rows[0][0]} 表头: {header_text}")
    for ln, raw in rows[start:]:
        cells = split_table_row(raw)
        if is_separator_row(cells):
            continue
        row_text = " | ".join(cells)
        for idx, cell in enumerate(cells):
            cell = cell.strip()
            if not cell:
                continue
            column = header[idx] if idx < len(header) and header[idx] else f"第{idx + 1}列"
            context = f"列: {column}；表头: {header_text}；本行: {row_text}"
            counter = _append_units(
                units, cell, section, ln, KIND_TABLE, context, counter, min_len=2
            )
    return counter


def _clean_comment(text: str) -> str:
    parts = []
    for line in text.splitlines():
        line = line.strip().lstrip("*").strip()
        if line:
            parts.append(line)
    return " ".join(parts)


def _neighbor_code(code_by_line: dict[int, str], line: int, step: int, limit: int = 4) -> str:
    ln = line + step
    for _ in range(limit):
        text = code_by_line.get(ln, "")
        if text:
            return text
        ln += step
    return ""


def _comment_context(comment: Comment, code_by_line: dict[int, str]) -> str:
    parts = []
    if comment.inline_code:
        parts.append(f"同行代码: {comment.inline_code}")
    else:
        prev = _neighbor_code(code_by_line, comment.line, -1)
        nxt = _neighbor_code(code_by_line, comment.end_line, 1)
        if prev:
            parts.append(f"上一行代码: {prev}")
        if nxt:
            parts.append(f"下一行代码: {nxt}")
    if comment.end_line > comment.line:
        parts.append(f"注释范围: L{comment.line}-L{comment.end_line}")
    return "；".join(parts)


def scan_code_block(code_lines: list[tuple[int, str]], lang: str) -> tuple[list[Comment], dict[int, str]]:
    """提取代码注释。字符串内的 //、--、# 和 https:// 按字面值处理。

    未闭合的字符串和文本块延续到后续行，避免把多行字符串内容当作注释。
    """
    markers = comment_markers(lang)
    comments: list[Comment] = []
    code_by_line: dict[int, str] = {}
    block: tuple[str, int, list[str], str] | None = None  # 结束符、起始行、内容、行内代码
    string_end: str | None = None  # 跨行字符串的结束符

    for ln, raw in code_lines:
        code_parts: list[str] = []
        i = 0
        while i < len(raw):
            if string_end is not None:
                pos = raw.find(string_end, i)
                if pos < 0:
                    code_parts.append(raw[i:])
                    i = len(raw)
                else:
                    code_parts.append(raw[i : pos + len(string_end)])
                    i = pos + len(string_end)
                    string_end = None
                continue

            if block is not None:
                end_marker, start_line, parts, inline_code = block
                pos = raw.find(end_marker, i)
                if pos < 0:
                    parts.append(raw[i:] + "\n")
                    i = len(raw)
                else:
                    parts.append(raw[i:pos] + "\n")
                    i = pos + len(end_marker)
                    comments.append(
                        Comment(_clean_comment("".join(parts)), start_line, ln, inline_code)
                    )
                    block = None
                continue

            ch = raw[i]
            if ch in ("'", '"', "`"):
                triple = raw[i : i + 3]
                if triple == '"""' or (triple == "'''" and lang in {"python", "py"}):
                    pos = raw.find(triple, i + 3)
                    if pos < 0:
                        code_parts.append(raw[i:])
                        string_end = triple
                        i = len(raw)
                    else:
                        code_parts.append(raw[i : pos + 3])
                        i = pos + 3
                    continue

                start = i
                quote = ch
                i += 1
                closed = False
                while i < len(raw):
                    if raw[i] == "\\":
                        i += 2
                        continue
                    if raw[i] == quote:
                        if quote == "'" and i + 1 < len(raw) and raw[i + 1] == "'":
                            i += 2
                            continue
                        i += 1
                        closed = True
                        break
                    i += 1
                code_parts.append(raw[start:i])
                if not closed:
                    string_end = quote
                continue

            started = False
            for begin, end in markers["block"]:
                if raw.startswith(begin, i):
                    block = (end, ln, [], "".join(code_parts).strip())
                    i += len(begin)
                    started = True
                    break
            if started:
                continue

            marker = next((m for m in markers["line"] if raw.startswith(m, i)), None)
            if marker is not None:
                comments.append(
                    Comment(
                        _clean_comment(raw[i + len(marker):]),
                        ln,
                        ln,
                        "".join(code_parts).strip(),
                    )
                )
                i = len(raw)
                continue

            code_parts.append(ch)
            i += 1
        code_by_line[ln] = "".join(code_parts).strip()

    if block is not None:
        end_marker, start_line, parts, inline_code = block
        last_line = code_lines[-1][0] if code_lines else start_line
        comments.append(Comment(_clean_comment("".join(parts)), start_line, last_line, inline_code))

    return comments, code_by_line


def add_code_comments(
    code_lines: list[tuple[int, str]],
    lang: str,
    section: str,
    units: list[Unit],
    counter: int,
    skipped: list[str],
) -> int:
    comments, code_by_line = scan_code_block(code_lines, lang)
    for comment in comments:
        if not comment.text:
            continue
        context = _comment_context(comment, code_by_line)
        counter = _append_units(
            units, comment.text, section, comment.line, KIND_COMMENT, context, counter, min_len=2
        )
    skipped.append(
        f"L{code_lines[0][0] if code_lines else '?'} 代码块 {lang or '未标注'}：执行语句仅作上下文"
    )
    return counter


def parse_markdown(md: str) -> tuple[list[Unit], list[str]]:
    units: list[Unit] = []
    skipped: list[str] = []
    section = ""
    heading_stack: list[tuple[int, str]] = []
    counter = 0
    in_code = False
    fence_char = ""
    fence_len = 0
    lang = ""
    code_start = 0
    code_lines: list[tuple[int, str]] = []
    para_buf: list[tuple[str, int]] = []  # (行文本, 行号)

    def flush_para():
        nonlocal counter
        if not para_buf:
            return
        text = "".join(t for t, _ in para_buf).strip()
        line = para_buf[0][1]
        para_buf.clear()
        if not text:
            return
        counter = _append_units(
            units, text, section, line, KIND_PROSE, "", counter, min_len=4, strip_markers=True
        )

    lines = md.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        ln = i + 1
        i += 1

        if in_code:
            stripped = raw.strip()
            if stripped and set(stripped) == {fence_char} and len(stripped) >= fence_len:
                if is_known_lang(lang):
                    counter = add_code_comments(code_lines, lang, section, units, counter, skipped)
                else:
                    skipped.append(f"L{code_start} 代码块 {lang or '未标注'}：未识别语言，代码仅作上下文")
                skipped.append(f"L{ln} 代码块结束")
                in_code = False
                code_lines = []
                lang = ""
            else:
                code_lines.append((ln, raw))
            continue

        stripped = raw.strip()

        fence = re.match(r"^(`{3,}|~{3,})(.*)$", stripped)
        if fence:
            flush_para()
            marker = fence.group(1)
            fence_char = marker[0]
            fence_len = len(marker)
            info = fence.group(2).strip()
            lang = info.split()[0].lower() if info else ""
            in_code = True
            code_start = ln
            skipped.append(f"L{ln} 代码块开始: {lang or '未标注'}")
            continue

        if stripped.startswith("|"):
            flush_para()
            rows = [(ln, stripped)]
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append((i + 1, lines[i].strip()))
                i += 1
            counter = parse_table(rows, section, units, counter, skipped)
            continue

        if stripped.startswith("<title>") or re.fullmatch(r"<title>.*</title>", stripped):
            flush_para()
            skipped.append(f"L{ln} 文档标题")
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            flush_para()
            level = len(m.group(1))
            title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append((level, title))
            section = " > ".join(t for _, t in heading_stack)
            skipped.append(f"L{ln} 标题: {title}")
            continue

        if not stripped:
            flush_para()
            continue

        if re.match(r"^([-*·]|\d+[.、)])\s*", stripped):
            flush_para()
            counter = _append_units(
                units, stripped, section, ln, KIND_PROSE, "", counter, min_len=4, strip_markers=True
            )
            continue

        para_buf.append((stripped, ln))

    if in_code:
        skipped.append(f"L{code_start} 代码块未闭合，未提取注释")
    flush_para()
    return units, skipped


# ---------- 阶段一：单元级判定 ----------

UNIT_NOTE = (
    "单元可能来自正文、表格单元或代码注释。表格单元结合 context 中的表头与同行字段理解；"
    "代码注释结合 context 中的代码理解。审查对象是单元文本，代码执行语句只作上下文。"
    "按信息价值判断；安全、凭据、幂等等关键词不单独决定保留或删除。"
)

NOUL_DEFS = {
    "meta": (
        "该单元是否只在介绍、强调或包装后续内容（如「需要注意的是」「换句话说」「显然」），"
        "或加入规范外、无新增信息的比较与提醒（如「与业务 batchId 不同」「二者不可混用」）；"
        "删除后读者仍能获取事实或执行任务。是 → yes。"
        "按信息价值判断：含已确认差异、事务边界、失败后果或数据范围的句子不算。"
    ),
    "defensive": "该单元是否用否定对照或预防误解的写法包装规则（如「不是X而是Y」「并不意味着」「不要理解成」），删除包装后规则仍可正面表述。直接限定写入范围、事务后果或失败处理的句子，按是否提供项目必要事实判断。是 → yes。",
    "process": "该单元是否在描述文档的编写、审查或修改过程（如「经过分析」「上一版存在」「根据本次要求」），而不是系统事实或设计决策。是 → yes。",
    "reassurance": "该单元是否主要安抚影响面（如「无新增风险」「其他不变」），删除后不损失职责、兼容性、失败后果或操作信息。是 → yes。",
    "dup": "该单元表达的事实或规则是否可能在本文件其他位置（正文、表格单元格或代码注释）出现，或被更详细地定义。这是粗筛，宁多勿漏。是 → yes。",
    "placeholder": "该单元是否包含未收口的值或占位：TODO、示例值、待核值、示例 URL。标注责任人不等于已收口；该未决条件影响方案成立且已写明确认对象与动作时，按项目必要性判断。是 → yes。",
}

ACTION_CRITERIA = {
    "keep": "提供读者理解、实施、运行或验证所需的事实、规则、职责、决策、接口、流程或边界；完整字段表定义、唯一事务边界、数据范围和失败后果按事实保留",
    "delete": "删除后不影响读者理解、实施、运行或验证；包括元话语、安抚、纯重复、规范外比较或提醒、通用常识和未收口占位",
    "rewrite": "含有效信息但带防御性包装、语序或形式不当，需改为直接规则或条件；改写只保留有效信息，不把无新增信息的提醒换成同义正面说明",
    "merge": "本单元复述了文件其他位置的权威定义，应合并过去并删除本单元，合并时保留约束；完整字段表定义本身保留，不合并到正文或注释",
}

DENSITY_CRITERIA = [
    "高：提供新的事实、职责、约束、决策、边界或验收标准",
    "中：部分重复但含补充信息或必要上下文",
    "低：主要承担过渡、强调、重复、安抚作用，删除后不损失有效信息",
]


def build_state(units: list[Unit], doc_type: str) -> dict:
    return {
        "doc_type": doc_type,
        "section_path": units[0].section,
        "sentences": [
            {
                "id": u.sid,
                "text": u.text,
                "kind": u.kind,
                **({"context": u.context} if u.context else {}),
            }
            for u in units
        ],
    }


def chunk_level_question(doc_type: str) -> tuple[str, Noul]:
    """块级判断：术语一致性（跨句判断，不适合按句拆分）。"""
    return "term_inconsistency", Noul(
        instructions=(
            f"阅读本组全部单元（文档类型 {doc_type}）。判断：是否存在同一概念/对象在"
            "不同单元中使用了不同的名称或写法（如同一字段一处叫 X 一处叫 Y、中英混用、"
            "大小写或下划线不一致）。仅统计确属同一实体的不一致，不同概念不算。"
        )
    )


def chunk_questions(units: list[Unit], doc_type: str) -> dict:
    qs: dict = {}
    for idx, u in enumerate(units):
        ref = f"`sentences[{idx}]`（id {u.sid}，类型 {u.kind}）"
        for key, ins in NOUL_DEFS.items():
            qs[f"{u.sid}_{key}"] = Noul(instructions=f"{UNIT_NOTE} 针对{ref}：{ins}")
        qs[f"{u.sid}_action"] = Choice(
            instructions=(
                f"{UNIT_NOTE} 针对{ref}：在文档类型 {doc_type} 的发布稿中，该单元应如何处置？"
            ),
            criteria=ACTION_CRITERIA,
        )
        qs[f"{u.sid}_density"] = Score(
            instructions=f"{UNIT_NOTE} 针对{ref}：该单元的信息密度如何？",
            criteria=DENSITY_CRITERIA,
        )
    return qs


# ---------- 阶段二：跨章节重复与权威定义定位 ----------

def number_lines(md: str) -> str:
    """给全文加源行号，供阶段二区分候选原位置与其他位置。"""
    return "\n".join(f"L{i}: {line}" for i, line in enumerate(md.splitlines(), 1))


def dup_state(units: list[Unit], full_doc: str, doc_type: str) -> dict:
    return {
        "doc_type": doc_type,
        "full_document": number_lines(full_doc),
        "candidates": [
            {
                "id": u.sid,
                "line": u.line,
                "section": u.section,
                "kind": u.kind,
                "text": u.text,
                **({"context": u.context} if u.context else {}),
            }
            for u in units
        ],
    }


def dup_questions(units: list[Unit]) -> dict:
    qs: dict = {}
    for idx, u in enumerate(units):
        ref = (
            f"`candidates[{idx}]`（id {u.sid}，源行 L{u.line}，"
            f"章节「{u.section}」，类型 {u.kind}）"
        )
        qs[f"{u.sid}_dup"] = Choice(
            instructions=(
                f"针对{ref}：该单元与文档其他位置是什么关系？"
                "duplicate 指本单元复述了别处更适合作为权威定义的内容，应合并过去。"
                "完整字段表定义优先于正文和注释的复述；表格单元格即使只含片段，也属于该权威定义。"
                "字段表存在时，表格单元格选 unique；正文和注释对表格的复述选 duplicate。"
                "唯一的事务边界、失败条件和数据范围保留，不因相近表述判为重复。"
                "比较范围包括正文、表格单元格和代码注释，仅依据 full_document 判断。"
                "full_document 每行以 Lx: 标注源行号；candidates 的 line 是本单元原位置。"
                "本单元在自身源行的出现、表格同一行的其他列，都不是其他位置的重复定义；"
                "结合 kind 和 context 中的列名、表头、同行字段判断。"
            ),
            criteria={
                "duplicate": "本单元复述了别处更适合作为权威定义的内容，应合并到权威定义处，只保留一处",
                "complementary": "其他位置有相近内容但角度不同，本单元含独立补充信息，应保留",
                "unique": "文档中无其他更权威的等价表述，本单元是唯一来源或权威定义",
            },
        )
    return qs


# ---------- 门控 ----------

def classify_findings(findings: list[dict]) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    deletes, merges, rewrites, reviews = [], [], [], []
    for f in findings:
        # dup 已由阶段二单独判定，不参与删除阈值，否则粗筛饱和会把全部单元送进复核。
        top_p = f.get("gate_p", f.get("top_p") or 0)
        if (
            f.get("action") == "delete"
            and (f.get("action_confidence") or 0) >= T_ACTION_CONF
            and top_p >= T_DELETE
        ):
            deletes.append(f)
        elif f.get("dup_relation") == "duplicate" and (f.get("dup_confidence") or 0) >= T_DUP:
            merges.append(f)
        elif f.get("action") == "rewrite" and (f.get("action_confidence") or 0) >= T_ACTION_CONF:
            rewrites.append(f)
        elif top_p >= T_REVIEW or (
            f.get("dup_relation") == "duplicate" and (f.get("dup_confidence") or 0) >= 0.55
        ):
            reviews.append(f)
        elif f.get("action") in ("delete", "merge", "rewrite") and (
            f.get("action_confidence") or 0
        ) >= T_REVIEW:
            reviews.append(f)
    return deletes, merges, rewrites, reviews


# ---------- 主流程 ----------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--out-prefix", default=None)
    ap.add_argument("--doc-type", default="详细设计")
    args = ap.parse_args()

    src = Path(args.input).expanduser().resolve()
    md = src.read_text(encoding="utf-8")
    out_prefix = Path(args.out_prefix) if args.out_prefix else src.with_suffix("")
    out_prefix.parent.mkdir(parents=True, exist_ok=True)

    units, skipped = parse_markdown(md)
    kinds = Counter(u.kind for u in units)
    print(
        f"[parse] units={len(units)} prose={kinds[KIND_PROSE]} "
        f"table={kinds[KIND_TABLE]} comment={kinds[KIND_COMMENT]} skipped_marks={len(skipped)}",
        file=sys.stderr,
    )

    client = TypeSafeClient()
    retry = RetryPolicy()
    findings: list[dict] = []
    failures: list[dict] = []
    chunk_flags: list[dict] = []

    # 阶段一（并发请求，wall time ≈ 最慢单请求）
    chunks = [units[start : start + CHUNK] for start in range(0, len(units), CHUNK)]

    def run_chunk(chunk: list[Unit]):
        questions = chunk_questions(chunk, args.doc_type)
        tid, tq = chunk_level_question(args.doc_type)
        questions[tid] = tq
        resp = client.system_one(
            state=build_state(chunk, args.doc_type),
            questions=questions,
            model=MODEL,
            retry=retry,
        )
        rows = []
        for u in chunk:
            row = {
                "sid": u.sid,
                "section": u.section,
                "line": u.line,
                "text": u.text,
                "kind": u.kind,
                "context": u.context,
            }
            smells = {}
            for key in NOUL_DEFS:
                a = resp.answers.get(f"{u.sid}_{key}")
                if a is not None:
                    smells[key] = round(a.noul, 3)
            act = resp.answers.get(f"{u.sid}_action")
            den = resp.answers.get(f"{u.sid}_density")
            row["smells"] = smells
            row["action"] = act.choice if act else None
            row["action_confidence"] = round(act.confidence, 3) if act else None
            row["density"] = round(den.score, 3) if den else None
            top = max(smells.values(), default=0.0)
            gate_top = max((v for k, v in smells.items() if k != "dup"), default=0.0)
            row["top_smell"] = max(smells, key=smells.get) if smells else None
            row["top_p"] = top
            row["gate_p"] = gate_top
            rows.append(row)
        ta = resp.answers.get(tid)
        flag = {"section": chunk[0].section, "sids": [u.sid for u in chunk]}
        if ta is not None:
            flag["term_inconsistency"] = round(ta.noul, 3)
        print(f"[stage1] {chunk[-1].sid} done", file=sys.stderr)
        return chunk, rows, flag

    with ThreadPoolExecutor(max_workers=min(4, len(chunks) or 1)) as pool:
        futs = {pool.submit(run_chunk, c): c for c in chunks}
        for fut in as_completed(futs):
            try:
                _, rows, flag = fut.result()
                findings.extend(rows)
                chunk_flags.append(flag)
            except Exception as e:  # noqa: BLE001
                failures.append({"stage": 1, "sids": [u.sid for u in futs[fut]], "error": str(e)})
    findings.sort(key=lambda r: r["sid"])

    # 阶段二：疑似重复单元（阶段一 dup 仅为粗筛，饱和属预期，阶段二全文比对做真判别）
    dup_cands = [f for f in findings if f["smells"].get("dup", 0) >= T_DUP_ADMIT]
    if dup_cands:
        cand_units = [
            Unit(
                sid=f["sid"],
                text=f["text"],
                section=f["section"],
                line=f["line"],
                kind=f.get("kind", KIND_PROSE),
                context=f.get("context", ""),
            )
            for f in dup_cands
        ]
        try:
            resp = client.system_one(
                state=dup_state(cand_units, md, args.doc_type),
                questions=dup_questions(cand_units),
                model=MODEL,
                retry=retry,
            )
        except Exception as e:  # noqa: BLE001
            failures.append({"stage": 2, "sids": [u.sid for u in cand_units], "error": str(e)})
            resp = None
        if resp is not None:
            by_sid = {f["sid"]: f for f in findings}
            for idx, u in enumerate(cand_units):
                a = resp.answers.get(f"{u.sid}_dup")
                if a is None:
                    continue
                by_sid[u.sid]["dup_relation"] = a.choice
                by_sid[u.sid]["dup_confidence"] = round(a.confidence, 3)
                by_sid[u.sid]["dup_probabilities"] = {k: round(v, 3) for k, v in a.probabilities.items()}

    deletes, merges, rewrites, reviews = classify_findings(findings)

    # 报告
    def fmt(f: dict) -> str:
        smells = ", ".join(
            f"{k}:{v}" for k, v in sorted(f["smells"].items(), key=lambda kv: -kv[1]) if v >= 0.3
        )
        extra = ""
        if "dup_relation" in f:
            extra = f"；跨章比对: {f['dup_relation']}({f.get('dup_confidence', 0)})"
        kind = f"，{f['kind']}" if f.get("kind") and f["kind"] != KIND_PROSE else ""
        context = f"\n  上下文: {f['context']}" if f.get("context") else ""
        return (
            f"- **[{f['sid']}] §{f['section']}**（L{f['line']}{kind}，action={f['action']}"
            f" conf={f['action_confidence']}，density={f['density']}）{extra}\n"
            f"  > {f['text']}{context}\n"
            f"  坏味道概率: {smells or '—'}"
        )

    lines = [
        f"# Jev 发布稿扫描报告：{src.name}",
        "",
        f"- 文档类型: {args.doc_type}｜单元数: {len(units)}｜模型: {MODEL}",
        f"- 覆盖: 正文 {kinds[KIND_PROSE]}｜表格单元 {kinds[KIND_TABLE]}｜代码注释 {kinds[KIND_COMMENT]}；代码执行语句仅作上下文",
        f"- 阈值: delete(非dup noul≥{T_DELETE}, action_conf≥{T_ACTION_CONF})｜merge(dup_conf≥{T_DUP})｜review(非dup noul≥{T_REVIEW})",
        f"- 请求失败: {len(failures)}（见 JSON 明细）",
        "",
        f"## 一、建议删除（{len(deletes)}）",
        "",
    ]
    lines += [fmt(f) for f in deletes] or ["（无）"]
    lines += ["", f"## 二、建议合并（{len(merges)}）", ""]
    lines += [fmt(f) for f in merges] or ["（无）"]
    lines += ["", f"## 三、建议改写（{len(rewrites)}）", ""]
    lines += [fmt(f) for f in rewrites] or ["（无）"]
    lines += ["", f"## 四、待复核（{len(reviews)}）", ""]
    lines += [fmt(f) for f in reviews] or ["（无）"]

    ti_flags = [c for c in chunk_flags if c.get("term_inconsistency", 0) >= 0.5]
    lines += ["", f"## 五、术语一致性（块级，{len(ti_flags)}）", ""]
    lines += [
        f"- §{c['section']}（{','.join(c['sids'])}）不一致概率: {c['term_inconsistency']}"
        for c in ti_flags
    ] or ["（无）"]

    report_md = out_prefix.with_suffix(".review.md")
    report_json = out_prefix.with_suffix(".review.json")
    report_md.write_text("\n".join(lines), encoding="utf-8")
    report_json.write_text(
        json.dumps(
            {"findings": findings, "chunk_flags": chunk_flags, "failures": failures, "skipped": skipped},
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"[done] report={report_md}", file=sys.stderr)
    print(
        f"summary: delete={len(deletes)} merge={len(merges)} rewrite={len(rewrites)} review={len(reviews)} fail={len(failures)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
