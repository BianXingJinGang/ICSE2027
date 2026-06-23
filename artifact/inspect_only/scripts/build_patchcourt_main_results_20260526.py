#!/usr/bin/env python3
"""Build PatchCourt main-result tables from frozen, append-only artifacts."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
AUDIT_DIR = ROOT / "audit_30plus_20260526"
FROZEN_INDEX = AUDIT_DIR / "frozen_post_audit_20260526" / "frozen_certificate_index_20260526.json"
HELDOUT_RESULTS = ROOT / "heldout_calibration_queue_20260526_124819_results.jsonl"
UPGRADE_RESULTS = ROOT / "audit_probe_upgrade_queue_20260526_131117_results.jsonl"
UPGRADE_SUMMARY = ROOT / "audit_probe_upgrade_queue_20260526_131117_summary.json"
UPGRADE_BDC_LAUNCH = ROOT / "bdc_queue_20260526_131207_launch_summary.json"
EXTRA_UPGRADE_RESULTS = ROOT / "audit_probe_upgrade_queue_20260526_140600_results.jsonl"
EXTRA_UPGRADE_LAUNCH = ROOT / "audit_probe_upgrade_queue_20260526_140600_launch_summary.json"
EXTRA_BDC_LAUNCH = ROOT / "bdc_queue_20260526_140640_launch_summary.json"
READINESS = ROOT / "external_model_baseline_readiness_20260526.json"
OUT_DIR = ROOT / "main_results_20260526"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def md_table(rows: list[dict], fields: list[str], headers: list[str] | None = None) -> str:
    if headers is None:
        headers = fields
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        values = []
        for field in fields:
            value = row.get(field, "")
            if isinstance(value, float):
                value = "%.3f" % value
            values.append(str(value).replace("|", "\\|"))
        out.append("| " + " | ".join(values) + " |")
    return "\n".join(out) + "\n"


def parse_json_prefix(value: str) -> dict:
    start = value.find("{")
    if start < 0:
        return {}
    decoder = json.JSONDecoder()
    parsed, _ = decoder.raw_decode(value[start:])
    return parsed


def rank(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        avg = (index + 1 + end) / 2.0
        for original_index, _ in ordered[index:end]:
            ranks[original_index] = avg
        index = end
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    x_dev = [x - x_mean for x in xs]
    y_dev = [y - y_mean for y in ys]
    denom = math.sqrt(sum(x * x for x in x_dev) * sum(y * y for y in y_dev))
    if denom == 0:
        return None
    return sum(x * y for x, y in zip(x_dev, y_dev)) / denom


def spearman(xs: list[float], ys: list[float]) -> float | None:
    return pearson(rank(xs), rank(ys))


def average_precision(rows: list[dict], score_field: str) -> float:
    sorted_rows = sorted(rows, key=lambda row: (row.get(score_field) or 0.0, row.get("task_id", "")), reverse=True)
    positives = sum(1 for row in sorted_rows if row.get("false_acceptance_label"))
    if positives == 0:
        return 0.0
    hits = 0
    precision_sum = 0.0
    for index, row in enumerate(sorted_rows, 1):
        if row.get("false_acceptance_label"):
            hits += 1
            precision_sum += hits / float(index)
    return precision_sum / float(positives)


def precision_at(rows: list[dict], score_field: str, k: int) -> dict:
    sorted_rows = sorted(rows, key=lambda row: (row.get(score_field) or 0.0, row.get("task_id", "")), reverse=True)
    top = sorted_rows[:k]
    positives = sum(1 for row in rows if row.get("false_acceptance_label"))
    hits = sum(1 for row in top if row.get("false_acceptance_label"))
    return {
        "score": score_field,
        "k": k,
        "reviewed": len(top),
        "false_acceptances_found": hits,
        "precision_at_k": hits / float(len(top)) if top else 0.0,
        "recall_at_k": hits / float(positives) if positives else 0.0,
    }


def abstain_row(rows: list[dict], rule: str, selected: set[str]) -> dict:
    total = len(rows)
    false_total = sum(1 for row in rows if row.get("false_acceptance_label"))
    abstained = [row for row in rows if row["task_id"] in selected]
    accepted = [row for row in rows if row["task_id"] not in selected]
    captured = sum(1 for row in abstained if row.get("false_acceptance_label"))
    residual = sum(1 for row in accepted if row.get("false_acceptance_label"))
    return {
        "rule": rule,
        "total_tasks": total,
        "abstain_count": len(abstained),
        "accept_count": len(accepted),
        "abstain_rate": len(abstained) / float(total) if total else 0.0,
        "false_acceptances_captured": captured,
        "false_acceptance_capture_rate": captured / float(false_total) if false_total else 0.0,
        "residual_false_acceptances": residual,
        "residual_false_acceptance_rate": residual / float(len(accepted)) if accepted else 0.0,
    }


def build_table1(frozen: list[dict], heldout: list[dict]) -> list[dict]:
    frozen_by_task = {row["task_id"]: row for row in frozen}
    rows = []
    for row in sorted(heldout, key=lambda item: item.get("freeze_id", 9999)):
        frozen_row = frozen_by_task.get(row["task_id"], {})
        rows.append(
            {
                "freeze_id": row.get("freeze_id"),
                "task_id": row.get("task_id"),
                "repo": row.get("repo"),
                "calibration_source": row.get("calibration_source"),
                "manual_audit_status": row.get("manual_audit_status"),
                "original_probe_layer": frozen_row.get("original_probe_layer"),
                "original_cc_ogb_lower_bound": row.get("original_cc_ogb_lower_bound"),
                "specification_debt_signal": bool(row.get("specification_debt_signal")),
                "heldout_status": row.get("heldout_status"),
                "heldout_f2p_pass": row.get("heldout_f2p_pass"),
                "false_acceptance_label": bool(row.get("false_acceptance_label")),
                "fail_to_pass_count": row.get("fail_to_pass_count"),
                "pass_to_pass_count": row.get("pass_to_pass_count"),
                "upgrade_bdc_available": bool(row.get("upgrade_bdc_available")),
                "specification_debt_reasons": row.get("specification_debt_reasons"),
                "issue_signal_score": frozen_row.get("issue_signal_score"),
                "probe_validity_score": frozen_row.get("probe_validity_score"),
            }
        )
    return rows


def build_table2(upgrade_results: list[dict], bdc_summary: dict) -> list[dict]:
    by_task: dict[str, list[dict]] = defaultdict(list)
    for row in upgrade_results:
        by_task[row["task_id"]].append(row)
    bdc_by_task = {row.get("task_id"): row for row in bdc_summary.get("certificates", [])}
    out = []
    for task_id in sorted(by_task):
        rows = by_task[task_id]
        outcomes = defaultdict(int)
        layers = defaultdict(int)
        for row in rows:
            outcomes[row.get("outcome") or "unknown"] += 1
            layers[row.get("probe_layer") or "unknown"] += 1
        cert = bdc_by_task.get(task_id, {})
        candidate_count = cert.get("candidate_count") or len(rows)
        pass_count = cert.get("pass_count") or outcomes.get("pass", 0)
        fail_count = cert.get("fail_count") or outcomes.get("fail", 0)
        lower_bound = min(pass_count, fail_count) / float(candidate_count) if cert else 0.0
        out.append(
            {
                "task_id": task_id,
                "repo": rows[0].get("repo"),
                "probe_id": rows[0].get("probe_id"),
                "probe_layer": ",".join(sorted(layers)),
                "probe_executions": len(rows),
                "pass_count": outcomes.get("pass", 0),
                "fail_count": outcomes.get("fail", 0),
                "timeout_count": outcomes.get("timeout", 0),
                "upgrade_bdc_available": bool(cert),
                "upgrade_behavior_group_count": cert.get("behavior_group_count", 0),
                "upgrade_cc_ogb_lower_bound": lower_bound,
                "certificate_id": cert.get("certificate_id", ""),
            }
        )
    return out


def pass_fail_bdc_count(rows: list[dict]) -> int:
    return sum(1 for row in rows if row.get("upgrade_bdc_available") and row.get("pass_count", 0) > 0 and row.get("fail_count", 0) > 0)


def build_correlation_and_rerank(rows: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    for row in rows:
        cc = row.get("original_cc_ogb_lower_bound") or 0.0
        debt = 1.0 if row.get("specification_debt_signal") else 0.0
        issue = (row.get("issue_signal_score") or 0) / 5.0
        validity = (row.get("probe_validity_score") or 0) / 5.0
        row["risk_cc_only"] = cc
        row["risk_cc_plus_debt"] = cc + 0.25 * debt
        row["risk_audit_weighted"] = cc + 0.25 * debt + 0.05 * issue + 0.05 * validity

    labels = [1.0 if row.get("false_acceptance_label") else 0.0 for row in rows]
    metrics = []
    for field in ["original_cc_ogb_lower_bound", "risk_cc_plus_debt", "risk_audit_weighted"]:
        values = [float(row.get(field) or 0.0) for row in rows]
        metrics.append(
            {
                "signal": field,
                "pearson_with_false_acceptance": pearson(values, labels),
                "spearman_with_false_acceptance": spearman(values, labels),
                "average_precision": average_precision(rows, field),
            }
        )
    debt_values = [1.0 if row.get("specification_debt_signal") else 0.0 for row in rows]
    metrics.append(
        {
            "signal": "specification_debt_signal",
            "pearson_with_false_acceptance": pearson(debt_values, labels),
            "spearman_with_false_acceptance": spearman(debt_values, labels),
            "average_precision": average_precision(rows, "risk_cc_plus_debt"),
        }
    )

    rerank = []
    for score in ["risk_cc_only", "risk_cc_plus_debt", "risk_audit_weighted"]:
        for k in [5, 10, 15, 20]:
            rerank.append(precision_at(rows, score, k))

    abstain = []
    for threshold in sorted(set(row.get("original_cc_ogb_lower_bound") or 0.0 for row in rows)):
        selected = {row["task_id"] for row in rows if (row.get("original_cc_ogb_lower_bound") or 0.0) >= threshold}
        abstain.append(abstain_row(rows, "cc_ogb>=%.2f" % threshold, selected))
    debt_selected = {row["task_id"] for row in rows if row.get("specification_debt_signal")}
    abstain.append(abstain_row(rows, "specification_debt_signal", debt_selected))
    combined_selected = {
        row["task_id"]
        for row in rows
        if row.get("specification_debt_signal") or (row.get("original_cc_ogb_lower_bound") or 0.0) >= 0.25
    }
    abstain.append(abstain_row(rows, "spec_debt_or_cc_ogb>=0.25", combined_selected))
    return metrics, rerank, abstain


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frozen = read_json(FROZEN_INDEX)
    heldout = read_jsonl(HELDOUT_RESULTS)
    upgrade_results = read_jsonl(UPGRADE_RESULTS)
    upgrade_summary = read_json(UPGRADE_SUMMARY)
    bdc_launch = read_json(UPGRADE_BDC_LAUNCH)
    bdc_summary = parse_json_prefix(bdc_launch.get("stdout", ""))
    extra_upgrade_results = read_jsonl(EXTRA_UPGRADE_RESULTS) if EXTRA_UPGRADE_RESULTS.exists() else []
    extra_upgrade_launch = read_json(EXTRA_UPGRADE_LAUNCH) if EXTRA_UPGRADE_LAUNCH.exists() else {}
    extra_bdc_launch = read_json(EXTRA_BDC_LAUNCH) if EXTRA_BDC_LAUNCH.exists() else {}
    extra_bdc_summary = parse_json_prefix(extra_bdc_launch.get("stdout", "")) if extra_bdc_launch else {}
    readiness = read_json(READINESS) if READINESS.exists() else {}

    table1 = build_table1(frozen, heldout)
    table2 = build_table2(upgrade_results, bdc_summary)
    table6 = build_table2(extra_upgrade_results, extra_bdc_summary) if extra_upgrade_results else []
    metrics, rerank, abstain = build_correlation_and_rerank(table1)

    summary = {
        "created_at": utc_now(),
        "gold_boundary": "held-out labels were read only after frozen_certificate_index_20260526.json was written",
        "heldout_queue": "heldout_calibration_queue_20260526_124819",
        "heldout_records": len(table1),
        "heldout_executable": sum(1 for row in table1 if row.get("heldout_status") == "executed"),
        "false_acceptance_true": sum(1 for row in table1 if row.get("false_acceptance_label")),
        "false_acceptance_false": sum(1 for row in table1 if not row.get("false_acceptance_label")),
        "specification_debt_signal": sum(1 for row in table1 if row.get("specification_debt_signal")),
        "upgrade_probe_queue": upgrade_summary.get("queue_id"),
        "upgrade_probe_target_count": upgrade_summary.get("target_count"),
        "upgrade_probe_execution_count": upgrade_summary.get("probe_result_count"),
        "upgrade_probe_layer_counts": upgrade_summary.get("probe_layers"),
        "upgrade_bdc_queue": bdc_summary.get("queue_id"),
        "upgrade_bdc_task_count": bdc_summary.get("certificate_task_count"),
        "upgrade_bdc_pass_fail_task_count": pass_fail_bdc_count(table2),
        "extra_full_package_probe_queue": (extra_upgrade_launch.get("summary") or {}).get("queue_id"),
        "extra_full_package_probe_target_count": (extra_upgrade_launch.get("summary") or {}).get("target_count"),
        "extra_full_package_probe_execution_count": (extra_upgrade_launch.get("summary") or {}).get("probe_result_count"),
        "extra_full_package_bdc_queue": extra_bdc_summary.get("queue_id"),
        "extra_full_package_bdc_task_count": extra_bdc_summary.get("certificate_task_count"),
        "extra_full_package_bdc_pass_fail_task_count": pass_fail_bdc_count(table6),
        "external_model_baseline_classification": readiness.get("classification", "unknown"),
        "external_model_baseline_ready": bool(readiness.get("independent_external_baseline_ready")),
    }

    table1_fields = [
        "freeze_id",
        "task_id",
        "repo",
        "calibration_source",
        "manual_audit_status",
        "original_probe_layer",
        "original_cc_ogb_lower_bound",
        "specification_debt_signal",
        "heldout_status",
        "heldout_f2p_pass",
        "false_acceptance_label",
        "fail_to_pass_count",
        "pass_to_pass_count",
        "upgrade_bdc_available",
        "specification_debt_reasons",
    ]
    table2_fields = [
        "task_id",
        "repo",
        "probe_id",
        "probe_layer",
        "probe_executions",
        "pass_count",
        "fail_count",
        "timeout_count",
        "upgrade_bdc_available",
        "upgrade_behavior_group_count",
        "upgrade_cc_ogb_lower_bound",
        "certificate_id",
    ]
    metrics_fields = ["signal", "pearson_with_false_acceptance", "spearman_with_false_acceptance", "average_precision"]
    rerank_fields = ["score", "k", "reviewed", "false_acceptances_found", "precision_at_k", "recall_at_k"]
    abstain_fields = [
        "rule",
        "total_tasks",
        "abstain_count",
        "accept_count",
        "abstain_rate",
        "false_acceptances_captured",
        "false_acceptance_capture_rate",
        "residual_false_acceptances",
        "residual_false_acceptance_rate",
    ]

    write_json(OUT_DIR / "main_results_summary_20260526.json", summary)
    write_json(OUT_DIR / "table1_heldout_false_acceptance_20260526.json", table1)
    write_json(OUT_DIR / "table2_upgraded_probe_20260526.json", table2)
    write_json(OUT_DIR / "table6_extra_full_package_probe_20260526.json", table6)
    write_json(OUT_DIR / "table3_correlation_20260526.json", metrics)
    write_json(OUT_DIR / "table4_rerank_20260526.json", rerank)
    write_json(OUT_DIR / "table5_abstain_20260526.json", abstain)
    write_csv(OUT_DIR / "table1_heldout_false_acceptance_20260526.csv", table1, table1_fields)
    write_csv(OUT_DIR / "table2_upgraded_probe_20260526.csv", table2, table2_fields)
    write_csv(OUT_DIR / "table6_extra_full_package_probe_20260526.csv", table6, table2_fields)
    write_csv(OUT_DIR / "table3_correlation_20260526.csv", metrics, metrics_fields)
    write_csv(OUT_DIR / "table4_rerank_20260526.csv", rerank, rerank_fields)
    write_csv(OUT_DIR / "table5_abstain_20260526.csv", abstain, abstain_fields)

    report = [
        "# PatchCourt Main Results 2026-05-26",
        "",
        "## Summary",
        "",
        md_table([summary], list(summary.keys())),
        "## Table 1: Held-Out False Acceptance",
        "",
        md_table(table1, table1_fields),
        "## Table 2: Upgraded Full-Package / Issue-Code Probes",
        "",
        md_table(table2, table2_fields),
        "## Table 6: Extra Full-Package Probe Layer",
        "",
        md_table(table6, table2_fields),
        "## Table 3: Correlation Signals",
        "",
        md_table(metrics, metrics_fields),
        "## Table 4: Rerank Triage",
        "",
        md_table(rerank, rerank_fields),
        "## Table 5: Abstain Triage",
        "",
        md_table(abstain, abstain_fields),
        "## Reading Notes",
        "",
        "- `llm_batch_direct` remains classified by the readiness gate; it is not treated as an independent external model baseline unless the readiness report says so.",
        "- Table 2 separates probe execution success from BDC formation; the current upgraded layer executes 10 targets and yields stable BDCs for 6 tasks.",
        "- Table 6 is an append-only extra full-package layer; pass/fail BDCs are stronger than all-fail behavioral splits.",
        "- Correlation and rerank rows are preliminary risk-signal analyses over the frozen 30-task audit set.",
        "",
    ]
    (OUT_DIR / "main_results_report_20260526.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
