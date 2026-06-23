from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "main_results_20260526"
OUT_DIR = Path("paper/icse2027/assets_20260528")

TABLE1 = RESULTS / "table1_heldout_false_acceptance_20260526.csv"
TABLE2 = RESULTS / "table2_upgraded_probe_20260526.csv"
TABLE6 = RESULTS / "table6_extra_full_package_probe_20260526.csv"


QWEN_ISSUE_SPECIFIC = {"mwaskom__seaborn-3407"}
QWEN_PACKAGE_INTEGRITY = {
    "mwaskom__seaborn-3190",
    "mwaskom__seaborn-3407",
    "pallets__flask-5063",
    "scikit-learn__scikit-learn-10508",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bool_value(value: str) -> bool:
    return str(value).strip().lower() == "true"


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def group_rate(rows: list[dict[str, str]], key: str) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row.get(key, "")].append(row)
    output = []
    for value, subset in sorted(groups.items(), key=lambda item: item[0]):
        false_count = sum(1 for row in subset if bool_value(row["false_acceptance_label"]))
        total = len(subset)
        output.append(
            {
                key: value,
                "tasks": total,
                "false_acceptance": false_count,
                "false_acceptance_rate": round(false_count / total, 3) if total else 0.0,
            }
        )
    return output


def cc_bin(value: str) -> str:
    try:
        parsed = float(value)
    except ValueError:
        return "unknown"
    return f"{parsed:.2f}"


def upgraded_status(main_rows: list[dict[str, str]], extra_rows: list[dict[str, str]]) -> dict[str, str]:
    status: dict[str, str] = {}
    for layer, rows in [("main", main_rows), ("extra", extra_rows)]:
        for row in rows:
            task = row["task_id"]
            has_bdc = bool_value(row["upgrade_bdc_available"])
            passes = int(row["pass_count"])
            fails = int(row["fail_count"])
            if has_bdc and passes > 0 and fails > 0:
                label = f"{layer}_pass_fail"
            elif has_bdc:
                label = f"{layer}_all_fail_divergence"
            else:
                label = f"{layer}_no_bdc"
            previous = status.get(task)
            if previous is None:
                status[task] = label
            elif "pass_fail" not in previous and "pass_fail" in label:
                status[task] = label
    return status


def add_derived_fields(rows: list[dict[str, str]], upgrade_status: dict[str, str]) -> None:
    for row in rows:
        task = row["task_id"]
        row["cc_ogb_bin"] = cc_bin(row["original_cc_ogb_lower_bound"])
        row["safe_route_probe_status"] = upgrade_status.get(task, "not_upgraded")
        row["safe_route_qwen_status"] = (
            "qwen_issue_specific"
            if task in QWEN_ISSUE_SPECIFIC
            else "qwen_package_integrity"
            if task in QWEN_PACKAGE_INTEGRITY
            else "not_qwen_positive"
        )


def case_priority(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for row in rows:
        task = row["task_id"]
        false_acceptance = bool_value(row["false_acceptance_label"])
        retained = row["manual_audit_status"] == "retain"
        probe_status = row["safe_route_probe_status"]
        qwen_status = row["safe_route_qwen_status"]
        score = 0
        score += 5 if false_acceptance else 0
        score += 3 if "pass_fail" in probe_status else 0
        score += 2 if retained else 0
        score += 2 if qwen_status == "qwen_issue_specific" else 0
        score += 1 if qwen_status == "qwen_package_integrity" else 0
        output.append(
            {
                "task_id": task,
                "repo": row["repo"],
                "score": score,
                "false_acceptance": false_acceptance,
                "manual_audit_status": row["manual_audit_status"],
                "probe_status": probe_status,
                "qwen_status": qwen_status,
                "reason": ";".join(
                    part
                    for part in [
                        "heldout_false_acceptance" if false_acceptance else "",
                        "stronger_probe_pass_fail" if "pass_fail" in probe_status else "",
                        "retained_audit" if retained else "",
                        qwen_status if qwen_status != "not_qwen_positive" else "",
                    ]
                    if part
                ),
            }
        )
    return sorted(output, key=lambda row: (-int(row["score"]), str(row["task_id"])))


def md_table(rows: list[dict[str, object]], fields: list[str]) -> str:
    lines = [
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    heldout = read_csv(TABLE1)
    main_upgrades = read_csv(TABLE2)
    extra_upgrades = read_csv(TABLE6)
    add_derived_fields(heldout, upgraded_status(main_upgrades, extra_upgrades))

    summaries = {
        "by_manual_audit_status": group_rate(heldout, "manual_audit_status"),
        "by_calibration_source": group_rate(heldout, "calibration_source"),
        "by_original_probe_layer": group_rate(heldout, "original_probe_layer"),
        "by_specification_debt_signal": group_rate(heldout, "specification_debt_signal"),
        "by_cc_ogb_bin": group_rate(heldout, "cc_ogb_bin"),
        "by_safe_route_probe_status": group_rate(heldout, "safe_route_probe_status"),
        "by_safe_route_qwen_status": group_rate(heldout, "safe_route_qwen_status"),
    }
    cases = case_priority(heldout)

    for name, rows in summaries.items():
        field = next(iter(rows[0].keys())) if rows else "group"
        write_csv(
            OUT_DIR / f"safe_route_{name}_20260528.csv",
            rows,
            [field, "tasks", "false_acceptance", "false_acceptance_rate"],
        )
    write_csv(
        OUT_DIR / "safe_route_case_priority_20260528.csv",
        cases,
        [
            "task_id",
            "repo",
            "score",
            "false_acceptance",
            "manual_audit_status",
            "probe_status",
            "qwen_status",
            "reason",
        ],
    )

    summary = {
        "created_at": "2026-05-28",
        "route": "safe_empirical_false_acceptance_characterization",
        "title": "Visible Tests Are Not Oracles: Characterizing False Acceptance in LLM-Based Repository Repair",
        "heldout_tasks": len(heldout),
        "heldout_false_acceptance": sum(1 for row in heldout if bool_value(row["false_acceptance_label"])),
        "summaries": summaries,
        "top_cases": cases[:8],
    }
    (OUT_DIR / "safe_route_characterization_20260528.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    report = [
        "# Safe-Route Characterization 2026-05-28",
        "",
        "This report locks the lower-risk ICSE route: characterize visible-test false acceptance and present PatchCourt as an auditable triage protocol, not as a correctness oracle or a broad independent-model reproduction claim.",
        "",
        "## Locked Title",
        "",
        "`Visible Tests Are Not Oracles: Characterizing False Acceptance in LLM-Based Repository Repair`",
        "",
        "## Core Claim",
        "",
        "Visible/probe acceptance leaves substantial residual held-out risk in LLM repository repair. PatchCourt provides a gold-boundary-aware evidence ledger and risk-triage protocol that exposes this risk before held-out labels are read.",
        "",
        "## Main Characterization Tables",
        "",
        "### By Manual Audit Status",
        "",
        md_table(summaries["by_manual_audit_status"], ["manual_audit_status", "tasks", "false_acceptance", "false_acceptance_rate"]),
        "",
        "### By Candidate Source",
        "",
        md_table(summaries["by_calibration_source"], ["calibration_source", "tasks", "false_acceptance", "false_acceptance_rate"]),
        "",
        "### By Original Probe Layer",
        "",
        md_table(summaries["by_original_probe_layer"], ["original_probe_layer", "tasks", "false_acceptance", "false_acceptance_rate"]),
        "",
        "### By Specification Debt",
        "",
        md_table(summaries["by_specification_debt_signal"], ["specification_debt_signal", "tasks", "false_acceptance", "false_acceptance_rate"]),
        "",
        "### By Stronger Probe Overlay",
        "",
        md_table(summaries["by_safe_route_probe_status"], ["safe_route_probe_status", "tasks", "false_acceptance", "false_acceptance_rate"]),
        "",
        "### By Qwen Status",
        "",
        md_table(summaries["by_safe_route_qwen_status"], ["safe_route_qwen_status", "tasks", "false_acceptance", "false_acceptance_rate"]),
        "",
        "## Top Case Study Candidates",
        "",
        md_table(cases[:10], ["task_id", "score", "false_acceptance", "probe_status", "qwen_status", "reason"]),
        "",
        "## Paper Consequences",
        "",
        "- Put the 17/30 held-out false-acceptance result in the abstract and first results table.",
        "- Treat full-package/issue-code BDCs as validation that the signal is not only a source-isolated artifact.",
        "- Treat Qwen as a stress-test and boundary result: one issue-specific BDC plus four package-integrity BDCs.",
        "- Move any claim about broad independent-source reproduction out of the main thesis.",
        "- Use rerank/abstain as a practical triage demonstration, not as a calibrated predictor claim.",
        "",
        "## Next Work Under This Route",
        "",
        "1. Page-budget the double-blind draft around RQ1-RQ3 as the main spine.",
        "2. Add related work around plausible patches, SWE-bench false acceptance, generated tests, and oracle problem work.",
        "3. Build an anonymous inspect-only artifact bundle.",
        "4. Only after the main empirical story is stable, optionally add a second independent model source or more Qwen issue-specific BDCs.",
        "",
    ]
    (OUT_DIR / "safe_route_characterization_20260528.md").write_text(
        "\n".join(report),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
