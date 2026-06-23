#!/usr/bin/env python3
"""Regenerate and verify Level-1 PatchCourt table claims from the anonymous bundle.

This script intentionally uses only packaged CSV/JSONL/Markdown files.  It does
not require model access, repository worktrees, held-out labels outside the
bundle, or machine-specific paths.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ARTIFACT_ROOT = Path(__file__).resolve().parents[1]
TABLES = ARTIFACT_ROOT / "tables"
CERTIFICATES = ARTIFACT_ROOT / "certificates"
DOCS = ARTIFACT_ROOT / "docs"
GENERATED = ARTIFACT_ROOT / "generated"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return path.relative_to(ARTIFACT_ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def as_int(value: Any) -> int:
    if value in (None, ""):
        return 0
    return int(float(value))


def as_float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def pass_fail_bdc(rows: list[dict[str, Any]]) -> int:
    return sum(
        1
        for row in rows
        if as_bool(row.get("upgrade_bdc_available"))
        and as_int(row.get("pass_count")) > 0
        and as_int(row.get("fail_count")) > 0
    )


def certificate_pass_fail(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if as_int(row.get("pass_count")) > 0 and as_int(row.get("fail_count")) > 0)


def find_rerank(rows: list[dict[str, str]], score: str, k: int) -> dict[str, str]:
    for row in rows:
        if row.get("score") == score and as_int(row.get("k")) == k:
            return row
    raise KeyError(f"missing rerank row: {score} @ {k}")


def find_abstain(rows: list[dict[str, str]], rule: str) -> dict[str, str]:
    for row in rows:
        if row.get("rule") == rule:
            return row
    raise KeyError(f"missing abstain row: {rule}")


def find_stage(rows: list[dict[str, str]], stage: str) -> dict[str, str]:
    for row in rows:
        if row.get("stage") == stage:
            return row
    raise KeyError(f"missing selection-funnel row: {stage}")


def find_route(rows: list[dict[str, str]], layer: str) -> dict[str, str]:
    for row in rows:
        if row.get("layer") == layer:
            return row
    raise KeyError(f"missing route-stability row: {layer}")


def collect_metrics() -> tuple[dict[str, Any], list[Path]]:
    table1_path = TABLES / "table1_heldout_false_acceptance_20260526.csv"
    table2_path = TABLES / "table2_upgraded_probe_20260526.csv"
    table3_path = TABLES / "table3_correlation_20260526.csv"
    table4_path = TABLES / "table4_rerank_20260526.csv"
    table5_path = TABLES / "table5_abstain_20260526.csv"
    table6_path = TABLES / "table6_extra_full_package_probe_20260526.csv"
    pilot50_path = TABLES / "pilot50_drop_reasons_20260529.csv"
    selection_funnel_path = TABLES / "selection_funnel_20260529.csv"
    route_stability_path = TABLES / "route_stability_20260529.csv"
    qwen_issue_path = CERTIFICATES / "bdc_queue_20260527_155027_certificates.jsonl"
    qwen_integrity_path = CERTIFICATES / "bdc_queue_20260527_155342_certificates.jsonl"
    qwen_rescue_path = CERTIFICATES / "bdc_queue_20260527_184051_certificates.jsonl"
    qwen_audit_path = TABLES / "qwen_bdc_audit_20260528.md"

    table1 = read_csv(table1_path)
    table2 = read_csv(table2_path)
    table3 = read_csv(table3_path)
    table4 = read_csv(table4_path)
    table5 = read_csv(table5_path)
    table6 = read_csv(table6_path)
    pilot50 = read_csv(pilot50_path)
    selection_funnel = read_csv(selection_funnel_path)
    route_stability = read_csv(route_stability_path)
    qwen_issue = read_jsonl(qwen_issue_path)
    qwen_integrity = read_jsonl(qwen_integrity_path)
    qwen_rescue = read_jsonl(qwen_rescue_path)

    cc_only_k10 = find_rerank(table4, "risk_cc_only", 10)
    cc_only_k20 = find_rerank(table4, "risk_cc_only", 20)
    audit_k10 = find_rerank(table4, "risk_audit_weighted", 10)
    audit_k20 = find_rerank(table4, "risk_audit_weighted", 20)
    debt_abstain = find_abstain(table5, "specification_debt_signal")
    pilot_stage = find_stage(selection_funnel, "Pilot task substrate used for discovery")
    raw_cert_stage = find_stage(selection_funnel, "Raw certificate records consumed by audit index")
    frozen_stage = find_stage(selection_funnel, "Conservative pass/fail task records frozen")
    layer_stage = find_stage(selection_funnel, "Frozen original layers: source/custom/issue-code")
    source_stage = find_stage(selection_funnel, "Frozen candidate-source split: direct-batch/Codex")
    heldout_route = find_route(route_stability, "Held-out FAIL_TO_PASS")
    upgrade_route = find_route(route_stability, "Main probe upgrades")
    frozen_route = find_route(route_stability, "Frozen audit index")

    metrics: dict[str, Any] = {
        "heldout_records": len(table1),
        "heldout_executable": sum(1 for row in table1 if row.get("heldout_status") == "executed"),
        "false_acceptance_true": sum(1 for row in table1 if as_bool(row.get("false_acceptance_label"))),
        "specification_debt_true": sum(1 for row in table1 if as_bool(row.get("specification_debt_signal"))),
        "frozen_source_isolated_original_layer": sum(
            1 for row in table1 if row.get("original_probe_layer") == "source_isolated_template"
        ),
        "frozen_custom_active_original_layer": sum(
            1 for row in table1 if row.get("original_probe_layer") == "custom_active_probe"
        ),
        "frozen_issue_code_original_layer": sum(
            1 for row in table1 if row.get("original_probe_layer") == "issue_codeblock_full_package"
        ),
        "frozen_direct_batch_source": sum(1 for row in table1 if row.get("calibration_source") == "llm_batch_direct"),
        "frozen_codex_source": sum(1 for row in table1 if row.get("calibration_source") == "codex_session_bootstrap"),
        "manual_audit_retain": sum(1 for row in table1 if row.get("manual_audit_status") == "retain"),
        "manual_audit_downgrade": sum(1 for row in table1 if row.get("manual_audit_status") == "downgrade"),
        "manual_audit_reject": sum(1 for row in table1 if row.get("manual_audit_status") == "reject"),
        "main_upgrade_targets": len(table2),
        "main_upgrade_bdc_tasks": sum(1 for row in table2 if as_bool(row.get("upgrade_bdc_available"))),
        "main_upgrade_pass_fail_bdc_tasks": pass_fail_bdc(table2),
        "extra_full_package_targets": len(table6),
        "extra_full_package_bdc_tasks": sum(1 for row in table6 if as_bool(row.get("upgrade_bdc_available"))),
        "extra_full_package_pass_fail_bdc_tasks": pass_fail_bdc(table6),
        "qwen_issue_full_package_bdc_tasks": len(qwen_issue),
        "qwen_issue_full_package_pass_fail_tasks": certificate_pass_fail(qwen_issue),
        "qwen_package_integrity_pass_fail_tasks": certificate_pass_fail(qwen_integrity),
        "qwen_rescue_pass_fail_tasks": certificate_pass_fail(qwen_rescue),
        "rerank_cc_only_precision_at_10": as_float(cc_only_k10["precision_at_k"]),
        "rerank_cc_only_precision_at_20": as_float(cc_only_k20["precision_at_k"]),
        "rerank_audit_weighted_precision_at_10": as_float(audit_k10["precision_at_k"]),
        "rerank_audit_weighted_precision_at_20": as_float(audit_k20["precision_at_k"]),
        "abstain_spec_debt_capture_rate": as_float(debt_abstain["false_acceptance_capture_rate"]),
        "abstain_spec_debt_residual_false_acceptances": as_int(debt_abstain["residual_false_acceptances"]),
        "correlation_rows": len(table3),
        "pilot50_rows": len(pilot50),
        "pilot50_snapshot_built": sum(1 for row in pilot50 if row.get("snapshot_built") == "true"),
        "pilot50_candidate_slots_total": sum(as_int(row.get("candidate_slots")) for row in pilot50),
        "pilot50_frozen_conservative": sum(
            1 for row in pilot50 if row.get("paper_funnel_status") == "frozen_conservative_certificate"
        ),
        "pilot50_broad_not_frozen": sum(
            1 for row in pilot50 if row.get("paper_funnel_status") == "broad_certificate_not_frozen"
        ),
        "pilot50_no_conservative_certificate": sum(
            1
            for row in pilot50
            if row.get("paper_funnel_status") == "no_conservative_certificate_in_final_audit_index"
        ),
        "selection_funnel_pilot_tasks": pilot_stage["count"],
        "selection_funnel_raw_certificates": raw_cert_stage["count"],
        "selection_funnel_frozen_certificates": frozen_stage["count"],
        "selection_funnel_original_layers": layer_stage["count"],
        "selection_funnel_candidate_sources": source_stage["count"],
        "route_heldout_before_after": f"{heldout_route['before']} -> {heldout_route['after']}",
        "route_upgrade_before_after": f"{upgrade_route['before']} -> {upgrade_route['after']}",
        "route_frozen_index_before_after": f"{frozen_route['before']} -> {frozen_route['after']}",
        "qwen_audit_mentions_final_issue_count": "Final Qwen issue-specific pass/fail BDC tasks after rescue | 1"
        in qwen_audit_path.read_text(encoding="utf-8-sig"),
    }
    inputs = [
        table1_path,
        table2_path,
        table3_path,
        table4_path,
        table5_path,
        table6_path,
        pilot50_path,
        selection_funnel_path,
        route_stability_path,
        qwen_issue_path,
        qwen_integrity_path,
        qwen_rescue_path,
        qwen_audit_path,
    ]
    return metrics, inputs


EXPECTED: dict[str, Any] = {
    "heldout_records": 30,
    "heldout_executable": 30,
    "false_acceptance_true": 17,
    "specification_debt_true": 26,
    "frozen_source_isolated_original_layer": 26,
    "frozen_custom_active_original_layer": 3,
    "frozen_issue_code_original_layer": 1,
    "frozen_direct_batch_source": 23,
    "frozen_codex_source": 7,
    "manual_audit_retain": 22,
    "manual_audit_downgrade": 8,
    "manual_audit_reject": 0,
    "main_upgrade_targets": 10,
    "main_upgrade_bdc_tasks": 6,
    "main_upgrade_pass_fail_bdc_tasks": 6,
    "extra_full_package_targets": 10,
    "extra_full_package_bdc_tasks": 7,
    "extra_full_package_pass_fail_bdc_tasks": 6,
    "qwen_issue_full_package_bdc_tasks": 5,
    "qwen_issue_full_package_pass_fail_tasks": 1,
    "qwen_package_integrity_pass_fail_tasks": 4,
    "qwen_rescue_pass_fail_tasks": 0,
    "rerank_cc_only_precision_at_10": 0.4,
    "rerank_cc_only_precision_at_20": 0.55,
    "rerank_audit_weighted_precision_at_10": 0.6,
    "rerank_audit_weighted_precision_at_20": 0.65,
    "abstain_spec_debt_capture_rate": 1.0,
    "abstain_spec_debt_residual_false_acceptances": 0,
    "correlation_rows": 4,
    "pilot50_rows": 50,
    "pilot50_snapshot_built": 50,
    "pilot50_candidate_slots_total": 200,
    "pilot50_frozen_conservative": 27,
    "pilot50_broad_not_frozen": 1,
    "pilot50_no_conservative_certificate": 22,
    "selection_funnel_pilot_tasks": "50",
    "selection_funnel_raw_certificates": "37",
    "selection_funnel_frozen_certificates": "30",
    "selection_funnel_original_layers": "26 / 3 / 1",
    "selection_funnel_candidate_sources": "23 / 7",
    "route_heldout_before_after": "15/30 executable -> 30/30 executable",
    "route_upgrade_before_after": "2/10 upgraded BDC targets -> 6/10 pass/fail BDC targets",
    "route_frozen_index_before_after": "30 conservative records -> 30 conservative records",
    "qwen_audit_mentions_final_issue_count": True,
}


def close_enough(observed: Any, expected: Any) -> bool:
    if isinstance(expected, float):
        return abs(float(observed) - expected) < 1e-9
    return observed == expected


def md_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    out = ["| " + " | ".join(fields) + " |", "| " + " | ".join(["---"] * len(fields)) + " |"]
    for row in rows:
        values = [str(row.get(field, "")).replace("|", "\\|") for field in fields]
        out.append("| " + " | ".join(values) + " |")
    return "\n".join(out)


def main() -> int:
    metrics, inputs = collect_metrics()
    checks = []
    ok = True
    for key, expected in EXPECTED.items():
        observed = metrics.get(key)
        passed = close_enough(observed, expected)
        ok = ok and passed
        checks.append(
            {
                "metric": key,
                "expected": expected,
                "observed": observed,
                "status": "PASS" if passed else "FAIL",
            }
        )

    input_rows = [
        {
            "file": rel(path),
            "sha256": sha256(path)[:16],
            "bytes": path.stat().st_size,
        }
        for path in inputs
    ]

    summary = {
        "created_at": utc_now(),
        "artifact_root": "<ARTIFACT_ROOT>",
        "level": "Level 1 inspect-only table regeneration",
        "overall_status": "PASS" if ok else "FAIL",
        "metrics": metrics,
        "checks": checks,
        "inputs": input_rows,
    }

    GENERATED.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    (GENERATED / "level1_table_recheck_20260528.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report = [
        "# Level 1 Table Regeneration Report 2026-05-29",
        "",
        f"Status: **{summary['overall_status']}**",
        "",
        "This check is run from the anonymous inspect-only artifact. It recomputes the manuscript headline counts, selection-funnel transparency checks, pilot-50 drop-reason counts, and route-stability checks from packaged CSV, JSONL, and Markdown files only. It does not access model endpoints, raw worktrees, private paths, or hidden labels outside the package.",
        "",
        "## Recomputed Checks",
        "",
        md_table(checks, ["metric", "expected", "observed", "status"]),
        "",
        "## Input File Fingerprints",
        "",
        md_table(input_rows, ["file", "sha256", "bytes"]),
        "",
        "## Reviewer Command",
        "",
        "```bash",
        "python scripts/verify_level1_tables_20260528.py",
        "```",
        "",
        "Output files:",
        "",
        "- `docs/LEVEL1_TABLE_REGENERATION_REPORT_20260528.md`",
        "- `generated/level1_table_recheck_20260528.json`",
        "",
    ]
    (DOCS / "LEVEL1_TABLE_REGENERATION_REPORT_20260528.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"overall_status": summary["overall_status"], "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
