#!/usr/bin/env python3
"""Build PatchCourt behavioral disagreement certificates from probe results."""

from __future__ import print_function

import argparse
import collections
import datetime as _dt
import hashlib
import json
import os
import re
import sys


GOLD_FIELDS = set(["patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"])
MAX_EXCERPT_CHARS = 600


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


def excerpt(value):
    value = value or ""
    if len(value) <= MAX_EXCERPT_CHARS:
        return value
    return value[:MAX_EXCERPT_CHARS] + "\n...[truncated]"


def certificate_for(args, task_id, probe_id, rows):
    groups = collections.defaultdict(list)
    for row in rows:
        groups[row.get("behavior_hash")].append(row)
    if len(groups) < 2:
        return None
    group_records = []
    for behavior_hash, items in sorted(groups.items(), key=lambda pair: pair[0]):
        representative = items[0]
        group_records.append(
            {
                "behavior_hash": behavior_hash,
                "candidate_count": len(items),
                "outcome": representative.get("outcome"),
                "exit_code": representative.get("exit_code"),
                "stdout_excerpt": excerpt(representative.get("stdout")),
                "stderr_excerpt": excerpt(representative.get("stderr")),
                "candidates": [
                    {
                        "candidate_id": item.get("candidate_id"),
                        "candidate_source": item.get("candidate_source"),
                        "candidate_repo": item.get("candidate_repo"),
                        "candidate_model_generated": bool(item.get("candidate_model_generated")),
                        "candidate_heuristic": bool(item.get("candidate_heuristic")),
                        "candidate_semantic_template": item.get("candidate_semantic_template") or "",
                        "candidate_generation_backend": item.get("candidate_generation_backend") or "",
                    }
                    for item in sorted(items, key=lambda r: r.get("candidate_id") or "")
                ],
            }
        )
    digest_input = json.dumps(
        {
            "task_id": task_id,
            "probe_id": probe_id,
            "groups": [
                {
                    "behavior_hash": group["behavior_hash"],
                    "candidate_ids": [c["candidate_id"] for c in group["candidates"]],
                }
                for group in group_records
            ],
        },
        sort_keys=True,
    ).encode("utf-8")
    cert_id = "%s::%s::%s" % (
        task_id,
        probe_id,
        hashlib.sha256(digest_input).hexdigest()[:12],
    )
    return {
        "schema_version": "0.1",
        "certificate_id": cert_id,
        "queue_id": args.queue_id,
        "probe_queue_id": args.probe_queue_id,
        "apply_queue_id": rows[0].get("apply_queue_id"),
        "task_id": task_id,
        "repo": rows[0].get("repo"),
        "probe_id": probe_id,
        "probe_description": rows[0].get("probe_description"),
        "candidate_count": len(rows),
        "behavior_group_count": len(group_records),
        "pass_count": len([row for row in rows if row.get("outcome") == "pass"]),
        "fail_count": len([row for row in rows if row.get("outcome") == "fail"]),
        "timeout_count": len([row for row in rows if row.get("outcome") == "timeout"]),
        "model_generated_candidate_count": len([row for row in rows if row.get("candidate_model_generated")]),
        "heuristic_candidate_count": len([row for row in rows if row.get("candidate_heuristic")]),
        "groups": group_records,
        "interpretation": "Visible-passing candidate patches disagree under an issue-derived executable probe.",
        "gold_used": False,
        "created_at": utc_now(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-run-dir", required=True)
    parser.add_argument("--probe-queue-id", required=True)
    parser.add_argument("--queue-id", required=True)
    args = parser.parse_args(argv)

    probe_queue_dir = os.path.join(args.snapshot_run_dir, "issue_probe_queues", args.probe_queue_id)
    probe_results_path = os.path.join(probe_queue_dir, "issue_probe_results.jsonl")
    rows = read_jsonl(probe_results_path)
    grouped = collections.defaultdict(list)
    for row in rows:
        grouped[(row.get("task_id"), row.get("probe_id"))].append(row)

    queue_dir = os.path.join(args.snapshot_run_dir, "bdc_queues", args.queue_id)
    cert_path = os.path.join(queue_dir, "behavior_disagreement_certificates.jsonl")
    certificates = []
    for (task_id, probe_id), items in sorted(grouped.items()):
        cert = certificate_for(args, task_id, probe_id, items)
        if cert:
            certificates.append(cert)
            append_jsonl(cert_path, cert)
    summary = {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "probe_queue_id": args.probe_queue_id,
        "probe_results_path": probe_results_path,
        "certificate_path": cert_path,
        "probe_result_count": len(rows),
        "probe_group_count": len(grouped),
        "certificate_count": len(certificates),
        "certificate_task_count": len(set(cert["task_id"] for cert in certificates)),
        "gold_used": False,
        "created_at": utc_now(),
        "certificates": certificates,
    }
    write_json(os.path.join(queue_dir, "bdc_summary.json"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
