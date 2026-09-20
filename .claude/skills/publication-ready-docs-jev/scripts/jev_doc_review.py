#!/usr/bin/env python3
"""Jev 驱动的文档发布稿扫描（publication-ready-docs skill 的判定层）。

用法:
    python jev_doc_review.py <input.md> [--out-prefix <report路径前缀>] [--doc-type 详细设计]

流程:
  1. 解析 markdown：按章节切分，提取句子级单元（跳过代码块与表格）。
  2. 阶段一：分块并行向 Jev 提问（每句 5 个 Noul + 1 个 Choice + 1 个 Score）。
  3. 阶段二：对阶段一标记为疑似重复的句子，全文比对判定重复与权威定义位置。
  4. 阈值门控（代码内）：输出 markdown 报告 + JSON 明细。

需要环境变量 TYPESAFE_API_KEY。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from typesafe_sdk import Choice, Noul, RetryPolicy, Score, TypeSafeClient

MODEL = "jev-latest"
CHUNK = 8  # 每请求句子数；7 问/句 → 56 问/请求

# 阈值（需在目标文档上校准后固化）
T_DELETE = 0.80   # 坏味道 noul >= 此值 且 action=delete 才建议删除
T_REVIEW = 0.50   # noul >= 此值进入复核
T_ACTION_CONF = 0.65
T_DUP = 0.70      # 阶段二重复判定置信度
T_DUP_ADMIT = 0.75  # 阶段一 dup noul 准入阶段二的门槛（仅做粗筛，阶段二才是真判别）


# ---------- markdown 解析 ----------

@dataclass
class Unit:
    sid: str
    text: str
    section: str
    line: int  # 源文件行号
    flags: list[str] = field(default_factory=list)


SENT_SPLIT = re.compile(r"(?<=[。；!?？！])")


def parse_markdown(md: str) -> tuple[list[Unit], list[str]]:
    units: list[Unit] = []
    skipped: list[str] = []
    section = ""
    counter = 0
    in_code = False
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
        for piece in SENT_SPLIT.split(text):
            piece = piece.strip().lstrip("-*· ").strip()
            if len(piece) < 4:
                continue
            counter += 1
            units.append(Unit(sid=f"s{counter:03d}", text=piece, section=section, line=line))

    lines = md.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        ln = i + 1
        i += 1
        if raw.strip().startswith("```"):
            if in_code:
                in_code = False
                skipped.append(f"L{ln} 代码块结束")
            else:
                flush_para()
                in_code = True
                skipped.append(f"L{ln} 代码块开始")
            continue
        if in_code:
            continue
        stripped = raw.strip()
        if stripped.startswith("|"):
            flush_para()
            skipped.append(f"L{ln} 表格")
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
            section = f"{title}" if level <= 1 else f"{section.split(' > ')[0]} > {title}" if section else title
            skipped.append(f"L{ln} 标题: {title}")
            continue
        if not stripped:
            flush_para()
            continue
        if re.match(r"^([-*·]|\d+[.、)])\s*", stripped):
            # 列表项独立成单元
            flush_para()
            item = stripped
            for piece in SENT_SPLIT.split(item):
                piece = piece.strip().lstrip("-*· ").strip()
                if len(piece) < 4:
                    continue
                counter += 1
                units.append(Unit(sid=f"s{counter:03d}", text=piece, section=section, line=ln))
            continue
        para_buf.append((stripped, ln))
    flush_para()
    return units, skipped


# ---------- 阶段一：句子级判定 ----------

NOUL_DEFS = {
    "meta": "该句是否属于元话语：仅在介绍、强调或包装后续内容（如「需要注意的是」「值得一提的是」「显然」「换句话说」「可以看到」），删除该句后语义不变。是 → yes。",
    "defensive": "该句是否属于防御性解释或预防误解式表达（如「并不意味着」「不要把X理解成A」「这不会导致误解」），即围绕假想误解反复解释，而非陈述真实规则。注意：真实的安全、数据、运维约束中的否定表达不是防御性解释，应答 no。",
    "process": "该句是否在描述文档产出或修改的工作过程、审计过程（如「经过分析」「我们发现」「上一版存在」「经过讨论决定」「为了避免误解」），而非最终事实。注意：设计决策的稳定依据（权衡、约束）不是过程语言，应答 no。",
    "reassurance": "该句是否属于影响面安抚句（如「无新增风险」「与现状一致」「仅涉及X，其他不变」且改动范围已由其他内容表达），主要作用是安抚而非提供信息。括号内的风险自证从句也算。真实的风险后果描述（如「需人工介入」）不算。",
    "dup": "该句表达的事实或规则是否可能在该文档的其他章节也已出现或被更详细地表述（粗筛，宁多勿漏）。同一规则在需求摘要、实现、异常分析中分别从不同角度出现属于常见情况，也算 yes。",
    "placeholder": "该句是否包含未收口的占位内容：TODO、待定值、示例值/示例 URL，且未显式标注为待确认项及确认责任人。注意：已显式写出待确认对象与动作的（如「联调前需与发送方核对后替换」）不算。",
}

ACTION_CRITERIA = {
    "keep": "保留：表达真实的事实、职责、约束、决策、接口、流程或验收标准，且表达方式适当",
    "delete": "删除后不影响读者理解、实施、运行或验证系统（元话语、安抚句、纯重复强调、无信息量句）",
    "rewrite": "包含有效信息但表达冗余或形式不当，需按转换算子改写（如 NEGATION→OWNERSHIP、WARNING→RULE、CLAIM→MECHANISM）",
    "merge": "与文档中其他位置的表述表达同一事实/规则，应合并到权威定义处，只删表述不删约束",
}

DENSITY_CRITERIA = [
    "高：提供新的事实、职责、约束、决策或验收标准",
    "中：部分重复但含少量补充信息或上下文",
    "低：主要承担过渡、强调、重复、安抚作用，删除后不损失有效信息",
]


def build_state(units: list[Unit], doc_type: str) -> dict:
    return {
        "doc_type": doc_type,
        "section_path": units[0].section,
        "sentences": [{"id": u.sid, "text": u.text} for u in units],
    }


def chunk_level_question(doc_type: str) -> tuple[str, Noul]:
    """块级判断：术语一致性（跨句判断，不适合按句拆分）。"""
    return "term_inconsistency", Noul(
        instructions=(
            f"阅读本组全部句子（文档类型 {doc_type}）。判断：是否存在同一概念/对象在"
            "不同句子中使用了不同的名称或写法（如同一字段一处叫 X 一处叫 Y、中英混用、"
            "大小写或下划线不一致）。仅统计确属同一实体的不一致，不同概念不算。"
        )
    )


def chunk_questions(units: list[Unit], doc_type: str) -> dict:
    qs: dict = {}
    for idx, u in enumerate(units):
        ref = f"`sentences[{idx}]`（id {u.sid}）"
        for key, ins in NOUL_DEFS.items():
            qs[f"{u.sid}_{key}"] = Noul(instructions=f"针对{ref}：{ins}")
        qs[f"{u.sid}_action"] = Choice(
            instructions=f"针对{ref}：在文档类型 {doc_type} 的发布稿中，该句应如何处置？",
            criteria=ACTION_CRITERIA,
        )
        qs[f"{u.sid}_density"] = Score(
            instructions=f"针对{ref}：该句的信息密度如何？",
            criteria=DENSITY_CRITERIA,
        )
    return qs


# ---------- 阶段二：跨章节重复与权威定义定位 ----------

def dup_state(units: list[Unit], full_doc: str, doc_type: str) -> dict:
    return {
        "doc_type": doc_type,
        "full_document": full_doc,
        "candidates": [{"id": u.sid, "section": u.section, "text": u.text} for u in units],
    }


def dup_questions(units: list[Unit]) -> dict:
    qs: dict = {}
    for idx, u in enumerate(units):
        ref = f"`candidates[{idx}]`（id {u.sid}，位于章节「{u.section}」）"
        qs[f"{u.sid}_dup"] = Choice(
            instructions=(
                f"针对{ref}：该句表达的事实/规则，与文档其他部分的表述是什么关系？"
                "仅依据 full_document 判断。"
            ),
            criteria={
                "duplicate": "其他章节已有等价或更权威的表述，本句应合并过去，只保留一处权威定义",
                "complementary": "其他章节有相近内容但角度不同，本句含独立补充信息，应保留",
                "unique": "文档中无其他等价表述，本句是唯一来源",
            },
        )
    return qs


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
    print(f"[parse] units={len(units)} skipped_marks={len(skipped)}", file=sys.stderr)

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
            row = {"sid": u.sid, "section": u.section, "line": u.line, "text": u.text}
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
            row["top_smell"] = max(smells, key=smells.get) if smells else None
            row["top_p"] = top
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

    # 阶段二：疑似重复句（阶段一 dup 仅为粗筛，饱和属预期，阶段二全文比对做真判别）
    dup_cands = [f for f in findings if f["smells"].get("dup", 0) >= T_DUP_ADMIT]
    if dup_cands:
        cand_units = [Unit(sid=f["sid"], text=f["text"], section=f["section"], line=f["line"]) for f in dup_cands]
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

    # 门控分组
    deletes, merges, rewrites, reviews = [], [], [], []
    for f in findings:
        top_p = f["top_p"]
        reassurance = f["smells"].get("reassurance", 0)
        density = f["density"] or 0
        if (
            f["action"] == "delete"
            and (f["action_confidence"] or 0) >= T_ACTION_CONF
            and top_p >= T_DELETE
        ) or (reassurance >= 0.85 and density >= 0.7):
            deletes.append(f)
        elif f.get("dup_relation") == "duplicate" and (f.get("dup_confidence") or 0) >= T_DUP:
            merges.append(f)
        elif f["action"] == "rewrite" and (f["action_confidence"] or 0) >= T_ACTION_CONF:
            rewrites.append(f)
        elif top_p >= T_REVIEW or (f.get("dup_relation") == "duplicate" and (f.get("dup_confidence") or 0) >= 0.55):
            reviews.append(f)

    # 报告
    def fmt(f: dict) -> str:
        smells = ", ".join(f"{k}:{v}" for k, v in sorted(f["smells"].items(), key=lambda kv: -kv[1]) if v >= 0.3)
        extra = ""
        if "dup_relation" in f:
            extra = f"；跨章比对: {f['dup_relation']}({f.get('dup_confidence', 0)})"
        return (
            f"- **[{f['sid']}] §{f['section']}**（L{f['line']}，action={f['action']}"
            f" conf={f['action_confidence']}，density={f['density']}）{extra}\n"
            f"  > {f['text']}\n"
            f"  坏味道概率: {smells or '—'}"
        )

    lines = [
        f"# Jev 发布稿扫描报告：{src.name}",
        "",
        f"- 文档类型: {args.doc_type}｜单元数: {len(units)}｜模型: {MODEL}",
        f"- 阈值: delete(noul≥{T_DELETE}, action_conf≥{T_ACTION_CONF})｜merge(dup_conf≥{T_DUP})｜review(noul≥{T_REVIEW})",
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
