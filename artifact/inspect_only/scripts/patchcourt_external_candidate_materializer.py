#!/usr/bin/env python3
"""Gold-blind candidate materializer for a truly independent model source.

This worker is intentionally separate from the Codex-session bootstrap
materializer. It may call an OpenAI-compatible API, the Hugging Face router, or
a local transformers model. If no such source is configured, it records a
blocked status and emits no fake diffs.
"""

from __future__ import print_function

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tempfile

try:
    from urllib import request as urllib_request
    from urllib import error as urllib_error
except ImportError:  # pragma: no cover - Python 2 is not supported, but keep py36 style.
    urllib_request = None
    urllib_error = None


GOLD_FIELDS = set(["patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"])
MAX_FILE_CHARS = 12000
MAX_ISSUE_CHARS = 6000
STRUCTURED_FORMAT = "structured_search_replace"
UNIFIED_DIFF_FORMAT = "unified_diff"


def utc_now():
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def safe_id(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", value or "unknown")[:180]


def assert_no_gold(value, path):
    if isinstance(value, dict):
        leaked = sorted(GOLD_FIELDS.intersection(value.keys()))
        if leaked:
            raise RuntimeError("%s contains gold fields: %s" % (path, leaked))
        for key, child in value.items():
            assert_no_gold(child, "%s.%s" % (path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_gold(child, "%s[%s]" % (path, index))


def read_json(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    assert_no_gold(value, path)
    return value


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            record = json.loads(stripped)
            assert_no_gold(record, "%s:%s" % (path, line_no))
            if record.get("gold_used") is not False:
                raise RuntimeError("%s:%s must carry gold_used=false" % (path, line_no))
            rows.append(record)
    return rows


def write_text(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(value or "")


def write_json(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def append_jsonl(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    except IOError:
        return ""


def read_repo_text_and_newline(path):
    with open(path, "rb") as handle:
        raw = handle.read()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("utf-8", "replace").replace("\r\n", "\n")
    return text, newline


def write_repo_text_with_newline(path, value, newline):
    text = value.replace("\r\n", "\n")
    if newline == "\r\n":
        text = text.replace("\n", "\r\n")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def run_command(cmd, cwd, timeout):
    return subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=timeout,
    )


def copy_repo(src, dst):
    ignore = shutil.ignore_patterns("__pycache__", ".pytest_cache", ".mypy_cache", ".tox")
    shutil.copytree(src, dst, symlinks=True, ignore=ignore)


def initialize_diff_repo(repo, timeout):
    git_dir = os.path.join(repo, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir, ignore_errors=True)
    run_command(["git", "init"], repo, timeout)
    run_command(["git", "add", "-A"], repo, timeout)
    run_command(
        [
            "git",
            "-c",
            "user.name=PatchCourt",
            "-c",
            "user.email=patchcourt@example.invalid",
            "commit",
            "--allow-empty",
            "-m",
            "patchcourt-structured-base",
        ],
        repo,
        timeout,
    )


def parse_targets(value):
    if not value:
        return set()
    return set(item.strip() for item in value.split(",") if item.strip())


def issue_for_candidate(candidate):
    context_path = candidate.get("context_path") or ""
    if not context_path:
        return ""
    return read_text(os.path.join(os.path.dirname(context_path), "issue.md"))


def context_file_paths(context):
    paths = []
    for item in context.get("context_files", []) or []:
        path = item.get("path") if isinstance(item, dict) else ""
        if path and path not in paths:
            paths.append(path)
    return paths


def prompt_for(
    candidate,
    context,
    issue_text,
    snapshot_run_dir,
    max_context_files,
    generation_format=UNIFIED_DIFF_FORMAT,
    repair_feedback="",
    max_file_chars=MAX_FILE_CHARS,
    max_issue_chars=MAX_ISSUE_CHARS,
    sample_index=0,
    sample_count=1,
):
    task_id = candidate.get("task_id")
    repo_root = os.path.join(snapshot_run_dir, "worktrees", safe_id(task_id), "repo")
    chunks = []
    for relpath in context_file_paths(context)[:max_context_files]:
        full_path = os.path.join(repo_root, relpath)
        text = read_text(full_path)
        if not text:
            continue
        chunks.append(
            "### File: {path}\n```text\n{content}\n```".format(
                path=relpath,
                content=text[:max_file_chars],
            )
        )
    common = (
        "You are an independent repair model generating a minimal patch for a public GitHub issue.\n"
        "Use only the public issue text and repository files shown below. Do not use developer patches, "
        "hidden tests, FAIL_TO_PASS, PASS_TO_PASS, or test_patch fields.\n\n"
        "Task: {task}\n"
        "Repo: {repo}\n"
        "Candidate source prompt lane: {source}\n\n"
        "Public issue text:\n{issue}\n\n"
        "Repository context:\n{context}\n\n"
    ).format(
        task=task_id,
        repo=candidate.get("repo"),
        source=candidate.get("candidate_source"),
        issue=(issue_text or "").strip()[:max_issue_chars],
        context="\n\n".join(chunks) if chunks else "(no context files available)",
    )
    diversity = ""
    if sample_count > 1:
        diversity = (
            "Independent sample {sample_index} of {sample_count}: produce a valid minimal fix, "
            "but choose the smallest plausible repair independently from other samples when multiple "
            "repair strategies or edit locations are possible. Do not add unrelated changes.\n\n"
        ).format(sample_index=sample_index + 1, sample_count=sample_count)
    if generation_format == STRUCTURED_FORMAT:
        feedback = ""
        if repair_feedback:
            feedback = (
                "\nYour previous structured edit did not apply in the repository copy.\n"
                "Repair feedback:\n{feedback}\n\n"
            ).format(feedback=repair_feedback[:5000])
        return (
            common
            + diversity
            + feedback
            + "Return only PatchCourt SEARCH/REPLACE edit blocks in this exact format:\n"
            + "File: relative/path.py\n"
            + "<<<<<<< SEARCH\n"
            + "exact text copied from that file\n"
            + "=======\n"
            + "replacement text\n"
            + ">>>>>>> REPLACE\n\n"
            + "Rules:\n"
            + "- Do not return a unified diff.\n"
            + "- The SEARCH text must be copied exactly from one shown file.\n"
            + "- Use the smallest edit that addresses the public issue.\n"
            + "- Use only files shown in the repository context.\n"
            + "- If multiple edits are needed, repeat the same block format.\n"
            + "- Do not include prose outside the edit blocks.\n"
        )
    return common + diversity + "Return one unified diff only. Do not include prose outside the diff.\n"


def extract_diff(response_text):
    text = response_text or ""
    fence = re.search(r"```(?:diff|patch)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1)
    diff_start = text.find("diff --git ")
    if diff_start >= 0:
        return text[diff_start:].strip() + "\n"
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("--- ") and index + 1 < len(lines) and lines[index + 1].startswith("+++ "):
            return "\n".join(lines[index:]).strip() + "\n"
    for index, line in enumerate(lines):
        if line.startswith("@@ "):
            head = max(0, index - 2)
            return "\n".join(lines[head:]).strip() + "\n"
    return ""


def strip_fence(text):
    value = text or ""
    fence = re.search(r"```(?:patchcourt-edit|text|json|diff|patch)?\s*(.*?)```", value, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1)
    return value


def parse_structured_edits(response_text):
    text = strip_fence(response_text)
    edits = []
    pattern = re.compile(
        r"(?:^|\n)File:\s*(?P<path>[^\n]+)\n<<<<<<< SEARCH\n(?P<old>.*?)\n=======\n(?P<new>.*?)\n>>>>>>> REPLACE",
        re.DOTALL,
    )
    for match in pattern.finditer(text):
        edits.append(
            {
                "path": match.group("path").strip().strip("`'\""),
                "old": match.group("old"),
                "new": match.group("new"),
                "format": "search_replace_block",
            }
        )
    if edits:
        return edits
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if not json_match:
        return []
    try:
        value = json.loads(json_match.group(0))
    except Exception:
        return []
    raw_edits = value.get("edits") if isinstance(value, dict) else []
    if not isinstance(raw_edits, list):
        return []
    for item in raw_edits:
        if not isinstance(item, dict):
            continue
        path = item.get("path") or item.get("file")
        old = item.get("old") or item.get("search")
        new = item.get("new") or item.get("replace")
        if path and old is not None and new is not None:
            edits.append({"path": str(path), "old": str(old), "new": str(new), "format": "json_edit"})
    return edits


def normalize_edit_path(path):
    relpath = (path or "").strip().strip("`'\"")
    while relpath.startswith("./"):
        relpath = relpath[2:]
    if relpath.startswith("a/") or relpath.startswith("b/"):
        relpath = relpath[2:]
    relpath = relpath.replace("\\", "/")
    return relpath


def safe_join_repo(repo, relpath):
    normalized = normalize_edit_path(relpath)
    if not normalized or normalized.startswith("/") or normalized.startswith("../") or "/../" in normalized:
        raise ValueError("unsafe_or_empty_path:%s" % relpath)
    full = os.path.abspath(os.path.join(repo, normalized))
    root = os.path.abspath(repo)
    if full != root and not full.startswith(root + os.sep):
        raise ValueError("path_escapes_repo:%s" % relpath)
    return normalized, full


def replace_once(content, old, new):
    candidates = [old]
    if old.startswith("\n"):
        candidates.append(old[1:])
    if old.endswith("\n"):
        candidates.append(old[:-1])
    stripped = old.strip("\n")
    if stripped and stripped not in candidates:
        candidates.append(stripped)
    for needle in candidates:
        if not needle:
            continue
        index = content.find(needle)
        if index >= 0:
            return content[:index] + new + content[index + len(needle):], needle
    fuzzy_content, fuzzy_matched = replace_by_stripped_line_sequence(content, old, new)
    if fuzzy_content is not None:
        return fuzzy_content, fuzzy_matched
    return None, None


def leading_whitespace(value):
    match = re.match(r"\s*", value)
    return match.group(0) if match else ""


def minimum_indent(lines):
    indents = []
    for line in lines:
        if line.strip():
            indents.append(len(leading_whitespace(line)))
    return min(indents) if indents else 0


def adapt_replacement_indent(new, target_indent):
    raw_lines = new.strip("\n").splitlines()
    if not raw_lines:
        return ""
    base_indent = minimum_indent(raw_lines)
    adapted = []
    for line in raw_lines:
        if not line.strip():
            adapted.append("")
        else:
            adapted.append(target_indent + line[base_indent:])
    return "\n".join(adapted)


def replace_by_stripped_line_sequence(content, old, new):
    old_lines = old.strip("\n").splitlines()
    if not old_lines:
        return None, None
    old_cmp = [line.strip() for line in old_lines]
    content_lines = content.splitlines(True)
    matches = []
    count = len(old_cmp)
    for start in range(0, len(content_lines) - count + 1):
        window = [content_lines[start + offset].strip() for offset in range(count)]
        if window == old_cmp:
            matches.append(start)
            if len(matches) > 1:
                return None, None
    if not matches:
        return None, None
    start = matches[0]
    end = start + count
    target_indent = leading_whitespace(content_lines[start])
    replacement = adapt_replacement_indent(new, target_indent)
    if end < len(content_lines) and content_lines[end - 1].endswith("\n"):
        replacement += "\n"
    matched = "".join(content_lines[start:end])
    return "".join(content_lines[:start]) + replacement + "".join(content_lines[end:]), matched


def apply_structured_response(candidate, args, response_text, candidate_dir):
    task_id = candidate.get("task_id")
    repo_root = os.path.join(args.snapshot_run_dir, "worktrees", safe_id(task_id), "repo")
    edits = parse_structured_edits(response_text)
    if not edits:
        return {"ok": False, "reason": "no_structured_search_replace_blocks"}
    tmp_root = tempfile.mkdtemp(prefix="patchcourt_structured_edit_")
    try:
        repo_copy = os.path.join(tmp_root, "repo")
        copy_repo(repo_root, repo_copy)
        initialize_diff_repo(repo_copy, args.structured_timeout_sec)
        applied = []
        for edit_index, edit in enumerate(edits):
            try:
                relpath, full_path = safe_join_repo(repo_copy, edit.get("path"))
            except ValueError as exc:
                return {"ok": False, "reason": "edit_%s_%s" % (edit_index, exc)}
            if not os.path.exists(full_path):
                return {"ok": False, "reason": "edit_%s_file_missing:%s" % (edit_index, relpath)}
            content, newline = read_repo_text_and_newline(full_path)
            old = edit.get("old") or ""
            new = edit.get("new") or ""
            next_content, matched = replace_once(content, old, new)
            if next_content is None:
                return {
                    "ok": False,
                    "reason": "edit_%s_search_text_not_found:%s" % (edit_index, relpath),
                    "search_preview": old[:1000],
                }
            write_repo_text_with_newline(full_path, next_content, newline)
            applied.append({"path": relpath, "search_sha256": hashlib.sha256(matched.encode("utf-8", "replace")).hexdigest()})
        diff = run_command(["git", "diff", "--no-ext-diff", "--binary"], repo_copy, args.structured_timeout_sec)
        if diff.returncode != 0:
            return {"ok": False, "reason": "git_diff_failed:%s" % diff.stderr[-1000:]}
        if not diff.stdout.strip():
            return {"ok": False, "reason": "structured_edit_generated_empty_diff"}
        diff_path = os.path.join(candidate_dir, "candidate.diff")
        write_text(diff_path, diff.stdout)
        check_strategy = "git_apply_strict"
        check = run_command(["git", "apply", "--check", diff_path], repo_root, args.structured_timeout_sec)
        if check.returncode != 0:
            whitespace_check = run_command(
                ["git", "apply", "--check", "--ignore-space-change", diff_path],
                repo_root,
                args.structured_timeout_sec,
            )
            if whitespace_check.returncode == 0:
                check_strategy = "git_apply_ignore_space_change"
                check = whitespace_check
        if check.returncode != 0:
            return {
                "ok": False,
                "reason": "programmatic_diff_failed_git_apply_check:%s" % check.stderr[-1500:],
                "diff_path": diff_path,
            }
        return {
            "ok": True,
            "diff_path": diff_path,
            "diff_sha256": hashlib.sha256(diff.stdout.encode("utf-8", "replace")).hexdigest(),
            "edit_count": len(applied),
            "applied_edits": applied,
            "apply_check_strategy": check_strategy,
        }
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def backend_status(args):
    backend = args.generation_backend
    if backend in {"openai_chat", "openai_compatible_chat"}:
        base_url = os.environ.get("OPENAI_BASE_URL", "")
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if backend == "openai_compatible_chat" and base_url:
            return {"ready": True, "reason": "ready"}
        return {
            "ready": bool(api_key),
            "reason": "OPENAI_API_KEY_missing" if not api_key else "ready",
        }
    if backend == "hf_router_chat":
        token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
        return {
            "ready": bool(token),
            "reason": "HF_TOKEN_missing" if not token else "ready",
        }
    if backend == "local_transformers":
        if not args.local_model:
            return {"ready": False, "reason": "local_model_path_or_name_missing"}
        try:
            import torch  # noqa: F401
            import transformers  # noqa: F401
        except Exception as exc:
            return {"ready": False, "reason": "local_transformers_import_failed:%r" % (exc,)}
        return {"ready": True, "reason": "ready"}
    return {"ready": False, "reason": "unsupported_generation_backend:%s" % backend}


def post_json(url, payload, headers, timeout):
    data = json.dumps(payload).encode("utf-8")
    request = urllib_request.Request(url, data=data, headers=headers)
    try:
        with urllib_request.urlopen(request, timeout=timeout) as handle:
            return handle.read().decode("utf-8", "replace")
    except urllib_error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        raise RuntimeError("HTTP %s from %s: %s" % (exc.code, url, body[:1000]))


def system_prompt_for(args):
    if args.generation_format == STRUCTURED_FORMAT:
        return "Return only PatchCourt SEARCH/REPLACE edit blocks. Do not return a unified diff."
    return "Return only a unified diff."


def call_openai_chat(args, prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    if not api_key and args.generation_backend == "openai_compatible_chat" and base_url:
        api_key = "patchcourt-local-endpoint"
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY_missing")
    payload = {
        "model": args.generation_model,
        "messages": [
            {"role": "system", "content": system_prompt_for(args)},
            {"role": "user", "content": prompt},
        ],
        "temperature": args.temperature,
        "max_tokens": args.max_new_tokens,
    }
    text = post_json(
        base_url + "/chat/completions",
        payload,
        {"Content-Type": "application/json", "Authorization": "Bearer " + api_key},
        args.request_timeout_sec,
    )
    value = json.loads(text)
    return value["choices"][0]["message"]["content"]


def call_hf_router_chat(args, prompt):
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN_missing")
    payload = {
        "model": args.generation_model,
        "messages": [
            {"role": "system", "content": system_prompt_for(args)},
            {"role": "user", "content": prompt},
        ],
        "temperature": args.temperature,
        "max_tokens": args.max_new_tokens,
    }
    text = post_json(
        os.environ.get("HF_ROUTER_URL", "https://router.huggingface.co/v1/chat/completions"),
        payload,
        {"Content-Type": "application/json", "Authorization": "Bearer " + token},
        args.request_timeout_sec,
    )
    value = json.loads(text)
    return value["choices"][0]["message"]["content"]


_LOCAL_MODEL = {"tokenizer": None, "model": None}


def call_local_transformers(args, prompt):
    if _LOCAL_MODEL["tokenizer"] is None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(args.local_model, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            args.local_model,
            torch_dtype="auto",
            device_map="auto",
            trust_remote_code=True,
        )
        _LOCAL_MODEL["tokenizer"] = tokenizer
        _LOCAL_MODEL["model"] = model
    tokenizer = _LOCAL_MODEL["tokenizer"]
    model = _LOCAL_MODEL["model"]
    messages = [
        {"role": "system", "content": system_prompt_for(args)},
        {"role": "user", "content": prompt},
    ]
    if hasattr(tokenizer, "apply_chat_template"):
        encoded = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True)
    else:
        encoded = tokenizer(prompt, return_tensors="pt").input_ids
    encoded = encoded.to(model.device)
    output = model.generate(encoded, max_new_tokens=args.max_new_tokens, do_sample=args.temperature > 0, temperature=max(args.temperature, 1e-5))
    generated = output[0][encoded.shape[-1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)


def call_model(args, prompt):
    if args.generation_backend in {"openai_chat", "openai_compatible_chat"}:
        return call_openai_chat(args, prompt)
    if args.generation_backend == "hf_router_chat":
        return call_hf_router_chat(args, prompt)
    if args.generation_backend == "local_transformers":
        return call_local_transformers(args, prompt)
    raise RuntimeError("unsupported_generation_backend:%s" % args.generation_backend)


def carry_forward(candidate, args):
    record = dict(candidate)
    record.update(
        {
            "materialization_queue_id": args.queue_id,
            "materialization_strategy": "carried_forward_control",
            "model_generated": False,
            "heuristic_candidate": False,
            "expected_behavior_change": False,
            "gold_used": False,
        }
    )
    return record


def blocked_record(candidate, args, reason):
    record = dict(candidate)
    record.update(
        {
            "status": "blocked_no_independent_model_source",
            "materialization_queue_id": args.queue_id,
            "materialization_strategy": "independent_model_generation_blocked",
            "generation_backend": args.generation_backend,
            "generation_model": args.generation_model,
            "blocked_reason": reason,
            "model_generated": False,
            "heuristic_candidate": False,
            "expected_behavior_change": True,
            "gold_used": False,
            "created_at": utc_now(),
        }
    )
    return record


def sample_label(sample_index, sample_count):
    if sample_count <= 1:
        return ""
    return "sample_%02d" % sample_index


def sample_suffix(base_suffix, sample_index, sample_count):
    if sample_count <= 1:
        return base_suffix
    return "%s_s%02d" % (base_suffix, sample_index)


def materialize_candidate(candidate, args, queue_dir, sample_index=0, sample_count=1):
    context = read_json(candidate.get("context_path"))
    issue_text = issue_for_candidate(candidate)
    task_id = candidate.get("task_id")
    source = candidate.get("candidate_source") or "unknown"
    source_dir_name = source
    label = sample_label(sample_index, sample_count)
    if label:
        source_dir_name = "%s__%s" % (source, label)
    candidate_dir = os.path.join(queue_dir, "tasks", safe_id(task_id), "candidates", safe_id(source_dir_name))
    os.makedirs(candidate_dir, exist_ok=True)
    candidate_suffix = sample_suffix(args.candidate_id_suffix, sample_index, sample_count)
    attempts = []
    total_started = time.time()
    repair_feedback = ""
    if args.generation_format == STRUCTURED_FORMAT:
        for attempt in range(max(1, args.repair_attempts + 1)):
            prompt = prompt_for(
                candidate,
                context,
                issue_text,
                args.snapshot_run_dir,
                args.max_context_files,
                args.generation_format,
                repair_feedback,
                args.max_file_chars,
                args.max_issue_chars,
                sample_index,
                sample_count,
            )
            prompt_path = os.path.join(candidate_dir, "prompt_%02d.md" % attempt)
            response_path = os.path.join(candidate_dir, "response_%02d.md" % attempt)
            write_text(prompt_path, prompt)
            started = time.time()
            response_text = call_model(args, prompt)
            duration = round(time.time() - started, 3)
            write_text(response_path, response_text)
            structured = apply_structured_response(candidate, args, response_text, candidate_dir)
            attempt_record = {
                "attempt": attempt,
                "duration_sec": duration,
                "prompt_path": prompt_path,
                "response_path": response_path,
                "ok": structured.get("ok"),
                "reason": structured.get("reason", ""),
            }
            attempts.append(attempt_record)
            if structured.get("ok"):
                record = dict(candidate)
                record.update(
                    {
                        "original_candidate_id": candidate.get("candidate_id"),
                        "candidate_id": "%s::%s::%s" % (task_id, source, candidate_suffix),
                        "status": "materialized_model",
                        "diff_path": structured["diff_path"],
                        "diff_sha256": structured["diff_sha256"],
                        "model_prompt_path": prompt_path,
                        "model_response_path": response_path,
                        "model_prompt_paths": [item["prompt_path"] for item in attempts],
                        "model_response_paths": [item["response_path"] for item in attempts],
                        "materialization_queue_id": args.queue_id,
                        "materialization_strategy": "independent_model_structured_search_replace_programmatic_diff",
                        "normalization_strategy": (
                            "structured_programmatic_diff_ignore_space_change"
                            if structured.get("apply_check_strategy") == "git_apply_ignore_space_change"
                            else ""
                        ),
                        "structured_apply_check_strategy": structured.get("apply_check_strategy"),
                        "generation_backend": args.generation_backend,
                        "generation_model": args.generation_model,
                        "generation_format": args.generation_format,
                        "model_generated": True,
                        "heuristic_candidate": False,
                        "expected_behavior_change": True,
                        "semantic_template": "independent_model_structured_edit_patch",
                        "modified_files": sorted(set(edit["path"] for edit in structured.get("applied_edits", []))),
                        "generation_duration_sec": round(time.time() - total_started, 3),
                        "sample_index": sample_index,
                        "sample_count": sample_count,
                        "structured_attempts": attempts,
                        "structured_edit_count": structured.get("edit_count", 0),
                        "gold_used": False,
                        "created_at": utc_now(),
                    }
                )
                return {"record": record, "duration_sec": record["generation_duration_sec"], "prompt_path": prompt_path, "response_path": response_path}
            repair_feedback = (
                "Attempt {attempt} failed with reason: {reason}\n"
                "Search preview, if any:\n{preview}"
            ).format(
                attempt=attempt,
                reason=structured.get("reason", "unknown"),
                preview=structured.get("search_preview", ""),
            )
        blocked = blocked_record(candidate, args, "structured_edit_failed_after_%s_attempts:%s" % (len(attempts), repair_feedback[:1000]))
        blocked.update(
            {
                "generation_format": args.generation_format,
                "sample_index": sample_index,
                "sample_count": sample_count,
                "structured_attempts": attempts,
                "generation_duration_sec": round(time.time() - total_started, 3),
            }
        )
        return {
            "record": blocked,
            "duration_sec": blocked["generation_duration_sec"],
            "prompt_path": attempts[-1]["prompt_path"] if attempts else "",
            "response_path": attempts[-1]["response_path"] if attempts else "",
        }

    prompt = prompt_for(
        candidate,
        context,
        issue_text,
        args.snapshot_run_dir,
        args.max_context_files,
        args.generation_format,
        "",
        args.max_file_chars,
        args.max_issue_chars,
        sample_index,
        sample_count,
    )
    prompt_path = os.path.join(candidate_dir, "prompt.md")
    response_path = os.path.join(candidate_dir, "response.md")
    diff_path = os.path.join(candidate_dir, "candidate.diff")
    write_text(prompt_path, prompt)
    started = time.time()
    response_text = call_model(args, prompt)
    duration = round(time.time() - started, 3)
    write_text(response_path, response_text)
    diff_text = extract_diff(response_text)
    if not diff_text:
        return {
            "record": blocked_record(candidate, args, "model_response_contained_no_unified_diff"),
            "duration_sec": duration,
            "prompt_path": prompt_path,
            "response_path": response_path,
        }
    write_text(diff_path, diff_text)
    diff_sha = hashlib.sha256(diff_text.encode("utf-8", "replace")).hexdigest()
    record = dict(candidate)
    record.update(
        {
            "original_candidate_id": candidate.get("candidate_id"),
            "candidate_id": "%s::%s::%s" % (task_id, source, candidate_suffix),
            "status": "materialized_model",
            "diff_path": diff_path,
            "diff_sha256": diff_sha,
            "model_prompt_path": prompt_path,
            "model_response_path": response_path,
            "materialization_queue_id": args.queue_id,
            "materialization_strategy": "independent_model_generation",
            "generation_backend": args.generation_backend,
            "generation_model": args.generation_model,
            "generation_format": args.generation_format,
            "model_generated": True,
            "heuristic_candidate": False,
            "expected_behavior_change": True,
            "semantic_template": "independent_model_generated_patch",
            "modified_files": [],
            "generation_duration_sec": duration,
            "sample_index": sample_index,
            "sample_count": sample_count,
            "gold_used": False,
            "created_at": utc_now(),
        }
    )
    return {"record": record, "duration_sec": duration, "prompt_path": prompt_path, "response_path": response_path}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-run-dir", required=True)
    parser.add_argument("--candidate-context-queue-id", required=True)
    parser.add_argument("--queue-id", required=True)
    parser.add_argument("--candidate-manifest", default="")
    parser.add_argument("--target-tasks", default="")
    parser.add_argument("--candidate-source-filter", default="")
    parser.add_argument("--generation-backend", default="openai_chat")
    parser.add_argument("--generation-model", default="gpt-4.1-mini")
    parser.add_argument("--candidate-id-suffix", default="external_model")
    parser.add_argument("--local-model", default="")
    parser.add_argument("--max-context-files", type=int, default=4)
    parser.add_argument("--max-file-chars", type=int, default=MAX_FILE_CHARS)
    parser.add_argument("--max-issue-chars", type=int, default=MAX_ISSUE_CHARS)
    parser.add_argument("--max-new-tokens", type=int, default=1200)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--request-timeout-sec", type=int, default=180)
    parser.add_argument("--generation-format", default=UNIFIED_DIFF_FORMAT, choices=[UNIFIED_DIFF_FORMAT, STRUCTURED_FORMAT])
    parser.add_argument("--repair-attempts", type=int, default=0)
    parser.add_argument("--structured-timeout-sec", type=int, default=90)
    parser.add_argument("--samples-per-candidate", type=int, default=1)
    args = parser.parse_args(argv)
    if args.samples_per_candidate < 1:
        raise RuntimeError("--samples-per-candidate must be >= 1")

    context_queue_dir = os.path.join(args.snapshot_run_dir, "candidate_context_queues", args.candidate_context_queue_id)
    input_manifest = args.candidate_manifest or os.path.join(context_queue_dir, "candidate_pool_manifest.jsonl")
    queue_dir = os.path.join(args.snapshot_run_dir, "candidate_materialization_queues", args.queue_id)
    output_manifest = os.path.join(queue_dir, "candidate_pool_manifest.jsonl")
    target_tasks = parse_targets(args.target_tasks)
    source_filter = parse_targets(args.candidate_source_filter)
    candidates = read_jsonl(input_manifest)
    status = backend_status(args)
    summary = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "context_queue_id": args.candidate_context_queue_id,
        "snapshot_run_dir": args.snapshot_run_dir,
        "input_manifest": input_manifest,
        "output_manifest": output_manifest,
        "target_tasks": sorted(target_tasks),
        "candidate_source_filter": sorted(source_filter),
        "generation_backend": args.generation_backend,
        "generation_model": args.generation_model,
        "generation_format": args.generation_format,
        "repair_attempts": args.repair_attempts,
        "samples_per_candidate": args.samples_per_candidate,
        "temperature": args.temperature,
        "max_file_chars": args.max_file_chars,
        "max_issue_chars": args.max_issue_chars,
        "candidate_id_suffix": args.candidate_id_suffix,
        "local_model": args.local_model,
        "backend_ready": status["ready"],
        "backend_status_reason": status["reason"],
        "started_at": utc_now(),
        "gold_used": False,
        "status_counts": {},
        "source_counts": {},
        "model_generated_count": 0,
        "skipped_non_target_count": 0,
    }
    for candidate in candidates:
        task_id = candidate.get("task_id")
        source = candidate.get("candidate_source") or "unknown"
        if target_tasks and task_id not in target_tasks:
            summary["skipped_non_target_count"] += 1
            continue
        if source_filter and source not in source_filter and source != "noop_control":
            summary["skipped_non_target_count"] += 1
            continue
        try:
            if source == "noop_control":
                record = carry_forward(candidate, args)
                records = [record]
            elif candidate.get("status") == "pending_generation":
                if not status["ready"]:
                    record = blocked_record(candidate, args, status["reason"])
                    records = [record]
                else:
                    records = []
                    for sample_index in range(args.samples_per_candidate):
                        try:
                            records.append(
                                materialize_candidate(candidate, args, queue_dir, sample_index, args.samples_per_candidate)["record"]
                            )
                        except Exception as sample_exc:
                            sample_blocked = blocked_record(
                                candidate,
                                args,
                                "materialization_sample_%02d_exception:%r" % (sample_index, sample_exc),
                            )
                            sample_blocked.update(
                                {
                                    "sample_index": sample_index,
                                    "sample_count": args.samples_per_candidate,
                                    "generation_format": args.generation_format,
                                }
                            )
                            records.append(sample_blocked)
            else:
                summary["skipped_non_target_count"] += 1
                continue
        except Exception as exc:
            records = [blocked_record(candidate, args, "materialization_exception:%r" % (exc,))]
        for record in records:
            append_jsonl(output_manifest, record)
            append_jsonl(os.path.join(queue_dir, "candidate_materialization_results.jsonl"), record)
            record_status = record.get("status") or "unknown"
            summary["status_counts"][record_status] = summary["status_counts"].get(record_status, 0) + 1
            summary["source_counts"][source] = summary["source_counts"].get(source, 0) + 1
            if record.get("model_generated"):
                summary["model_generated_count"] += 1
    summary["finished_at"] = utc_now()
    write_json(os.path.join(queue_dir, "candidate_materialization_summary.json"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
