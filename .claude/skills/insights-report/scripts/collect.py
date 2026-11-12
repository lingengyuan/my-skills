#!/usr/bin/env python3
"""Collect coding-agent session statistics for the insights-report skill.

Supports Claude Code, Codex, and pi. Each agent has its own adapter that
normalizes transcripts into one message model. All later metrics are computed
from that model, so adding an agent means adding one reader.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

CLAUDE_DIR = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
PROJECTS_DIR = CLAUDE_DIR / "projects"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
PI_HOME = Path(os.environ.get("PI_HOME", Path.home() / ".pi"))
OMP_HOME = Path(os.environ.get("OMP_HOME", Path.home() / ".omp"))
BUILTIN_FACETS_DIR = CLAUDE_DIR / "usage-data" / "facets"
DEFAULT_OUT = CLAUDE_DIR / "usage-data" / "insights-skill"

AGENT_LABELS = {"claude": "Claude Code", "codex": "Codex", "omp": "omp", "pi": "pi"}

LANGUAGE_BY_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".jsx": "JavaScript", ".py": "Python", ".rb": "Ruby", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".c": "C", ".h": "C", ".cpp": "C++",
    ".cc": "C++", ".cxx": "C++", ".hpp": "C++", ".hh": "C++", ".hxx": "C++",
    ".ipp": "C++", ".md": "Markdown", ".json": "JSON", ".yaml": "YAML",
    ".yml": "YAML", ".sh": "Shell", ".css": "CSS", ".html": "HTML",
}

TOOL_NAME_MAP = {
    "claude": {},
    "codex": {
        "exec_command": "Bash", "apply_patch": "Edit", "view_image": "Read",
        "spawn_agent": "Agent", "wait_agent": "Agent",
    },
    "pi": {"bash": "Bash", "edit": "Edit", "write": "Write", "read": "Read"},
    "omp": {"bash": "Bash", "edit": "Edit", "write": "Write", "read": "Read"},
}

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
TASK_TOOLS = {"Task", "Agent"}
WRITE_TOOLS = {"Write"}
EDIT_LIKE_TOOLS = {"Edit", "MultiEdit", "NotebookEdit"}

ERROR_PATTERNS = [
    (("exit code",), "Command Failed"),
    (("rejected", "doesn't want"), "User Rejected"),
    (("string to replace not found", "no changes"), "Edit Failed"),
    (("modified since read",), "File Changed"),
    (("exceeds maximum", "too large"), "File Too Large"),
    (("file not found", "does not exist"), "File Not Found"),
]


def parse_ts(value):
    if isinstance(value, (int, float)):
        seconds = value / 1000 if value > 1e11 else value
        try:
            return datetime.fromtimestamp(seconds, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def iter_jsonl(path):
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def error_category(content):
    if not isinstance(content, str):
        return "Other"
    low = content.lower()
    for needles, label in ERROR_PATTERNS:
        if any(n in low for n in needles):
            return label
    return "Other"


def codex_error(text):
    """Codex outputs carry an exit code; generic 'error:' text is too noisy."""
    return bool(
        re.search(r"exit code:?\s*[1-9]", text or "", re.I)
        or re.search(r'"exit_code"\s*:\s*[1-9]', text or "")
        or re.search(r'"status"\s*:\s*"failed"', text or "")
    )


def clean_codex_user_text(text):
    if "## My request:" in text:
        text = text.split("## My request:", 1)[1]
    text = re.sub(r"<environment_context>.*$", "", text, flags=re.S)
    text = re.sub(r"<INSTRUCTIONS>.*?</INSTRUCTIONS>", "", text, flags=re.S)
    return text.strip()


def diff_lines(old, new):
    counts = Counter(old.split("\n"))
    added = 0
    for line in new.split("\n"):
        seen = counts.get(line, 0)
        counts[line] = seen - 1
        if seen <= 0:
            added += 1
    removed = sum(max(v, 0) for v in counts.values())
    return added, removed


def parse_json_args(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {"input": value}
        except json.JSONDecodeError:
            return {"input": value}
    return {}


def normalize_tool_name(agent, name):
    return TOOL_NAME_MAP.get(agent, {}).get(name, name)


def tool_paths(agent, tool, args, raw):
    paths = []
    for key in ("file_path", "path"):
        value = args.get(key)
        if isinstance(value, str) and value:
            paths.append(value)
    for value in args.get("paths") or []:
        if isinstance(value, str) and value:
            paths.append(value)
    if agent == "codex" and tool == "Edit" and raw:
        paths.extend(re.findall(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", raw, re.M))
    if agent == "pi" and tool == "Edit":
        for item in args.get("edits") or []:
            if isinstance(item, dict) and item.get("path"):
                paths.append(item["path"])
    return paths


def tool_command(agent, tool, args, raw):
    if tool == "Bash":
        command = args.get("command") or args.get("cmd")
        if isinstance(command, str):
            return command
    if agent == "codex" and raw and tool in ("exec", "js"):
        return raw
    return ""


def text_from_blocks(blocks):
    if isinstance(blocks, str):
        return blocks
    if not isinstance(blocks, list):
        return ""
    parts = []
    for block in blocks:
        if isinstance(block, dict) and block.get("type") in ("text", "input_text", "output_text", "Text"):
            text = block.get("text")
            if isinstance(text, str) and text:
                parts.append(text)
    return "\n".join(parts)


def result_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return text_from_blocks(value)
    if isinstance(value, dict):
        return text_from_blocks(value.get("content"))
    return ""


# --- Claude Code ---------------------------------------------------------

def read_claude(path):
    session_id = path.stem
    cwd = ""
    permission_mode = ""
    messages = []
    first_ts = last_ts = None

    for entry in iter_jsonl(path):
        if entry.get("isSidechain"):
            continue
        kind = entry.get("type")
        if kind not in ("user", "assistant"):
            continue
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        session_id = entry.get("sessionId") or session_id
        cwd = cwd or entry.get("cwd") or ""
        permission_mode = permission_mode or entry.get("permissionMode") or ""
        ts = parse_ts(entry.get("timestamp"))
        if ts:
            first_ts = ts if first_ts is None or ts < first_ts else first_ts
            last_ts = ts if last_ts is None or ts > last_ts else last_ts

        content = message.get("content")
        if kind == "assistant":
            calls = []
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        calls.append({
                            "name": block.get("name") or "",
                            "input": block.get("input") if isinstance(block.get("input"), dict) else {},
                            "raw": "",
                        })
            usage = message.get("usage") if isinstance(message.get("usage"), dict) else {}
            messages.append({
                "role": "assistant", "timestamp": ts, "text": text_from_blocks(content),
                "tool_calls": calls,
                "usage": {"input": usage.get("input_tokens") or 0,
                          "output": usage.get("output_tokens") or 0},
            })
        else:
            text = text_from_blocks(content)
            if text.strip():
                messages.append({"role": "user", "timestamp": ts, "text": text,
                                 "tool_calls": [], "usage": {}})
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        messages.append({
                            "role": "tool", "timestamp": ts, "text": "",
                            "tool_calls": [], "usage": {},
                            "tool_result": {
                                "is_error": bool(block.get("is_error")),
                                "content": result_text(block.get("content")),
                            },
                        })

    return {
        "agent": "claude", "session_id": session_id, "project_path": cwd,
        "permission_mode": permission_mode, "messages": messages,
        "first_ts": first_ts, "last_ts": last_ts, "mtime": path.stat().st_mtime,
    }


# --- Codex ---------------------------------------------------------------

def read_codex(path):
    session_id = path.stem
    cwd = ""
    approval = ""
    messages = []
    first_ts = last_ts = None

    for entry in iter_jsonl(path):
        kind = entry.get("type")
        payload = entry.get("payload") if isinstance(entry.get("payload"), dict) else {}
        ts = parse_ts(entry.get("timestamp"))
        if ts:
            first_ts = ts if first_ts is None or ts < first_ts else first_ts
            last_ts = ts if last_ts is None or ts > last_ts else last_ts

        if kind == "session_meta":
            session_id = payload.get("session_id") or payload.get("id") or session_id
            cwd = payload.get("cwd") or cwd
            continue
        if kind == "turn_context":
            approval = payload.get("approval_policy") or approval
            cwd = payload.get("cwd") or cwd
            continue
        if kind == "token_usage_record":
            usage = payload.get("usage") if isinstance(payload.get("usage"), dict) else {}
            messages.append({
                "role": "usage", "timestamp": ts, "text": "", "tool_calls": [],
                "usage": {"input": usage.get("input_tokens") or 0,
                          "output": usage.get("output_tokens") or 0},
            })
            continue
        if kind == "event_msg":
            event = payload.get("type")
            if event == "turn_aborted":
                messages.append({"role": "user", "timestamp": ts,
                                 "text": "[Request interrupted by user]",
                                 "tool_calls": [], "usage": {}})
            elif event == "item_completed":
                item = payload.get("item") if isinstance(payload.get("item"), dict) else {}
                item_type = item.get("type")
                if item_type == "UserMessage":
                    text = clean_codex_user_text(text_from_blocks(item.get("content")))
                    if text:
                        messages.append({"role": "user", "timestamp": ts, "text": text,
                                         "tool_calls": [], "usage": {}})
                elif item_type == "AgentMessage":
                    text = text_from_blocks(item.get("content"))
                    if text.strip():
                        messages.append({"role": "assistant", "timestamp": ts, "text": text,
                                         "tool_calls": [], "usage": {}})
            elif event in ("user_message", "agent_message"):
                text = result_text(payload.get("message"))
                if text.strip():
                    messages.append({
                        "role": "user" if event == "user_message" else "assistant",
                        "timestamp": ts, "text": text, "tool_calls": [], "usage": {},
                    })
            continue
        if kind != "response_item":
            continue

        item = payload.get("type")
        if item == "message":
            # response_item messages either duplicate item_completed or inject context.
            continue
        if item in ("function_call", "custom_tool_call"):
            raw = payload.get("arguments") if item == "function_call" else payload.get("input")
            args = parse_json_args(raw)
            messages.append({
                "role": "assistant", "timestamp": ts, "text": "",
                "tool_calls": [{"name": payload.get("name") or "", "input": args,
                                "raw": raw if isinstance(raw, str) else "",
                                "namespace": payload.get("namespace") or ""}],
                "usage": {},
            })
        elif item in ("function_call_output", "custom_tool_call_output"):
            text = result_text(payload.get("output"))
            messages.append({
                "role": "tool", "timestamp": ts, "text": "", "tool_calls": [], "usage": {},
                "tool_result": {"is_error": codex_error(text), "content": text},
            })

    return {
        "agent": "codex", "session_id": session_id, "project_path": cwd,
        "permission_mode": approval, "messages": messages,
        "first_ts": first_ts, "last_ts": last_ts, "mtime": path.stat().st_mtime,
    }


# --- pi ------------------------------------------------------------------

def read_pi(path, agent="pi"):
    session_id = path.stem
    cwd = ""
    messages = []
    first_ts = last_ts = None

    for entry in iter_jsonl(path):
        kind = entry.get("type")
        ts = parse_ts(entry.get("timestamp"))
        if kind == "session":
            session_id = entry.get("id") or session_id
            cwd = entry.get("cwd") or cwd
            ts = ts or parse_ts(entry.get("timestamp"))
        elif kind == "message":
            message = entry.get("message") if isinstance(entry.get("message"), dict) else {}
            ts = ts or parse_ts(message.get("timestamp"))
            role = message.get("role")
            content = message.get("content")
            usage = message.get("usage") if isinstance(message.get("usage"), dict) else {}
            if role == "assistant":
                calls = []
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "toolCall":
                            calls.append({
                                "name": block.get("name") or "",
                                "input": block.get("arguments") if isinstance(block.get("arguments"), dict) else {},
                                "raw": "",
                            })
                messages.append({
                    "role": "assistant", "timestamp": ts, "text": text_from_blocks(content),
                    "tool_calls": calls,
                    "usage": {"input": usage.get("input") or 0,
                              "output": usage.get("output") or 0},
                })
            elif role == "user":
                text = text_from_blocks(content)
                if text.strip():
                    messages.append({"role": "user", "timestamp": ts, "text": text,
                                     "tool_calls": [], "usage": {}})
            elif role == "toolResult":
                text = result_text(content)
                messages.append({
                    "role": "tool", "timestamp": ts, "text": "", "tool_calls": [], "usage": {},
                    "tool_result": {"is_error": bool(message.get("isError")), "content": text},
                })
        if ts:
            first_ts = ts if first_ts is None or ts < first_ts else first_ts
            last_ts = ts if last_ts is None or ts > last_ts else last_ts

    return {
        "agent": agent, "session_id": session_id, "project_path": cwd,
        "permission_mode": "", "messages": messages,
        "first_ts": first_ts, "last_ts": last_ts, "mtime": path.stat().st_mtime,
    }


class CodexRPCError(RuntimeError):
    pass


class CodexRPC:
    """Minimal JSON-RPC client for `codex app-server`."""

    def __init__(self, timeout=60):
        binary = os.environ.get("CODEX_BIN") or shutil.which("codex")
        if not binary:
            raise CodexRPCError("codex not found")
        self.proc = subprocess.Popen(
            [binary, "app-server"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1,
        )
        self._lock = threading.Lock()
        self._events = {}
        self._results = {}
        self._next_id = 1
        self._closed = False
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            request_id = message.get("id")
            with self._lock:
                event = self._events.get(request_id)
                if event is not None:
                    self._results[request_id] = message
                    event.set()

    def call(self, method, params=None, timeout=60):
        with self._lock:
            request_id = self._next_id
            self._next_id += 1
            event = threading.Event()
            self._events[request_id] = event
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}
        try:
            self.proc.stdin.write(json.dumps(payload) + "\n")
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise CodexRPCError(f"app-server write failed: {exc}") from exc
        if not event.wait(timeout):
            raise CodexRPCError(f"app-server timeout on {method}")
        with self._lock:
            message = self._results.pop(request_id, None)
            self._events.pop(request_id, None)
        if message is None:
            raise CodexRPCError(f"app-server returned no response for {method}")
        if message.get("error"):
            raise CodexRPCError(f"app-server error on {method}: {message['error']}")
        return message.get("result") or {}

    def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            try:
                self.proc.kill()
            except OSError:
                pass


def codex_rpc_items(rpc, thread_id):
    items = []
    cursor = None
    while True:
        params = {"threadId": thread_id, "limit": 500}
        if cursor:
            params["cursor"] = cursor
        result = rpc.call("thread/items/list", params, timeout=120)
        items.extend(result.get("data") or [])
        cursor = result.get("nextCursor")
        if not cursor:
            break
    return items


def codex_items_to_messages(entries):
    messages = []
    for entry in entries:
        item = entry.get("item") if isinstance(entry.get("item"), dict) else entry
        kind = item.get("type")
        ts = parse_ts(item.get("startedAtMs") or item.get("completedAtMs") or entry.get("startedAtMs"))

        if kind == "userMessage":
            text = text_from_blocks(item.get("content"))
            if text.strip():
                messages.append({"role": "user", "timestamp": ts, "text": text,
                                 "tool_calls": [], "usage": {}})
        elif kind == "agentMessage":
            text = item.get("text") or ""
            if text.strip():
                messages.append({"role": "assistant", "timestamp": ts, "text": text,
                                 "tool_calls": [], "usage": {}})
        elif kind == "commandExecution":
            command = item.get("command") or ""
            messages.append({
                "role": "assistant", "timestamp": ts, "text": "",
                "tool_calls": [{"name": "Bash",
                                "input": {"command": command, "cwd": item.get("cwd") or ""},
                                "raw": ""}],
                "usage": {},
            })
            messages.append({
                "role": "tool", "timestamp": ts, "text": "", "tool_calls": [], "usage": {},
                "tool_result": {
                    "is_error": item.get("exitCode") not in (0, None),
                    "content": item.get("aggregatedOutput") or "",
                },
            })
        elif kind == "mcpToolCall":
            server = item.get("server") or ""
            tool = item.get("tool") or ""
            name = f"mcp__{server}__{tool}" if server else f"mcp__{tool}"
            args = item.get("arguments") if isinstance(item.get("arguments"), dict) else {}
            messages.append({
                "role": "assistant", "timestamp": ts, "text": "",
                "tool_calls": [{"name": name, "input": args, "raw": ""}], "usage": {},
            })
            error = item.get("error")
            result = item.get("result")
            messages.append({
                "role": "tool", "timestamp": ts, "text": "", "tool_calls": [], "usage": {},
                "tool_result": {
                    "is_error": bool(error),
                    "content": result_text(result) if result is not None else str(error or ""),
                },
            })
        elif kind == "fileChange":
            changes = [c for c in item.get("changes") or [] if isinstance(c, dict)]
            paths = [c.get("path") for c in changes if c.get("path")]
            added = removed = 0
            patches = []
            for change in changes:
                diff = change.get("diff") or ""
                patches.append(diff)
                if (change.get("kind") or {}).get("type") == "add":
                    added += diff.count("\n") + 1
                else:
                    for line in diff.split("\n"):
                        if line.startswith("+") and not line.startswith("+++"):
                            added += 1
                        elif line.startswith("-") and not line.startswith("---"):
                            removed += 1
            messages.append({
                "role": "assistant", "timestamp": ts, "text": "",
                "tool_calls": [{
                    "name": "Edit",
                    "input": {"paths": paths, "path": paths[0] if paths else "",
                              "added_lines": added, "removed_lines": removed},
                    "raw": "\n".join(patches),
                }],
                "usage": {},
            })
        elif kind == "webSearch":
            messages.append({
                "role": "assistant", "timestamp": ts, "text": "",
                "tool_calls": [{"name": "WebSearch",
                                "input": {"query": item.get("query") or ""}, "raw": ""}],
                "usage": {},
            })
        elif kind == "imageView":
            messages.append({
                "role": "assistant", "timestamp": ts, "text": "",
                "tool_calls": [{"name": "Read", "input": {"path": item.get("path") or ""}, "raw": ""}],
                "usage": {},
            })
        elif kind in ("subAgentActivity", "collabAgentToolCall"):
            messages.append({
                "role": "assistant", "timestamp": ts, "text": "",
                "tool_calls": [{"name": "Agent", "input": {}, "raw": ""}], "usage": {},
            })
        elif kind == "functionCallOutput":
            text = result_text(item.get("output"))
            messages.append({
                "role": "tool", "timestamp": ts, "text": "", "tool_calls": [], "usage": {},
                "tool_result": {"is_error": codex_error(text), "content": text},
            })
        elif kind == "dynamicToolCall":
            messages.append({
                "role": "assistant", "timestamp": ts, "text": "",
                "tool_calls": [{"name": item.get("tool") or "tool", "input": {}, "raw": ""}],
                "usage": {},
            })
    return messages


def fetch_codex_rpc(days, meta_dir, max_threads):
    """Read threads through Codex's built-in app-server instead of rollout files."""
    rpc = CodexRPC()
    try:
        rpc.call("initialize", {
            "clientInfo": {"name": "insights-report", "version": "1.0"},
            "capabilities": {"experimentalApi": True},
        })
        threads = []
        cursor = None
        while len(threads) < max_threads:
            params = {
                "limit": min(100, max_threads - len(threads)),
                "sortKey": "updated_at",
                "sortDirection": "desc",
            }
            if cursor:
                params["cursor"] = cursor
            result = rpc.call("thread/list", params)
            data = result.get("data") or []
            threads.extend(data)
            cursor = result.get("nextCursor")
            if not cursor or not data:
                break

        cutoff = time.time() - days * 86400 if days > 0 else None
        metas = []
        for thread in threads:
            updated = thread.get("updatedAt") or 0
            if cutoff and updated < cutoff:
                continue
            if thread.get("ephemeral"):
                continue
            source = thread.get("threadSource") or thread.get("source") or ""
            if str(source).startswith("subAgent"):
                continue
            session_id = thread.get("id") or thread.get("sessionId")
            if not session_id:
                continue
            cache_path = meta_dir / cache_name("codex", session_id)
            cached = load_cached_meta(cache_path, updated)
            if cached:
                metas.append(cached)
                continue
            items = codex_rpc_items(rpc, session_id)
            session = {
                "agent": "codex",
                "session_id": session_id,
                "project_path": thread.get("cwd") or "",
                "permission_mode": "",
                "messages": codex_items_to_messages(items),
                "first_ts": parse_ts(thread.get("createdAt")),
                "last_ts": parse_ts(updated),
                "mtime": updated,
            }
            meta = compute_meta(session)
            meta["transcript"] = transcript_digest(session)
            save_meta(cache_path, meta)
            metas.append(meta)
        return metas
    finally:
        rpc.close()


READERS = {"claude": read_claude, "codex": read_codex, "pi": read_pi,
           "omp": lambda path: read_pi(path, "omp")}


def iter_sessions(agents):
    seen = set()
    if "claude" in agents and PROJECTS_DIR.is_dir():
        for path in PROJECTS_DIR.rglob("*.jsonl"):
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield "claude", path
    if "codex" in agents:
        roots = [CODEX_HOME / "sessions", CODEX_HOME / "archived_sessions"]
        for root in roots:
            if not root.is_dir():
                continue
            for path in root.rglob("rollout-*.jsonl"):
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    yield "codex", path
    if "pi" in agents:
        root = PI_HOME / "agent" / "sessions"
        if root.is_dir():
            for path in root.rglob("*.jsonl"):
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    yield "pi", path
    if "omp" in agents:
        root = OMP_HOME / "agent" / "sessions"
        if root.is_dir():
            for path in root.rglob("*.jsonl"):
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    yield "omp", path


def meaningful_prompt(candidates):
    skip_prefixes = ("<local-command", "<command-message>", "<command-name>", "<system-reminder>")
    for text in candidates:
        stripped = (text or "").strip()
        if stripped and not stripped.startswith(skip_prefixes):
            return stripped
    return next((c.strip() for c in candidates if c and c.strip()), "")


def compute_meta(session):
    tool_counts = Counter()
    languages = Counter()
    git_commits = git_pushes = 0
    input_tokens = output_tokens = 0
    interruptions = 0
    response_times = []
    tool_errors = 0
    error_categories = Counter()
    uses_task = uses_mcp = uses_web_search = uses_web_fetch = False
    lines_added = lines_removed = 0
    files_modified = set()
    message_hours = []
    user_timestamps = []
    file_edit_calls = 0

    user_messages = assistant_messages = 0
    last_assistant_ts = None
    prompt_candidates = []

    for msg in session["messages"]:
        role = msg["role"]
        ts = msg.get("timestamp")
        usage = msg.get("usage") or {}
        input_tokens += usage.get("input") or 0
        output_tokens += usage.get("output") or 0

        if role == "assistant":
            assistant_messages += 1
            if ts:
                last_assistant_ts = ts
            for call in msg.get("tool_calls") or []:
                raw_name = call.get("name") or ""
                tool = normalize_tool_name(session["agent"], raw_name)
                args = call.get("input") if isinstance(call.get("input"), dict) else {}
                raw = call.get("raw") or ""
                tool_counts[tool] += 1
                if raw_name in TASK_TOOLS or tool in TASK_TOOLS or "agent" in raw_name.lower():
                    uses_task = True
                if (raw_name.startswith("mcp__")
                        or str(args.get("namespace", "")).startswith("mcp__")
                        or str(call.get("namespace", "")).startswith("mcp__")):
                    uses_mcp = True
                if raw_name in ("WebSearch", "web_search"):
                    uses_web_search = True
                if raw_name in ("WebFetch", "web_fetch"):
                    uses_web_fetch = True
                if tool in EDIT_TOOLS:
                    file_edit_calls += 1

                paths = tool_paths(session["agent"], tool, args, raw)
                for file_path in paths:
                    lang = LANGUAGE_BY_EXT.get(Path(file_path).suffix.lower())
                    if lang:
                        languages[lang] += 1
                    if tool in EDIT_TOOLS:
                        files_modified.add(file_path)

                if tool in EDIT_LIKE_TOOLS:
                    if session["agent"] in ("pi", "omp"):
                        for item in args.get("edits") or []:
                            if isinstance(item, dict):
                                added, removed = diff_lines(item.get("oldText") or "", item.get("newText") or "")
                                lines_added += added
                                lines_removed += removed
                    elif session["agent"] == "codex" and raw:
                        if "added_lines" in args:
                            lines_added += args.get("added_lines") or 0
                            lines_removed += args.get("removed_lines") or 0
                        else:
                            for line in raw.split("\n"):
                                if line.startswith("+") and not line.startswith("+++"):
                                    lines_added += 1
                                elif line.startswith("-") and not line.startswith("---"):
                                    lines_removed += 1
                    else:
                        added, removed = diff_lines(args.get("old_string") or "", args.get("new_string") or "")
                        lines_added += added
                        lines_removed += removed
                if tool in WRITE_TOOLS:
                    body = args.get("content")
                    if isinstance(body, str) and body:
                        lines_added += body.count("\n") + 1

                command = tool_command(session["agent"], tool, args, raw)
                if command:
                    if "git commit" in command:
                        git_commits += 1
                    if "git push" in command:
                        git_pushes += 1

        elif role == "user":
            text = msg.get("text") or ""
            if not text.strip():
                continue
            user_messages += 1
            prompt_candidates.append(text)
            if ts:
                local = ts.astimezone()
                message_hours.append(local.hour)
                user_timestamps.append(ts.isoformat())
                if last_assistant_ts:
                    gap = (ts - last_assistant_ts).total_seconds()
                    if 2 < gap < 3600:
                        response_times.append(gap)
            if "[Request interrupted by user" in text:
                interruptions += 1

        elif role == "tool":
            result = msg.get("tool_result") or {}
            if result.get("is_error"):
                tool_errors += 1
                error_categories[error_category(result.get("content"))] += 1

    first_ts = session["first_ts"]
    last_ts = session["last_ts"]
    duration = round((last_ts - first_ts).total_seconds() / 60) if first_ts and last_ts else 0
    first_prompt = meaningful_prompt(prompt_candidates[:10])

    return {
        "agent": session["agent"],
        "session_id": session["session_id"],
        "project_path": session["project_path"],
        "start_time": first_ts.isoformat() if first_ts else "",
        "transcript_mtime": session["mtime"],
        "duration_minutes": duration,
        "user_message_count": user_messages,
        "assistant_message_count": assistant_messages,
        "tool_counts": dict(tool_counts),
        "languages": dict(languages),
        "git_commits": git_commits,
        "git_pushes": git_pushes,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "first_prompt": first_prompt[:2000],
        "summary": "",
        "user_interruptions": interruptions,
        "user_response_times": response_times,
        "tool_errors": tool_errors,
        "tool_error_categories": dict(error_categories),
        "uses_task_agent": uses_task,
        "uses_mcp": uses_mcp,
        "uses_web_search": uses_web_search,
        "uses_web_fetch": uses_web_fetch,
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "files_modified": len(files_modified),
        "message_hours": message_hours,
        "user_message_timestamps": user_timestamps,
        "permission_mode": session["permission_mode"] or "",
        "bash_would_prompt_count": 0,
        "file_edit_tool_count": file_edit_calls,
        "destructive_command_count": 0,
    }


def cache_name(agent, session_id):
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)
    return f"{agent}-{safe}.json"


def load_cached_meta(path, mtime):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if data.get("transcript_mtime") != mtime:
        return None
    return data


def save_meta(path, meta):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_facet(facets_dir, session_id):
    path = facets_dir / f"{session_id}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def is_warmup_only(facet):
    if not facet:
        return False
    goals = facet.get("goal_categories") or {}
    active = [k for k, v in goals.items() if (v or 0) > 0]
    return len(active) == 1 and active[0] == "warmup_minimal"


def multi_clauding(sessions):
    points = []
    for meta in sessions:
        for ts in meta.get("user_message_timestamps") or []:
            parsed = parse_ts(ts)
            if parsed:
                points.append((parsed.timestamp(), meta["session_id"]))
    points.sort()
    pairs = set()
    involved = set()
    messages_during = set()
    left = 0
    last_index = {}
    for right, (ts, session_id) in enumerate(points):
        while left < right and ts - points[left][0] > 1800:
            old_ts, old_sid = points[left]
            if last_index.get(old_sid) == left:
                del last_index[old_sid]
            left += 1
        previous = last_index.get(session_id)
        if previous is not None:
            for middle in range(previous + 1, right):
                mid_ts, mid_sid = points[middle]
                if mid_sid != session_id:
                    pairs.add(tuple(sorted((session_id, mid_sid))))
                    involved.update((session_id, mid_sid))
                    messages_during.update({
                        (points[previous][0], session_id),
                        (mid_ts, mid_sid),
                        (ts, session_id),
                    })
                    break
        last_index[session_id] = right
    return {
        "overlap_events": len(pairs),
        "sessions_involved": len(involved),
        "user_messages_during": len(messages_during),
    }


def aggregate(sessions, facets, scanned):
    stats = {
        "total_sessions": len(sessions),
        "total_sessions_scanned": scanned,
        "sessions_with_facets": sum(1 for s in sessions if s["session_id"] in facets),
        "agent_counts": dict(Counter(s["agent"] for s in sessions)),
        "date_range": {"start": "", "end": ""},
        "total_messages": 0,
        "total_duration_hours": 0.0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "tool_counts": {},
        "languages": {},
        "git_commits": 0,
        "git_pushes": 0,
        "projects": {},
        "goal_categories": {},
        "outcomes": {},
        "satisfaction": {},
        "helpfulness": {},
        "session_types": {},
        "friction": {},
        "success": {},
        "session_summaries": [],
        "total_interruptions": 0,
        "total_tool_errors": 0,
        "tool_error_categories": {},
        "user_response_times": [],
        "median_response_time": 0,
        "avg_response_time": 0,
        "sessions_using_task_agent": 0,
        "sessions_using_mcp": 0,
        "sessions_using_web_search": 0,
        "sessions_using_web_fetch": 0,
        "total_lines_added": 0,
        "total_lines_removed": 0,
        "total_files_modified": 0,
        "days_active": 0,
        "messages_per_day": 0,
        "message_hours": [],
        "multi_clauding": {"overlap_events": 0, "sessions_involved": 0, "user_messages_during": 0},
    }

    starts = []
    hours = []
    response_times = []
    for meta in sessions:
        stats["total_messages"] += meta["user_message_count"]
        stats["total_duration_hours"] += meta["duration_minutes"] / 60
        stats["total_input_tokens"] += meta["input_tokens"]
        stats["total_output_tokens"] += meta["output_tokens"]
        stats["git_commits"] += meta["git_commits"]
        stats["git_pushes"] += meta["git_pushes"]
        stats["total_interruptions"] += meta["user_interruptions"]
        stats["total_tool_errors"] += meta["tool_errors"]
        stats["total_lines_added"] += meta["lines_added"]
        stats["total_lines_removed"] += meta["lines_removed"]
        stats["total_files_modified"] += meta["files_modified"]
        response_times.extend(meta["user_response_times"])
        hours.extend(meta["message_hours"])
        starts.append(meta["start_time"])

        for key, value in (meta["tool_error_categories"] or {}).items():
            stats["tool_error_categories"][key] = stats["tool_error_categories"].get(key, 0) + value
        for key, value in (meta["tool_counts"] or {}).items():
            stats["tool_counts"][key] = stats["tool_counts"].get(key, 0) + value
        for key, value in (meta["languages"] or {}).items():
            stats["languages"][key] = stats["languages"].get(key, 0) + value
        if meta["project_path"]:
            stats["projects"][meta["project_path"]] = stats["projects"].get(meta["project_path"], 0) + 1
        if meta["uses_task_agent"]:
            stats["sessions_using_task_agent"] += 1
        if meta["uses_mcp"]:
            stats["sessions_using_mcp"] += 1
        if meta["uses_web_search"]:
            stats["sessions_using_web_search"] += 1
        if meta["uses_web_fetch"]:
            stats["sessions_using_web_fetch"] += 1

        facet = facets.get(meta["session_id"])
        if facet:
            for key, value in (facet.get("goal_categories") or {}).items():
                if value and value > 0:
                    stats["goal_categories"][key] = stats["goal_categories"].get(key, 0) + value
            outcome = facet.get("outcome")
            if outcome:
                stats["outcomes"][outcome] = stats["outcomes"].get(outcome, 0) + 1
            for key, value in (facet.get("user_satisfaction_counts") or {}).items():
                if value and value > 0:
                    stats["satisfaction"][key] = stats["satisfaction"].get(key, 0) + value
            helpfulness = facet.get("claude_helpfulness")
            if helpfulness:
                stats["helpfulness"][helpfulness] = stats["helpfulness"].get(helpfulness, 0) + 1
            session_type = facet.get("session_type")
            if session_type:
                stats["session_types"][session_type] = stats["session_types"].get(session_type, 0) + 1
            for key, value in (facet.get("friction_counts") or {}).items():
                if value and value > 0:
                    stats["friction"][key] = stats["friction"].get(key, 0) + value
            success = facet.get("primary_success")
            if success and success != "none":
                stats["success"][success] = stats["success"].get(success, 0) + 1

        if len(stats["session_summaries"]) < 50:
            stats["session_summaries"].append({
                "agent": meta["agent"],
                "id": meta["session_id"][:8],
                "date": meta["start_time"][:10],
                "project": meta["project_path"],
                "duration_minutes": meta["duration_minutes"],
                "user_messages": meta["user_message_count"],
                "summary": (meta.get("summary") or meta["first_prompt"][:100]).strip(),
                "goal": (facet or {}).get("underlying_goal", ""),
            })

    starts = sorted(s for s in starts if s)
    if starts:
        stats["date_range"]["start"] = starts[0][:10]
        stats["date_range"]["end"] = starts[-1][:10]
    stats["user_response_times"] = response_times
    if response_times:
        ordered = sorted(response_times)
        stats["median_response_time"] = ordered[len(ordered) // 2]
        stats["avg_response_time"] = sum(response_times) / len(response_times)
    stats["message_hours"] = hours
    stats["days_active"] = len({s[:10] for s in starts})
    if stats["days_active"]:
        stats["messages_per_day"] = round(stats["total_messages"] / stats["days_active"], 1)
    stats["multi_clauding"] = multi_clauding(sessions)
    return stats


def build_digest(stats):
    lines = []
    lines.append("# Insights digest")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Date range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    agents = ", ".join(f"{k}={v}" for k, v in sorted(stats["agent_counts"].items())) or "none"
    lines.append(
        f"Sessions: {stats['total_sessions']} analyzed / {stats['total_sessions_scanned']} scanned"
        f" | Messages: {stats['total_messages']} | Hours: {stats['total_duration_hours']:.1f}"
        f" | Commits: {stats['git_commits']} | Facets: {stats['sessions_with_facets']}"
    )
    lines.append(f"Agents: {agents}")
    lines.append("")

    def top(mapping, n=8):
        return ", ".join(f"{k}={v}" for k, v in sorted(mapping.items(), key=lambda x: -x[1])[:n]) or "none"

    lines.append("## Headline")
    lines.append(f"- Tools: {top(stats['tool_counts'])}")
    lines.append(f"- Languages: {top(stats['languages'])}")
    lines.append(f"- Goals: {top(stats['goal_categories'])}")
    lines.append(f"- Outcomes: {top(stats['outcomes'])}")
    lines.append(f"- Satisfaction: {top(stats['satisfaction'])}")
    lines.append(f"- Friction: {top(stats['friction'])}")
    lines.append(f"- Success: {top(stats['success'])}")
    lines.append(f"- Lines: +{stats['total_lines_added']}/-{stats['total_lines_removed']}"
                 f" | Files: {stats['total_files_modified']} | Days: {stats['days_active']}")
    lines.append(f"- Interruptions: {stats['total_interruptions']} | Tool errors: {stats['total_tool_errors']}"
                 f" | Median response: {stats['median_response_time']:.0f}s")
    lines.append("")

    lines.append("## Session summaries")
    for item in stats["session_summaries"]:
        summary = (item["summary"] or "").replace("\n", " ").strip()
        goal = (item["goal"] or "").replace("\n", " ").strip()
        lines.append(
            f"- [{item['agent']}] {item['date']} | {item['project']} | {item['duration_minutes']}m"
            f" | {item['user_messages']} msgs | {summary[:220]}"
            + (f" | goal: {goal[:160]}" if goal else "")
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def build_facet_digest(facets):
    lines = []
    friction_details = []
    for facet in facets.values():
        detail = (facet.get("friction_detail") or "").strip()
        if detail:
            friction_details.append(f"- {detail}")
    if friction_details:
        lines.append("## Friction details")
        lines.extend(friction_details[:20])
        lines.append("")

    instructions = []
    for facet in facets.values():
        instructions.extend(facet.get("user_instructions_to_claude") or [])
    if instructions:
        lines.append("## User instructions to Claude")
        lines.extend(f"- {item}" for item in instructions[:15])
        lines.append("")
    return "\n".join(lines) + "\n"


def transcript_digest(session, limit=30000):
    lines = [
        f"Session: {session['session_id'][:8]}",
        f"Agent: {AGENT_LABELS.get(session['agent'], session['agent'])}",
        f"Date: {session['first_ts'].isoformat() if session['first_ts'] else ''}",
        f"Project: {session['project_path']}",
        "",
    ]
    for msg in session["messages"]:
        role = msg["role"]
        if role == "user" and msg.get("text"):
            lines.append(f"USER: {msg['text'][:500]}")
        elif role == "assistant":
            if msg.get("text"):
                lines.append(f"ASSISTANT: {msg['text'][:300]}")
            for call in msg.get("tool_calls") or []:
                lines.append(f"TOOL: {call.get('name', '')}")
        if sum(len(line) for line in lines) > limit:
            lines.append("[transcript truncated]")
            break
    return "\n".join(lines)


def emit_facets(sessions, facets, out_dir, limit, paths):
    todo = []
    for meta in sessions:
        if meta["session_id"] in facets or len(todo) >= limit:
            continue
        path = paths.get((meta["agent"], meta["session_id"]))
        transcript = meta.get("transcript") or ""
        if not transcript and path:
            try:
                transcript = transcript_digest(READERS[meta["agent"]](path))
            except OSError:
                transcript = ""
        todo.append({
            "agent": meta["agent"],
            "session_id": meta["session_id"],
            "project_path": meta["project_path"],
            "start_time": meta["start_time"],
            "duration_minutes": meta["duration_minutes"],
            "user_message_count": meta["user_message_count"],
            "transcript": transcript or meta["first_prompt"][:2000],
        })
    path = out_dir / "facets-todo.json"
    path.write_text(json.dumps(todo, ensure_ascii=False, indent=2), encoding="utf-8")
    return path, len(todo)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", default="all",
                        help="claude, codex, omp, pi, or all. Comma-separated. Default: all.")
    parser.add_argument("--days", type=int, default=30, help="Only sessions updated within N days. 0 = all.")
    parser.add_argument("--max-sessions", type=int, default=500, help="Maximum sessions to analyze.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output directory.")
    parser.add_argument("--facets-dir", type=Path, default=BUILTIN_FACETS_DIR,
                        help="Directory of per-session facet JSON files.")
    parser.add_argument("--emit-facets", action="store_true",
                        help="Write facets-todo.json for sessions without a facet.")
    parser.add_argument("--max-facets", type=int, default=50,
                        help="Maximum sessions listed in facets-todo.json.")
    args = parser.parse_args()

    requested = [item.strip() for item in args.agent.split(",") if item.strip()]
    if "all" in requested:
        requested = list(AGENT_LABELS)
    unknown = [item for item in requested if item not in AGENT_LABELS]
    if unknown:
        parser.error(f"unknown agent: {', '.join(unknown)}; choose from {', '.join(AGENT_LABELS)} or all")

    out_dir = args.out
    meta_dir = out_dir / "session-meta"
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    cutoff = None
    if args.days > 0:
        cutoff = datetime.now(timezone.utc).timestamp() - args.days * 86400

    sessions = []
    session_paths = {}
    rpc_count = 0
    file_agents = requested
    if "codex" in requested:
        try:
            rpc_metas = fetch_codex_rpc(args.days, meta_dir, args.max_sessions)
            sessions.extend(rpc_metas)
            rpc_count = len(rpc_metas)
            file_agents = [a for a in requested if a != "codex"]
            print(f"codex: {rpc_count} threads via app-server", file=sys.stderr)
        except Exception as exc:
            print(f"codex app-server unavailable, using rollout files: {exc}", file=sys.stderr)

    candidates = []
    for agent, path in iter_sessions(file_agents):
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if cutoff and mtime < cutoff:
            continue
        candidates.append((mtime, agent, path))
    candidates.sort(key=lambda item: item[0], reverse=True)

    for mtime, agent, path in candidates:
        if len(sessions) - rpc_count >= args.max_sessions:
            break
        cached = load_cached_meta(meta_dir / cache_name(agent, path.stem), mtime)
        if cached:
            sessions.append(cached)
            session_paths[(cached["agent"], cached["session_id"])] = path
            continue
        try:
            parsed = READERS[agent](path)
        except OSError as exc:
            print(f"skip {path}: {exc}", file=sys.stderr)
            continue
        meta = compute_meta(parsed)
        save_meta(meta_dir / cache_name(agent, path.stem), meta)
        sessions.append(meta)
        session_paths[(meta["agent"], meta["session_id"])] = path

    sessions.sort(key=lambda meta: meta.get("transcript_mtime") or 0, reverse=True)
    sessions = sessions[:args.max_sessions]

    selected = [s for s in sessions
                if s["user_message_count"] >= 2 and s["duration_minutes"] >= 1]
    selected.sort(key=lambda s: s["start_time"], reverse=True)

    facets = {}
    if args.facets_dir.is_dir():
        for meta in selected:
            facet = load_facet(args.facets_dir, meta["session_id"])
            if facet and not is_warmup_only(facet):
                facets[meta["session_id"]] = facet

    stats = aggregate(selected, facets, len(candidates) + rpc_count)
    (out_dir / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    digest = build_digest(stats) + build_facet_digest(facets)
    (out_dir / "digest.md").write_text(digest, encoding="utf-8")

    print(f"stats:  {out_dir / 'stats.json'}")
    print(f"digest: {out_dir / 'digest.md'}")
    agents = ", ".join(f"{k}={v}" for k, v in sorted(stats["agent_counts"].items())) or "none"
    print(
        f"sessions: {stats['total_sessions']} analyzed / {stats['total_sessions_scanned']} scanned"
        f" | messages: {stats['total_messages']} | facets: {stats['sessions_with_facets']}"
    )
    print(f"agents: {agents}")

    if args.emit_facets:
        path, count = emit_facets(selected, facets, out_dir, args.max_facets, session_paths)
        print(f"facets todo: {path} ({count} sessions)")


if __name__ == "__main__":
    main()
