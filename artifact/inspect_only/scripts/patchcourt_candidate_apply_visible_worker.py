#!/usr/bin/env python3
"""Python 3.6-compatible candidate apply and visible-filter worker.

This stage is gold-blind. It consumes the candidate pool emitted by the
candidate-context stage, materializes candidate worktrees for records that
already have a unified diff, applies the diff, rewrites the public visible
command plan to the candidate worktree, and executes the visible commands.
Pending candidate-generation requests are recorded as not materialized.
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
import glob


GOLD_FIELDS = set(["patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"])
MAX_STREAM_CHARS = 4096


def utc_now():
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def safe_id(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", value or "unknown")[:180]


def read_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            record = json.loads(stripped)
            leaked = sorted(GOLD_FIELDS.intersection(record.keys()))
            if leaked:
                raise RuntimeError("%s:%s contains gold fields: %s" % (path, line_no, leaked))
            if record.get("gold_used") is not False:
                raise RuntimeError("%s:%s must carry gold_used=false" % (path, line_no))
            records.append(record)
    return records


def read_json(path):
    with open(path, "r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    return value


def write_json(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(value)


def append_jsonl(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def truncate_stream(value):
    if len(value) <= MAX_STREAM_CHARS:
        return value, False
    return value[:MAX_STREAM_CHARS], True


def stream_record(path, value):
    write_text(path, value)
    data = value.encode("utf-8", "replace")
    return {
        "path": path,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def load_task_env_routes(path):
    if not path:
        return {}
    if not os.path.exists(path):
        raise RuntimeError("missing task env map: %s" % path)
    value = read_json(path)
    if value.get("gold_used") is not False:
        raise RuntimeError("task env map must carry gold_used=false")
    assert_no_gold_in_map(value, "task_env_map")
    routes = value.get("routes", value)
    if not isinstance(routes, dict):
        raise RuntimeError("task env map routes must be a dict")
    return routes


def assert_no_gold_in_map(value, path):
    if isinstance(value, dict):
        leaked = sorted(GOLD_FIELDS.intersection(value.keys()))
        if leaked:
            raise RuntimeError("%s contains gold fields: %s" % (path, leaked))
        for key, child in value.items():
            assert_no_gold_in_map(child, "%s.%s" % (path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            assert_no_gold_in_map(child, "%s[%s]" % (path, index))


def task_route(task_routes, task_id):
    route = {}
    default_route = task_routes.get("*")
    if isinstance(default_route, dict):
        route.update(default_route)
    specific = task_routes.get(task_id)
    if isinstance(specific, dict):
        route.update(specific)
    return route


def route_venv_dir(default_venv_dir, route):
    return route.get("venv_dir") or default_venv_dir


def run_shell(command, cwd=None, timeout=180, env=None):
    started = time.time()
    timed_out = False
    try:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=cwd,
            env=env,
        )
        try:
            out, err = proc.communicate(timeout=timeout)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            out, err = proc.communicate()
            exit_code = -124
    except Exception as exc:
        out, err = b"", repr(exc).encode("utf-8")
        exit_code = -1
    finished = time.time()
    return {
        "command": command,
        "cwd": cwd or "",
        "exit_code": exit_code,
        "timed_out": timed_out,
        "duration_sec": round(finished - started, 3),
        "stdout": out.decode("utf-8", "replace"),
        "stderr": err.decode("utf-8", "replace"),
    }


def python_path(venv_dir):
    candidate = os.path.join(venv_dir, "bin", "python") if venv_dir else ""
    if candidate and os.path.exists(candidate):
        return candidate
    return sys.executable


def command_output(command, cwd=None, timeout=30, env=None):
    result = run_shell(command, cwd=cwd, timeout=timeout, env=env)
    if result["exit_code"] != 0:
        raise RuntimeError(
            "command failed (%s): %s%s"
            % (result["exit_code"], result.get("stdout") or "", result.get("stderr") or "")
        )
    return result.get("stdout", "").strip()


def write_pytest_version_file(candidate_repo):
    path = os.path.join(candidate_repo, "src", "_pytest", "_version.py")
    if not os.path.isdir(os.path.dirname(path)):
        return {"status": "skipped_missing_dir", "path": path}
    content = "version = '7.3.0+patchcourt'\nversion_tuple = (7, 3, 0)\n"
    write_text(path, content)
    return {"status": "ok", "path": path, "bytes": len(content.encode("utf-8"))}


def write_sklearn_check_build_stub(candidate_repo):
    path = os.path.join(candidate_repo, "sklearn", "__check_build", "_check_build.py")
    if not os.path.isdir(os.path.dirname(path)):
        return {"status": "skipped_missing_dir", "path": path}
    content = "def check_build():\n    return True\n"
    write_text(path, content)
    return {"status": "ok", "path": path, "bytes": len(content.encode("utf-8"))}


def write_sklearn_import_stubs(candidate_repo):
    check_result = write_sklearn_check_build_stub(candidate_repo)
    murmur_path = os.path.join(candidate_repo, "sklearn", "utils", "murmurhash.py")
    if not os.path.isdir(os.path.dirname(murmur_path)):
        return {
            "status": "skipped_missing_dir",
            "check_build": check_result,
            "murmurhash_path": murmur_path,
        }
    content = (
        "def murmurhash3_32(key, seed=0, positive=False):\n"
        "    value = hash((key, seed)) & 0xFFFFFFFF\n"
        "    if positive:\n"
        "        return value\n"
        "    return value - 0x100000000 if value & 0x80000000 else value\n"
    )
    write_text(murmur_path, content)
    return {
        "status": "ok",
        "check_build": check_result,
        "murmurhash_path": murmur_path,
        "bytes": len(content.encode("utf-8")),
    }


def copy_installed_matplotlib_extensions(candidate_repo, venv_dir, timeout):
    target_dir = os.path.join(candidate_repo, "lib", "matplotlib")
    if not os.path.isdir(target_dir):
        return {"status": "skipped_missing_dir", "target_dir": target_dir}
    py = python_path(venv_dir)
    site = command_output(
        "%s - <<'PY'\nimport matplotlib, os\nprint(os.path.dirname(matplotlib.__file__))\nPY" % shell_quote(py),
        cwd=candidate_repo,
        timeout=timeout,
    )
    copied = []
    for source in sorted(glob.glob(os.path.join(site, "*.so"))):
        dest = os.path.join(target_dir, os.path.basename(source))
        shutil.copy2(source, dest)
        copied.append(os.path.basename(dest))
    version_source = os.path.join(site, "_version.py")
    version_dest = os.path.join(target_dir, "_version.py")
    if os.path.exists(version_source):
        shutil.copy2(version_source, version_dest)
        copied.append("_version.py")
    elif not os.path.exists(version_dest):
        write_text(version_dest, "version = '0+patchcourt'\n__version__ = version\n")
        copied.append("_version.py")
    return {
        "status": "ok",
        "source_site_package": site,
        "target_dir": target_dir,
        "copied": copied,
    }


def shell_quote(value):
    return "'" + (value or "").replace("'", "'\"'\"'") + "'"


def run_pre_visible_steps(candidate_repo, route, venv_dir, timeout):
    steps = route.get("pre_visible_steps") or []
    results = []
    for step in steps:
        started = time.time()
        try:
            if step == "write_pytest_version_file":
                result = write_pytest_version_file(candidate_repo)
            elif step == "write_sklearn_check_build_stub":
                result = write_sklearn_check_build_stub(candidate_repo)
            elif step == "write_sklearn_import_stubs":
                result = write_sklearn_import_stubs(candidate_repo)
            elif step == "copy_installed_matplotlib_extensions":
                result = copy_installed_matplotlib_extensions(candidate_repo, venv_dir, timeout)
            else:
                result = {"status": "unknown_step", "step": step}
        except Exception as exc:
            result = {"status": "failed", "step": step, "error": repr(exc)}
        result.update(
            {
                "step": step,
                "duration_sec": round(time.time() - started, 3),
                "created_at": utc_now(),
            }
        )
        results.append(result)
    return results


def parse_version(value):
    parts = []
    for item in re.findall(r"\d+", value or "")[:3]:
        parts.append(int(item))
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def read_file(path, limit=65536):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read(limit)
    except IOError:
        return ""


def current_python_version(venv_dir):
    python_path = os.path.join(venv_dir, "bin", "python") if venv_dir else sys.executable
    if not os.path.exists(python_path):
        python_path = sys.executable
    try:
        proc = subprocess.Popen(
            [python_path, "-c", "import sys; print('%s.%s.%s' % sys.version_info[:3])"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, _ = proc.communicate(timeout=10)
        if proc.returncode == 0:
            return out.decode("utf-8", "replace").strip()
    except Exception:
        pass
    return "%s.%s.%s" % sys.version_info[:3]


def detect_python_requires(cwd):
    candidates = [
        os.path.join(cwd, "setup.cfg"),
        os.path.join(cwd, "pyproject.toml"),
        os.path.join(cwd, "setup.py"),
    ]
    for path in candidates:
        text = read_file(path)
        if not text:
            continue
        patterns = [
            r"python_requires\s*=\s*['\"]?([^'\"\r\n,]+)",
            r"['\"]python_requires['\"]\s*:\s*['\"]([^'\"]+)",
            r"requires-python\s*=\s*['\"]([^'\"]+)",
            r"requires_python\s*=\s*['\"]([^'\"]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
    return ""


def min_python_version(requirement):
    if not requirement:
        return None
    matches = re.findall(r">=\s*([0-9]+(?:\.[0-9]+){0,2})", requirement)
    if matches:
        return parse_version(matches[0])
    matches = re.findall(r">\s*([0-9]+(?:\.[0-9]+){0,2})", requirement)
    if matches:
        parsed = list(parse_version(matches[0]))
        parsed[-1] += 1
        return tuple(parsed)
    return None


def command_uses_python(command):
    cmd = command.get("cmd") or ""
    return "python" in cmd or "pytest" in cmd


def environment_resolution(command, venv_dir):
    current = current_python_version(venv_dir)
    requirement = detect_python_requires(command.get("cwd") or "")
    required_min = min_python_version(requirement)
    current_tuple = parse_version(current)
    incompatible = bool(required_min and current_tuple < required_min and command_uses_python(command))
    return {
        "python_version": current,
        "python_requires": requirement,
        "required_min_python": ".".join(str(part) for part in required_min) if required_min else "",
        "venv_dir": venv_dir,
        "status": "python_version_incompatible" if incompatible else "ok",
    }


def classify_visible_result(result):
    if result.get("skipped"):
        if result.get("skip_kind"):
            return result.get("skip_kind")
        return "environment_python_version"
    if result.get("timed_out"):
        return "timeout"
    if result.get("exit_code") == 0:
        return "none"
    if result.get("name", "").startswith("pytest"):
        return "pytest_collect_failure"
    return "command_failure"


def is_pytest_no_tests_collected(command, exit_code, stdout, stderr):
    if exit_code != 5:
        return False
    cmd = command.get("cmd") or ""
    name = command.get("name") or ""
    if "pytest" not in cmd and not name.startswith("pytest"):
        return False
    combined = (stdout or "") + "\n" + (stderr or "")
    return "no tests collected" in combined.lower()


def missing_dependency_name(stdout, stderr):
    combined = (stdout or "") + "\n" + (stderr or "")
    patterns = [
        r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)['\"]",
        r"ImportError:\s+No module named ['\"]([^'\"]+)['\"]",
    ]
    for pattern in patterns:
        match = re.search(pattern, combined)
        if match:
            return match.group(1).split(".")[0]
    return ""


def visible_artifact_paths(queue_dir, candidate, command):
    artifact_dir = os.path.join(
        queue_dir,
        "visible_artifacts",
        safe_id(candidate.get("candidate_id")),
        safe_id(command.get("command_id")),
    )
    return {
        "dir": artifact_dir,
        "stdout": os.path.join(artifact_dir, "stdout.txt"),
        "stderr": os.path.join(artifact_dir, "stderr.txt"),
        "result": os.path.join(artifact_dir, "result.json"),
    }


def visible_env(venv_dir, worker_gpu):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["CUDA_VISIBLE_DEVICES"] = str(worker_gpu)
    if venv_dir:
        venv_bin = os.path.join(venv_dir, "bin")
        if os.path.isdir(venv_bin):
            env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")
    return env


def run_visible_command(command, candidate, timeout, venv_dir, worker_gpu, queue_dir, route):
    artifacts = visible_artifact_paths(queue_dir, candidate, command)
    environment = environment_resolution(command, venv_dir)
    started = time.time()
    started_at = utc_now()
    timed_out = False
    skipped = False
    skip_reason = ""
    skip_kind = ""
    original_exit_code = None
    if environment["status"] != "ok":
        skipped = True
        skip_reason = (
            "Command requires repository Python %s but active venv is Python %s"
            % (environment.get("python_requires") or "unknown", environment["python_version"])
        )
        skip_kind = "environment_python_version"
        stdout_full = ""
        stderr_full = skip_reason
        exit_code = 125
    else:
        result = run_shell(
            command["cmd"],
            cwd=command["cwd"],
            timeout=timeout,
            env=visible_env(venv_dir, worker_gpu),
        )
        stdout_full = result["stdout"]
        stderr_full = result["stderr"]
        exit_code = result["exit_code"]
        timed_out = result["timed_out"]
        original_exit_code = exit_code
        if route.get("classify_pytest_no_tests_collected_as_skip") and is_pytest_no_tests_collected(
            command, exit_code, stdout_full, stderr_full
        ):
            skipped = True
            skip_reason = "pytest collect command produced no executable tests"
            skip_kind = "pytest_no_tests_collected"
            exit_code = 125
        else:
            skip_modules = set(route.get("classify_missing_dependency_as_skip_modules") or [])
            missing_module = missing_dependency_name(stdout_full, stderr_full)
            if missing_module and missing_module in skip_modules:
                skipped = True
                skip_reason = "visible command requires missing dependency module %s" % missing_module
                skip_kind = "environment_missing_dependency"
                exit_code = 125
    finished = time.time()
    stdout, stdout_truncated = truncate_stream(stdout_full)
    stderr, stderr_truncated = truncate_stream(stderr_full)
    stdout_artifact = stream_record(artifacts["stdout"], stdout_full)
    stderr_artifact = stream_record(artifacts["stderr"], stderr_full)
    record = {
        "schema_version": "0.1",
        "queue_id": candidate.get("apply_queue_id"),
        "context_queue_id": candidate.get("context_queue_id"),
        "candidate_id": candidate.get("candidate_id"),
        "candidate_source": candidate.get("candidate_source"),
        "task_id": candidate.get("task_id"),
        "repo": candidate.get("repo"),
        "command_id": command.get("command_id"),
        "base_command_id": command.get("base_command_id"),
        "name": command.get("name"),
        "cmd": command.get("cmd"),
        "cwd": command.get("cwd"),
        "candidate_repo": candidate.get("candidate_repo"),
        "exit_code": exit_code,
        "original_exit_code": original_exit_code,
        "timed_out": timed_out,
        "skipped": skipped,
        "skip_reason": skip_reason,
        "skip_kind": skip_kind,
        "environment": environment,
        "duration_sec": round(finished - started, 3),
        "started_at": started_at,
        "finished_at": utc_now(),
        "stdout": stdout,
        "stderr": stderr,
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
        "stdout_artifact": stdout_artifact,
        "stderr_artifact": stderr_artifact,
        "gold_used": False,
    }
    record["error_class"] = classify_visible_result(record)
    write_json(artifacts["result"], record)
    return record


def copy_repo(base_repo, candidate_repo):
    if not os.path.isdir(base_repo):
        raise RuntimeError("missing base repo: %s" % base_repo)
    if os.path.exists(candidate_repo):
        raise RuntimeError("candidate repo already exists: %s" % candidate_repo)
    shutil.copytree(base_repo, candidate_repo, symlinks=True)


def apply_diff(candidate, candidate_repo, timeout):
    diff_path = candidate.get("diff_path") or ""
    if not diff_path:
        return {
            "status": "missing_diff_path",
            "diff_path": diff_path,
            "check": None,
            "apply": None,
        }
    if not os.path.exists(diff_path):
        return {
            "status": "missing_diff_file",
            "diff_path": diff_path,
            "check": None,
            "apply": None,
        }
    try:
        diff_size = os.path.getsize(diff_path)
    except OSError:
        diff_size = -1
    if diff_size == 0:
        return {
            "status": "applied_noop",
            "diff_path": diff_path,
            "diff_size": diff_size,
            "check": None,
            "apply": None,
        }
    quoted = "'" + diff_path.replace("'", "'\"'\"'") + "'"
    apply_strategy = "git_apply_strict"
    check = run_shell("git apply --check %s" % quoted, cwd=candidate_repo, timeout=timeout)
    if check["exit_code"] != 0 and candidate.get("normalization_strategy"):
        whitespace_check = run_shell(
            "git apply --check --ignore-space-change %s" % quoted,
            cwd=candidate_repo,
            timeout=timeout,
        )
        if whitespace_check["exit_code"] == 0:
            apply_strategy = "git_apply_ignore_space_change_after_normalization"
            check = whitespace_check
    if check["exit_code"] != 0:
        return {
            "status": "apply_check_failed",
            "diff_path": diff_path,
            "diff_size": diff_size,
            "apply_strategy": apply_strategy,
            "check": check,
            "apply": None,
        }
    apply_command = "git apply %s" % quoted
    if apply_strategy == "git_apply_ignore_space_change_after_normalization":
        apply_command = "git apply --ignore-space-change %s" % quoted
    applied = run_shell(apply_command, cwd=candidate_repo, timeout=timeout)
    return {
        "status": "applied" if applied["exit_code"] == 0 else "apply_failed",
        "diff_path": diff_path,
        "diff_size": diff_size,
        "apply_strategy": apply_strategy,
        "check": check,
        "apply": applied,
    }


def load_base_visible_plan(snapshot_run_dir, task_id):
    plan_path = os.path.join(snapshot_run_dir, "worktrees", safe_id(task_id), "visible_command_plan.jsonl")
    if not os.path.exists(plan_path):
        return plan_path, []
    return plan_path, read_jsonl(plan_path)


def rewrite_visible_plan(base_commands, candidate, candidate_repo):
    rewritten = []
    for index, command in enumerate(base_commands):
        updated = dict(command)
        base_command_id = command.get("command_id")
        updated.update(
            {
                "schema_version": "0.1",
                "command_id": "%s::visible::%02d" % (candidate.get("candidate_id"), index),
                "base_command_id": base_command_id,
                "candidate_id": candidate.get("candidate_id"),
                "candidate_source": candidate.get("candidate_source"),
                "context_queue_id": candidate.get("context_queue_id"),
                "apply_queue_id": candidate.get("apply_queue_id"),
                "cwd": candidate_repo,
                "candidate_repo": candidate_repo,
                "gold_used": False,
            }
        )
        rewritten.append(updated)
    return rewritten


def summarize_visible(results):
    executable_count = len([item for item in results if not item.get("skipped")])
    pass_count = len([item for item in results if not item.get("skipped") and item.get("exit_code") == 0])
    fail_count = len([item for item in results if not item.get("skipped") and item.get("exit_code") != 0])
    skipped_count = len([item for item in results if item.get("skipped")])
    timed_out_count = len([item for item in results if item.get("timed_out")])
    error_class_counts = {}
    for item in results:
        key = item.get("error_class") or "unknown"
        error_class_counts[key] = error_class_counts.get(key, 0) + 1
    strict_visible_pass = bool(results and fail_count == 0 and skipped_count == 0)
    compatible_visible_pass = bool(executable_count > 0 and fail_count == 0)
    return {
        "command_count": len(results),
        "executable_count": executable_count,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "skipped_count": skipped_count,
        "timed_out_count": timed_out_count,
        "error_class_counts": error_class_counts,
        "strict_visible_pass": strict_visible_pass,
        "compatible_visible_pass": compatible_visible_pass,
    }


def materialized_candidate(candidate):
    if candidate.get("status") in ("materialized", "materialized_control"):
        return True
    diff_path = candidate.get("diff_path") or ""
    return bool(diff_path and os.path.exists(diff_path))


def not_materialized_result(candidate, args, queue_dir):
    record = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "context_queue_id": args.candidate_context_queue_id,
        "candidate_id": candidate.get("candidate_id"),
        "candidate_source": candidate.get("candidate_source"),
        "task_id": candidate.get("task_id"),
        "repo": candidate.get("repo"),
        "worker_id": args.worker_id,
        "gpu": args.gpu,
        "candidate_record_status": candidate.get("status"),
        "apply_status": "not_materialized",
        "reason": "candidate request has no materialized unified diff yet",
        "diff_path": candidate.get("diff_path") or "",
        "visible_summary": summarize_visible([]),
        "gold_used": False,
        "created_at": utc_now(),
    }
    append_jsonl(os.path.join(queue_dir, "candidate_apply_results.jsonl"), record)
    return record


def process_candidate(candidate, args, queue_dir):
    if not materialized_candidate(candidate):
        return not_materialized_result(candidate, args, queue_dir)

    task_id = candidate.get("task_id")
    route = task_route(args.task_env_routes, task_id)
    effective_venv_dir = route_venv_dir(args.venv_dir, route)
    candidate_id = candidate.get("candidate_id")
    base_repo = os.path.join(args.snapshot_run_dir, "worktrees", safe_id(task_id), "repo")
    candidate_dir = os.path.join(queue_dir, "candidates", safe_id(candidate_id))
    candidate_repo = os.path.join(candidate_dir, "repo")
    os.makedirs(candidate_dir, exist_ok=False)
    copy_repo(base_repo, candidate_repo)

    candidate_augmented = dict(candidate)
    candidate_augmented.update(
        {
            "apply_queue_id": args.queue_id,
            "context_queue_id": args.candidate_context_queue_id,
            "candidate_dir": candidate_dir,
            "candidate_repo": candidate_repo,
            "gold_used": False,
        }
    )
    apply_result = apply_diff(candidate, candidate_repo, args.timeout_sec)
    pre_visible_results = []
    if apply_result["status"] in ("applied", "applied_noop"):
        pre_visible_results = run_pre_visible_steps(
            candidate_repo,
            route,
            effective_venv_dir,
            args.timeout_sec,
        )
    plan_path, base_commands = load_base_visible_plan(args.snapshot_run_dir, task_id)
    visible_plan = rewrite_visible_plan(base_commands, candidate_augmented, candidate_repo)
    plan_out = os.path.join(candidate_dir, "candidate_visible_command_plan.jsonl")
    for command in visible_plan:
        append_jsonl(plan_out, command)

    visible_results = []
    if apply_result["status"] in ("applied", "applied_noop"):
        for command in visible_plan:
            visible_result = run_visible_command(
                command,
                candidate_augmented,
                args.timeout_sec,
                effective_venv_dir,
                args.gpu,
                queue_dir,
                route,
            )
            visible_results.append(visible_result)
            append_jsonl(os.path.join(candidate_dir, "candidate_visible_results.jsonl"), visible_result)
            append_jsonl(os.path.join(queue_dir, "candidate_visible_results.jsonl"), visible_result)

    result = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "context_queue_id": args.candidate_context_queue_id,
        "candidate_id": candidate_id,
        "candidate_source": candidate.get("candidate_source"),
        "candidate_record_status": candidate.get("status"),
        "task_id": task_id,
        "repo": candidate.get("repo"),
        "worker_id": args.worker_id,
        "gpu": args.gpu,
        "base_repo": base_repo,
        "candidate_dir": candidate_dir,
        "candidate_repo": candidate_repo,
        "diff_path": candidate.get("diff_path") or "",
        "normalization_queue_id": candidate.get("normalization_queue_id"),
        "normalization_status": candidate.get("normalization_status"),
        "normalization_strategy": candidate.get("normalization_strategy"),
        "original_diff_path": candidate.get("original_diff_path"),
        "apply_result": apply_result,
        "apply_status": apply_result.get("status"),
        "task_environment_route": route,
        "effective_venv_dir": effective_venv_dir,
        "pre_visible_results": pre_visible_results,
        "base_visible_plan_path": plan_path,
        "candidate_visible_plan_path": plan_out,
        "visible_summary": summarize_visible(visible_results),
        "gold_used": False,
        "created_at": utc_now(),
    }
    write_json(os.path.join(candidate_dir, "candidate_apply_result.json"), result)
    append_jsonl(os.path.join(queue_dir, "candidate_apply_results.jsonl"), result)
    append_jsonl(os.path.join(queue_dir, "materialized_candidate_manifest.jsonl"), candidate_augmented)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-run-dir", required=True)
    parser.add_argument("--candidate-context-queue-id", required=True)
    parser.add_argument("--candidate-manifest", default="")
    parser.add_argument("--queue-id", required=True)
    parser.add_argument("--worker-id", type=int, required=True)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--gpu", required=True)
    parser.add_argument("--timeout-sec", type=int, default=180)
    parser.add_argument("--venv-dir", default="")
    parser.add_argument("--task-env-map", default="")
    args = parser.parse_args(argv)
    args.task_env_routes = load_task_env_routes(args.task_env_map)

    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu)
    context_queue_dir = os.path.join(
        args.snapshot_run_dir,
        "candidate_context_queues",
        args.candidate_context_queue_id,
    )
    candidate_manifest = args.candidate_manifest or os.path.join(
        context_queue_dir,
        "candidate_pool_manifest.jsonl",
    )
    candidates = read_jsonl(candidate_manifest)
    assigned = [
        candidate for index, candidate in enumerate(candidates) if index % args.num_workers == args.worker_id
    ]
    queue_dir = os.path.join(args.snapshot_run_dir, "candidate_apply_queues", args.queue_id)
    worker_dir = os.path.join(queue_dir, "workers", "worker_%02d_gpu_%s" % (args.worker_id, args.gpu))
    os.makedirs(worker_dir, exist_ok=True)

    summary = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "context_queue_id": args.candidate_context_queue_id,
        "snapshot_run_dir": args.snapshot_run_dir,
        "candidate_manifest": candidate_manifest,
        "worker_id": args.worker_id,
        "num_workers": args.num_workers,
        "gpu": args.gpu,
        "assigned_candidate_count": len(assigned),
        "timeout_sec": args.timeout_sec,
        "venv_dir": args.venv_dir,
        "task_env_map": args.task_env_map,
        "task_env_route_count": len(args.task_env_routes),
        "started_at": utc_now(),
        "gold_used": False,
        "apply_status_counts": {},
        "visible_strict_pass_count": 0,
        "visible_compatible_pass_count": 0,
        "visible_command_count": 0,
        "results": [],
    }
    for candidate in assigned:
        result = process_candidate(candidate, args, queue_dir)
        summary["results"].append(result)
        status = result.get("apply_status") or "unknown"
        summary["apply_status_counts"][status] = summary["apply_status_counts"].get(status, 0) + 1
        visible_summary = result.get("visible_summary") or {}
        if visible_summary.get("strict_visible_pass"):
            summary["visible_strict_pass_count"] += 1
        if visible_summary.get("compatible_visible_pass"):
            summary["visible_compatible_pass_count"] += 1
        summary["visible_command_count"] += visible_summary.get("command_count", 0)
    summary["finished_at"] = utc_now()
    write_json(os.path.join(worker_dir, "candidate_apply_visible_worker_summary.json"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
