#!/usr/bin/env python3
"""Normalize independent-model diffs into strict git-apply candidates.

The external model lane preserves the raw model response. This optional,
append-only normalization layer tries to apply those raw diffs with GNU patch
fuzz, then re-exports the resulting repository delta as a strict git diff.
It records the normalization strategy so these candidates can be reported
separately from raw strict diffs.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def utc_now() -> str:
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def safe_id(value: str | None) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", value or "unknown")[:180]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()


def run(cmd: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )


def copy_repo(src: Path, dst: Path) -> None:
    ignore = shutil.ignore_patterns(".git/objects/pack/tmp_*", "__pycache__", ".pytest_cache")
    shutil.copytree(str(src), str(dst), symlinks=True, ignore=ignore)


def initialize_diff_repo(repo: Path, timeout: int) -> None:
    git_dir = repo / ".git"
    if git_dir.exists():
        shutil.rmtree(str(git_dir), ignore_errors=True)
    run(["git", "init"], repo, timeout)
    run(["git", "add", "-A"], repo, timeout)
    run(
        [
            "git",
            "-c",
            "user.name=PatchCourt",
            "-c",
            "user.email=patchcourt@example.invalid",
            "commit",
            "--allow-empty",
            "-m",
            "patchcourt-normalization-base",
        ],
        repo,
        timeout,
    )


def apply_with_patch_fuzz(raw_diff: Path, repo: Path, fuzz: int, timeout: int) -> tuple[str, subprocess.CompletedProcess]:
    attempts = [
        ("patch_p1_fuzz", ["patch", "-p1", "--batch", "--fuzz=%s" % fuzz, "-i", str(raw_diff)]),
        ("patch_p1_fuzz_ignore_ws", ["patch", "-p1", "--batch", "-l", "--fuzz=%s" % fuzz, "-i", str(raw_diff)]),
        ("patch_p0_fuzz", ["patch", "-p0", "--batch", "--fuzz=%s" % fuzz, "-i", str(raw_diff)]),
        ("patch_p0_fuzz_ignore_ws", ["patch", "-p0", "--batch", "-l", "--fuzz=%s" % fuzz, "-i", str(raw_diff)]),
    ]
    last = None
    for name, cmd in attempts:
        cp = run(cmd, repo, timeout)
        if cp.returncode == 0:
            return name, cp
        last = cp
    return "patch_fuzz_failed", last


def normalize_model_record(record: dict, args: argparse.Namespace, queue_dir: Path) -> dict:
    task_id = record.get("task_id")
    source = record.get("candidate_source") or "unknown"
    base_repo = Path(args.snapshot_run_dir) / "worktrees" / safe_id(task_id) / "repo"
    raw_diff = Path(record.get("diff_path") or "")
    out_dir = queue_dir / "tasks" / safe_id(task_id) / "candidates" / safe_id(source)
    out_diff = out_dir / "candidate.diff"
    out_dir.mkdir(parents=True, exist_ok=True)

    normalized = dict(record)
    normalized.update(
        {
            "original_diff_path": str(raw_diff),
            "original_diff_sha256": file_sha256(raw_diff) if raw_diff.exists() else "",
            "normalization_queue_id": args.queue_id,
            "normalization_created_at": utc_now(),
            "gold_used": False,
        }
    )

    if not raw_diff.exists():
        normalized.update(
            {
                "status": "blocked_no_independent_model_source",
                "normalization_status": "raw_diff_missing",
                "blocked_reason": "raw_diff_missing",
            }
        )
        return normalized

    tmp_root = Path(tempfile.mkdtemp(prefix="patchcourt_diff_normalize_"))
    try:
        repo_copy = tmp_root / "repo"
        copy_repo(base_repo, repo_copy)
        initialize_diff_repo(repo_copy, args.timeout_sec)

        strict = run(["git", "apply", "--check", str(raw_diff)], repo_copy, args.timeout_sec)
        if strict.returncode == 0:
            shutil.copyfile(str(raw_diff), str(out_diff))
            normalized.update(
                {
                    "diff_path": str(out_diff),
                    "diff_sha256": file_sha256(out_diff),
                    "normalization_status": "strict_git_apply_already_valid",
                    "normalization_strategy": "strict_copy",
                    "materialization_strategy": record.get("materialization_strategy", "independent_model_generation"),
                    "status": "materialized_model",
                }
            )
            return normalized

        fuzz_strategy, fuzz = apply_with_patch_fuzz(raw_diff, repo_copy, args.fuzz, args.timeout_sec)
        if fuzz.returncode != 0:
            normalized.update(
                {
                    "status": "blocked_no_independent_model_source",
                    "normalization_status": fuzz_strategy,
                    "blocked_reason": fuzz_strategy,
                    "normalization_stdout": fuzz.stdout[-2000:],
                    "normalization_stderr": fuzz.stderr[-2000:],
                }
            )
            return normalized

        diff = run(["git", "diff", "--no-ext-diff", "--binary"], repo_copy, args.timeout_sec)
        if diff.returncode != 0 or not diff.stdout.strip():
            normalized.update(
                {
                    "status": "blocked_no_independent_model_source",
                    "normalization_status": "normalized_diff_empty_or_failed",
                    "blocked_reason": "normalized_diff_empty_or_failed",
                    "normalization_stdout": diff.stdout[-2000:],
                    "normalization_stderr": diff.stderr[-2000:],
                }
            )
            return normalized

        out_diff.write_text(diff.stdout, encoding="utf-8", newline="\n")
        normalized.update(
            {
                "diff_path": str(out_diff),
                "diff_sha256": text_sha256(diff.stdout),
                "normalization_status": "patch_fuzz_reexported_git_diff",
                "normalization_strategy": "gnu_%s_reexport" % fuzz_strategy,
                "normalization_fuzz": args.fuzz,
                "normalization_stdout": fuzz.stdout[-2000:],
                "normalization_stderr": fuzz.stderr[-2000:],
                "materialization_strategy": "independent_model_generation_patch_fuzz_normalized",
                "status": "materialized_model",
            }
        )
        return normalized
    finally:
        shutil.rmtree(str(tmp_root), ignore_errors=True)


def carry_record(record: dict, args: argparse.Namespace) -> dict:
    carried = dict(record)
    carried.update({"normalization_queue_id": args.queue_id, "normalization_status": "carried_forward", "gold_used": False})
    return carried


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-run-dir", required=True)
    parser.add_argument("--candidate-manifest", required=True)
    parser.add_argument("--queue-id", required=True)
    parser.add_argument("--fuzz", type=int, default=3)
    parser.add_argument("--timeout-sec", type=int, default=60)
    args = parser.parse_args()

    queue_dir = Path(args.snapshot_run_dir) / "candidate_materialization_queues" / args.queue_id
    output_manifest = queue_dir / "candidate_pool_manifest.jsonl"
    summary = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "snapshot_run_dir": args.snapshot_run_dir,
        "input_manifest": args.candidate_manifest,
        "output_manifest": str(output_manifest),
        "fuzz": args.fuzz,
        "timeout_sec": args.timeout_sec,
        "started_at": utc_now(),
        "gold_used": False,
        "status_counts": {},
        "normalization_status_counts": {},
        "model_generated_count": 0,
    }

    for record in read_jsonl(Path(args.candidate_manifest)):
        if record.get("status") == "materialized_model" and record.get("diff_path"):
            out = normalize_model_record(record, args, queue_dir)
        else:
            out = carry_record(record, args)
        append_jsonl(output_manifest, out)
        append_jsonl(queue_dir / "candidate_normalization_results.jsonl", out)
        status = out.get("status") or "unknown"
        norm_status = out.get("normalization_status") or "unknown"
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1
        summary["normalization_status_counts"][norm_status] = summary["normalization_status_counts"].get(norm_status, 0) + 1
        if out.get("model_generated") and out.get("status") == "materialized_model":
            summary["model_generated_count"] += 1

    summary["finished_at"] = utc_now()
    write_json(queue_dir / "candidate_normalization_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
