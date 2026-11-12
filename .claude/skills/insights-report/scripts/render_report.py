#!/usr/bin/env python3
"""Render the insights-report HTML from stats.json and analysis.json."""

import argparse
import html
import json
import re
from datetime import datetime
from pathlib import Path

ASSET_CSS = Path(__file__).resolve().parent.parent / "assets" / "style.css"

AGENT_LABELS = {"claude": "Claude Code", "codex": "Codex", "omp": "omp", "pi": "pi"}

LABELS = {
    "debug_investigate": "Debug/Investigate", "implement_feature": "Implement Feature",    "fix_bug": "Fix Bug", "write_script_tool": "Write Script/Tool", "refactor_code": "Refactor Code",
    "configure_system": "Configure System", "create_pr_commit": "Create PR/Commit",
    "analyze_data": "Analyze Data", "understand_codebase": "Understand Codebase",
    "write_tests": "Write Tests", "write_docs": "Write Docs", "deploy_infra": "Deploy/Infra",
    "warmup_minimal": "Cache Warmup", "fast_accurate_search": "Fast/Accurate Search",
    "correct_code_edits": "Correct Code Edits", "good_explanations": "Good Explanations",
    "proactive_help": "Proactive Help", "multi_file_changes": "Multi-file Changes",
    "handled_complexity": "Multi-file Changes", "good_debugging": "Good Debugging",
    "misunderstood_request": "Misunderstood Request", "wrong_approach": "Wrong Approach",
    "buggy_code": "Buggy Code", "user_rejected_action": "User Rejected Action",
    "claude_got_blocked": "Claude Got Blocked", "user_stopped_early": "User Stopped Early",
    "wrong_file_or_location": "Wrong File/Location", "excessive_changes": "Excessive Changes",
    "slow_or_verbose": "Slow/Verbose", "tool_failed": "Tool Failed", "user_unclear": "User Unclear",
    "external_issue": "External Issue", "frustrated": "Frustrated", "dissatisfied": "Dissatisfied",
    "likely_satisfied": "Likely Satisfied", "satisfied": "Satisfied", "happy": "Happy",
    "unsure": "Unsure", "neutral": "Neutral", "delighted": "Delighted", "single_task": "Single Task",
    "multi_task": "Multi Task", "iterative_refinement": "Iterative Refinement",
    "exploration": "Exploration", "quick_question": "Quick Question",
    "fully_achieved": "Fully Achieved", "mostly_achieved": "Mostly Achieved",
    "partially_achieved": "Partially Achieved", "not_achieved": "Not Achieved",
    "unclear_from_transcript": "Unclear", "unhelpful": "Unhelpful",
    "slightly_helpful": "Slightly Helpful", "moderately_helpful": "Moderately Helpful",
    "very_helpful": "Very Helpful", "essential": "Essential",
}


def esc(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def label(key):
    return LABELS.get(key, str(key).replace("_", " ").title())


def rich(text):
    """Escape then apply the small Markdown subset the prompts produce."""
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def paragraphs(text):
    if not text:
        return ""
    blocks = [b.strip() for b in str(text).split("\n\n") if b.strip()]
    out = []
    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if lines and all(line.startswith(("- ", "• ")) for line in lines):
            out.append("<ul>" + "".join(
                f"<li>{rich(line[2:])}</li>" for line in lines
            ) + "</ul>")
        else:
            out.append(f"<p>{rich(' '.join(lines))}</p>")
    return "".join(out)


def bar_chart(mapping, color, limit=6, order=None):
    mapping = mapping or {}
    if order:
        items = [(key, mapping.get(key, 0)) for key in order if mapping.get(key, 0) > 0]
    else:
        items = sorted(mapping.items(), key=lambda kv: -kv[1])[:limit]
    if not items:
        return '<p class="empty">No data</p>'
    maximum = max(value for _, value in items) or 1
    rows = []
    for key, value in items:
        width = value / maximum * 100
        rows.append(
            '<div class="bar-row">'
            f'<div class="bar-label">{esc(label(key))}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{width:.1f}%;background:{color}"></div></div>'
            f'<div class="bar-value">{value}</div>'
            "</div>"
        )
    return "".join(rows)


def response_time_chart(values):
    buckets = [("2-10s", 0), ("10-30s", 0), ("30s-1m", 0), ("1-2m", 0),
               ("2-5m", 0), ("5-15m", 0), (">15m", 0)]
    counts = {name: 0 for name, _ in buckets}
    for value in values or []:
        if value < 10:
            counts["2-10s"] += 1
        elif value < 30:
            counts["10-30s"] += 1
        elif value < 60:
            counts["30s-1m"] += 1
        elif value < 120:
            counts["1-2m"] += 1
        elif value < 300:
            counts["2-5m"] += 1
        elif value < 900:
            counts["5-15m"] += 1
        else:
            counts[">15m"] += 1
    return bar_chart(counts, "#6366f1", order=[name for name, _ in buckets])


def hour_chart(hours):
    groups = [
        ("Morning (6-12)", {6, 7, 8, 9, 10, 11}),
        ("Afternoon (12-18)", {12, 13, 14, 15, 16, 17}),
        ("Evening (18-24)", {18, 19, 20, 21, 22, 23}),
        ("Night (0-6)", {0, 1, 2, 3, 4, 5}),
    ]
    counts = {name: 0 for name, _ in groups}
    for hour in hours or []:
        for name, members in groups:
            if hour in members:
                counts[name] += 1
                break
    return bar_chart(counts, "#8b5cf6", order=[name for name, _ in groups])


def section_stats(stats):
    lines = stats.get("total_lines_added", 0)
    removed = stats.get("total_lines_removed", 0)
    return [
        (f"{stats.get('total_messages', 0):,}", "Messages"),
        (f"+{lines:,}/-{removed:,}", "Lines"),
        (f"{stats.get('total_files_modified', 0):,}", "Files"),
        (f"{stats.get('days_active', 0)}", "Days"),
        (f"{stats.get('messages_per_day', 0)}", "Msgs/Day"),
    ]


def render(stats, analysis):
    glance = analysis.get("at_a_glance") or {}
    areas = (analysis.get("project_areas") or {}).get("areas") or []
    style = (analysis.get("interaction_style") or {})
    works = (analysis.get("what_works") or {})
    friction = (analysis.get("friction_analysis") or {})
    suggestions = (analysis.get("suggestions") or {})
    horizon = (analysis.get("on_the_horizon") or {})
    fun = (analysis.get("fun_ending") or {})

    start = stats.get("date_range", {}).get("start", "")
    end = stats.get("date_range", {}).get("end", "")
    agent_counts = stats.get("agent_counts") or {}
    agent_text = ", ".join(
        f"{AGENT_LABELS.get(key, key)} {value}"
        for key, value in sorted(agent_counts.items(), key=lambda kv: -kv[1])
    )
    subtitle = (
        f"{stats.get('total_messages', 0):,} messages across "
        f"{stats.get('total_sessions', 0)} sessions"
        + (f" ({stats.get('total_sessions_scanned')} total)" if stats.get("total_sessions_scanned") else "")
        + (f" | {agent_text}" if agent_text else "")
        + f" | {start} to {end}"
    )

    glance_html = ""
    if glance:
        rows = []
        for key, anchor, label_text in [
            ("whats_working", "#section-wins", "What's working"),
            ("whats_hindering", "#section-friction", "What's hindering you"),
            ("quick_wins", "#section-features", "Quick wins to try"),
            ("ambitious_workflows", "#section-horizon", "Ambitious workflows"),
        ]:
            if glance.get(key):
                rows.append(
                    f'<div class="glance-section"><strong>{label_text}:</strong> '
                    f'{rich(glance[key])} <a href="{anchor}" class="see-more">See more →</a></div>'
                )
        if rows:
            glance_html = (
                '<div class="at-a-glance"><div class="glance-title">At a Glance</div>'
                '<div class="glance-sections">' + "".join(rows) + "</div></div>"
            )

    area_html = "".join(
        '<div class="project-area">'
        f'<div class="area-header"><span class="area-name">{esc(area.get("name"))}</span>'
        f'<span class="area-count">~{esc(area.get("session_count", ""))} sessions</span></div>'
        f'<div class="area-desc">{rich(area.get("description"))}</div></div>'
        for area in areas
    ) or '<p class="empty">No project areas generated</p>'

    wins_html = "".join(
        '<div class="big-win">'
        f'<div class="big-win-title">{esc(item.get("title"))}</div>'
        f'<div class="big-win-desc">{rich(item.get("description"))}</div></div>'
        for item in works.get("impressive_workflows") or []
    ) or '<p class="empty">No wins generated</p>'

    friction_html = "".join(
        '<div class="friction-category">'
        f'<div class="friction-title">{esc(item.get("category"))}</div>'
        f'<div class="friction-desc">{rich(item.get("description"))}</div>'
        + ("<ul class=\"friction-examples\">" + "".join(
            f"<li>{rich(example)}</li>" for example in item.get("examples") or []
        ) + "</ul>" if item.get("examples") else "")
        + "</div>"
        for item in friction.get("categories") or []
    ) or '<p class="empty">No friction categories generated</p>'

    claude_md = "".join(
        '<div class="claude-md-item">'
        f'<code class="cmd-code">{esc(item.get("addition"))}</code>'
        f'<div class="cmd-why">{rich(item.get("why"))}</div></div>'
        for item in suggestions.get("claude_md_additions") or []
    )
    claude_md_html = (
        '<div class="claude-md-section"><h3>Suggested CLAUDE.md Additions</h3>'
        + (claude_md or '<p class="empty">None suggested</p>')
        + "</div>"
    )

    features_html = "".join(
        '<div class="feature-card">'
        f'<div class="feature-title">{esc(item.get("feature"))}</div>'
        f'<div class="feature-oneliner">{rich(item.get("one_liner"))}</div>'
        f'<div class="feature-why">{rich(item.get("why_for_you"))}</div>'
        + (f'<div class="feature-examples"><div class="feature-example">'
           f'<code class="example-code">{esc(item.get("example_code"))}</code></div></div>'
           if item.get("example_code") else "")
        + "</div>"
        for item in suggestions.get("features_to_try") or []
    ) or '<p class="empty">No features suggested</p>'

    patterns_html = "".join(
        '<div class="pattern-card">'
        f'<div class="pattern-title">{esc(item.get("title"))}</div>'
        f'<div class="pattern-summary">{rich(item.get("suggestion"))}</div>'
        f'<div class="pattern-detail">{rich(item.get("detail"))}</div>'
        + (f'<div class="pattern-prompt"><div class="prompt-label">Try this prompt</div>'
           f'<code>{esc(item.get("copyable_prompt"))}</code></div>'
           if item.get("copyable_prompt") else "")
        + "</div>"
        for item in suggestions.get("usage_patterns") or []
    ) or '<p class="empty">No usage patterns suggested</p>'

    horizon_html = "".join(
        '<div class="horizon-card">'
        f'<div class="horizon-title">{esc(item.get("title"))}</div>'
        f'<div class="horizon-possible">{rich(item.get("whats_possible"))}</div>'
        + (f'<div class="horizon-tip"><strong>How to try:</strong> {rich(item.get("how_to_try"))}</div>'
           if item.get("how_to_try") else "")
        + (f'<div class="pattern-prompt"><div class="prompt-label">Copyable prompt</div>'
           f'<code>{esc(item.get("copyable_prompt"))}</code></div>'
           if item.get("copyable_prompt") else "")
        + "</div>"
        for item in horizon.get("opportunities") or []
    ) or '<p class="empty">No opportunities generated</p>'

    fun_html = ""
    if fun.get("headline"):
        fun_html = (
            '<div class="fun-ending">'
            f'<div class="fun-headline">{rich(fun.get("headline"))}</div>'
            f'<div class="fun-detail">{rich(fun.get("detail"))}</div></div>'
        )

    stats_html = "".join(
        f'<div class="stat"><div class="stat-value">{esc(value)}</div>'
        f'<div class="stat-label">{esc(name)}</div></div>'
        for value, name in section_stats(stats)
    )

    toc = [
        ("#section-work", "What You Work On"),
        ("#section-usage", "How You Use Agents"),
        ("#section-wins", "Impressive Things You Did"),
        ("#section-friction", "Where Things Go Wrong"),
        ("#section-features", "Features to Try"),
        ("#section-patterns", "New Ways to Use Agents"),
        ("#section-horizon", "On the Horizon"),
    ]
    toc_html = '<nav class="nav-toc">' + "".join(
        f'<a href="{href}">{esc(name)}</a>' for href, name in toc
    ) + "</nav>"

    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Coding Agent Insights</title>
  <style>
{Path(ASSET_CSS).read_text(encoding="utf-8")}
  </style>
</head>
<body>
  <div class="container">
    <h1>Coding Agent Insights</h1>
    <p class="subtitle">{esc(subtitle)}</p>
    {glance_html}
    <div class="stats-row">{stats_html}</div>
    {toc_html}

    <h2 id="section-work">What You Work On</h2>
    <div class="project-areas">{area_html}</div>

    <h2 id="section-usage">How You Use Agents</h2>
    <div class="narrative">{paragraphs(style.get("narrative"))}</div>
    {f'<div class="key-insight"><strong>Key pattern:</strong> {rich(style.get("key_pattern"))}</div>' if style.get("key_pattern") else ""}
    <div class="charts-row">
      <div class="chart-card"><div class="chart-title">Agents</div>{bar_chart(agent_counts, "#f59e0b")}</div>
      <div class="chart-card"><div class="chart-title">Top Tools</div>{bar_chart(stats.get("tool_counts"), "#2563eb", 8)}</div>
    </div>
    <div class="charts-row">
      <div class="chart-card"><div class="chart-title">Languages</div>{bar_chart(stats.get("languages"), "#0891b2", 8)}</div>
      <div class="chart-card"><div class="chart-title">Session Types</div>{bar_chart(stats.get("session_types"), "#0d9488")}</div>
    </div>
    <div class="charts-row">
      <div class="chart-card"><div class="chart-title">Outcomes</div>{bar_chart(stats.get("outcomes"), "#8b5cf6")}</div>
      <div class="chart-card"><div class="chart-title">Time of Day</div>{hour_chart(stats.get("message_hours"))}</div>
    </div>
    <div class="chart-card"><div class="chart-title">Response Times</div>{response_time_chart(stats.get("user_response_times"))}</div>

    <h2 id="section-wins">Impressive Things You Did</h2>
    {f'<p class="section-intro">{rich(works.get("intro"))}</p>' if works.get("intro") else ""}
    <div class="big-wins">{wins_html}</div>

    <h2 id="section-friction">Where Things Go Wrong</h2>
    {f'<p class="section-intro">{rich(friction.get("intro"))}</p>' if friction.get("intro") else ""}
    <div class="charts-row">
      <div class="chart-card"><div class="chart-title">Primary Friction Types</div>{bar_chart(stats.get("friction"), "#dc2626")}</div>
      <div class="chart-card"><div class="chart-title">Inferred Satisfaction</div>{bar_chart(stats.get("satisfaction"), "#eab308")}</div>
    </div>
    <div class="friction-categories">{friction_html}</div>

    <h2 id="section-features">Existing Agent Features to Try</h2>
    <div class="features-section">{features_html}</div>
    {claude_md_html}

    <h2 id="section-patterns">New Ways to Use Agents</h2>
    <div class="patterns-section">{patterns_html}</div>

    <h2 id="section-horizon">On the Horizon</h2>
    {f'<p class="section-intro">{rich(horizon.get("intro"))}</p>' if horizon.get("intro") else ""}
    <div class="horizon-section">{horizon_html}</div>
    {fun_html}
  </div>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stats", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    stats = json.loads(args.stats.read_text(encoding="utf-8"))
    analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
    html_text = render(stats, analysis)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html_text, encoding="utf-8")
    print(f"report: {args.out}")


if __name__ == "__main__":
    main()
