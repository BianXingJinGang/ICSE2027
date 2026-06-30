#!/usr/bin/env python3
"""Build PatchCourt evidence ledger and CC-OGB lower-bound records.

This stage is gold-blind. It consumes behavioral disagreement certificates,
candidate apply/visible results, and issue-probe results. It does not read
developer patches or held-out labels.
"""

from __future__ import print_function

import argparse
import collections
import datetime as _dt
import json
import os
import sys


GOLD_FIELDS = set(["patch", "test_patch", "FAIL_TO_PASS", "PASS_TO_PASS"])


def utc_now():
    return _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_no_gold(value, path, location="root"):
    if isinstance(value, dict):
        leaked = sorted(GOLD_FIELDS.intersection(value.keys()))
        if leaked:
            raise RuntimeError("%s:%s contains gold fields: %s" % (path, location, leaked))
        for key, item in value.items():
            ensure_no_gold(item, path, "%s.%s" % (location, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            ensure_no_gold(item, path, "%s[%d]" % (location, index))


def require_gold_false(record, path, line_no):
    if record.get("gold_used") is not False:
        raise RuntimeError("%s:%s must carry gold_used=false" % (path, line_no))


def read_jsonl(path, require_gold=True):
    records = []
    with open(path, "r", encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, 1):
            stripped = line.strip()
            if not stripped:
                continue
            record = json.loads(stripped)
            ensure_no_gold(record, path, "line_%d" % line_no)
            if require_gold:
                require_gold_false(record, path, line_no)
            records.append(record)
    return records


def write_json(path, value):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_jsonl(path, records):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def ratio(numerator, denominator):
    if not denominator:
        return 0.0
    return round(float(numerator) / float(denominator), 6)


def pair_count(size):
    return int(size * (size - 1) / 2)


def flatten_candidates(certificate):
    candidates = []
    for group in certificate.get("groups") or []:
        for candidate in group.get("candidates") or []:
            item = dict(candidate)
            item["behavior_hash"] = group.get("behavior_hash")
            item["behavior_outcome"] = group.get("outcome")
            item["behavior_exit_code"] = group.get("exit_code")
            candidates.append(item)
    return candidates


def indexed(records, key):
    out = {}
    for record in records:
        value = record.get(key)
        if value:
            out[value] = record
    return out


def probe_index(records):
    out = {}
    for record in records:
        key = (record.get("task_id"), record.get("probe_id"), record.get("candidate_id"))
        out[key] = record
    return out


def visible_summary(candidate_id, apply_by_candidate):
    apply_record = apply_by_candidate.get(candidate_id) or {}
    summary = apply_record.get("visible_summary") or {}
    return {
        "apply_status": apply_record.get("apply_status") or "",
        "strict_visible_pass": bool(summary.get("strict_visible_pass")),
        "compatible_visible_pass": bool(summary.get("compatible_visible_pass")),
        "visible_command_count": summary.get("command_count", 0),
        "visible_pass_count": summary.get("pass_count", 0),
        "visible_fail_count": summary.get("fail_count", 0),
        "visible_skipped_count": summary.get("skipped_count", 0),
        "candidate_repo": apply_record.get("candidate_repo") or "",
    }


def group_records(certificate):
    groups = []
    for index, group in enumerate(certificate.get("groups") or []):
        candidate_ids = [candidate.get("candidate_id") for candidate in group.get("candidates") or []]
        sources = sorted(set(candidate.get("candidate_source") for candidate in group.get("candidates") or []))
        groups.append(
            {
                "group_id": "g%02d" % index,
                "behavior_hash": group.get("behavior_hash"),
                "candidate_count": group.get("candidate_count", len(candidate_ids)),
                "candidate_ids": candidate_ids,
                "candidate_sources": sources,
                "model_generated_candidate_count": len(
                    [candidate for candidate in group.get("candidates") or [] if candidate.get("candidate_model_generated")]
                ),
                "heuristic_candidate_count": len(
                    [candidate for candidate in group.get("candidates") or [] if candidate.get("candidate_heuristic")]
                ),
                "outcome": group.get("outcome"),
                "exit_code": group.get("exit_code"),
                "stdout_excerpt": group.get("stdout_excerpt") or "",
                "stderr_excerpt": group.get("stderr_excerpt") or "",
            }
        )
    return groups


def cc_ogb_metrics(certificate):
    groups = certificate.get("groups") or []
    sizes = [int(group.get("candidate_count") or len(group.get("candidates") or [])) for group in groups]
    candidate_count = int(certificate.get("candidate_count") or sum(sizes))
    behavior_group_count = len(groups)
    pair_total = pair_count(candidate_count)
    same_behavior_pairs = sum(pair_count(size) for size in sizes)
    disagreeing_pairs = pair_total - same_behavior_pairs
    majority_size = max(sizes) if sizes else 0
    majority_fraction = ratio(majority_size, candidate_count)
    majority_gap = round(1.0 - majority_fraction, 6) if candidate_count else 0.0
    outcome_counts = collections.Counter(group.get("outcome") for group in groups for _ in range(int(group.get("candidate_count") or 0)))
    pass_count = int(certificate.get("pass_count") or outcome_counts.get("pass", 0))
    fail_count = int(certificate.get("fail_count") or outcome_counts.get("fail", 0))
    timeout_count = int(certificate.get("timeout_count") or outcome_counts.get("timeout", 0))
    pass_fail_split = bool(pass_count > 0 and fail_count > 0)
    pass_fail_minority = min(pass_count, fail_count) if pass_fail_split else 0
    pass_fail_lower_bound = ratio(pass_fail_minority, candidate_count)
    outcome_majority = max(outcome_counts.values()) if outcome_counts else 0
    outcome_gap = round(1.0 - ratio(outcome_majority, candidate_count), 6) if candidate_count else 0.0
    cc_ogb_lower_bound = max(majority_gap, pass_fail_lower_bound)
    return {
        "candidate_count": candidate_count,
        "behavior_group_count": behavior_group_count,
        "behavior_group_sizes": sizes,
        "pair_total": pair_total,
        "same_behavior_pairs": same_behavior_pairs,
        "disagreeing_candidate_pairs": disagreeing_pairs,
        "candidate_pair_disagreement_rate": ratio(disagreeing_pairs, pair_total),
        "majority_behavior_size": majority_size,
        "majority_behavior_fraction": majority_fraction,
        "majority_behavior_gap_lower_bound": majority_gap,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "timeout_count": timeout_count,
        "pass_fail_split": pass_fail_split,
        "pass_fail_minority_fraction": pass_fail_lower_bound,
        "outcome_gap_lower_bound": outcome_gap,
        "cc_ogb_lower_bound": cc_ogb_lower_bound,
        "certifies_visible_non_collapse": behavior_group_count >= 2,
        "certifies_issue_probe_outcome_split": pass_fail_split,
    }


def risk_tier(metrics):
    if metrics.get("pass_fail_split") and metrics.get("cc_ogb_lower_bound", 0.0) >= 0.5:
        return "high"
    if metrics.get("pass_fail_split"):
        return "medium"
    if metrics.get("cc_ogb_lower_bound", 0.0) >= 0.25:
        return "medium"
    return "low"


def task_decision(metrics, pass_behavior_group_count):
    if not metrics.get("certifies_visible_non_collapse"):
        return "accept_visible_evidence_only"
    if pass_behavior_group_count > 1:
        return "abstain_high_spec_debt"
    if metrics.get("pass_fail_split"):
        return "rerank_probe_passing_candidates_and_abstain_until_audit"
    return "abstain_behavior_disagreement"


def candidate_decision(probe_record, pass_behavior_group_count):
    outcome = probe_record.get("outcome") if probe_record else ""
    if outcome == "pass" and pass_behavior_group_count <= 1:
        return "retain_or_promote_for_review"
    if outcome == "pass":
        return "retain_but_request_spec_audit"
    if outcome == "fail":
        return "demote_or_reject_pending_audit"
    if outcome == "timeout":
        return "rerun_or_quarantine_timeout"
    return "insufficient_probe_evidence"


def build_records(args, certificates, apply_results, probe_results):
    apply_by_candidate = indexed(apply_results, "candidate_id")
    probes = probe_index(probe_results)
    ledger = []
    cc_ogb_records = []
    adjudication_records = []
    created_at = utc_now()

    for certificate in sorted(certificates, key=lambda item: item.get("certificate_id") or ""):
        task_id = certificate.get("task_id")
        probe_id = certificate.get("probe_id")
        groups = group_records(certificate)
        metrics = cc_ogb_metrics(certificate)
        pass_behavior_group_count = len([group for group in groups if group.get("outcome") == "pass"])
        specification_debt_signal = pass_behavior_group_count > 1
        candidates = []
        candidate_decisions = []
        for candidate in sorted(flatten_candidates(certificate), key=lambda item: item.get("candidate_id") or ""):
            candidate_id = candidate.get("candidate_id")
            probe_record = probes.get((task_id, probe_id, candidate_id))
            vis = visible_summary(candidate_id, apply_by_candidate)
            c_record = {
                "candidate_id": candidate_id,
                "candidate_source": candidate.get("candidate_source"),
                "candidate_model_generated": bool(candidate.get("candidate_model_generated")),
                "candidate_heuristic": bool(candidate.get("candidate_heuristic")),
                "candidate_semantic_template": candidate.get("candidate_semantic_template") or "",
                "candidate_generation_backend": candidate.get("candidate_generation_backend") or "",
                "behavior_hash": candidate.get("behavior_hash"),
                "behavior_outcome": candidate.get("behavior_outcome"),
                "behavior_exit_code": candidate.get("behavior_exit_code"),
                "probe_outcome": probe_record.get("outcome") if probe_record else "",
                "probe_exit_code": probe_record.get("exit_code") if probe_record else None,
                "probe_result_path": probe_record.get("probe_code_path") if probe_record else "",
                "stdout_artifact": probe_record.get("stdout_artifact") if probe_record else {},
                "stderr_artifact": probe_record.get("stderr_artifact") if probe_record else {},
                "visible": vis,
            }
            c_record["adjudication"] = candidate_decision(probe_record, pass_behavior_group_count)
            candidates.append(c_record)
            candidate_decisions.append(
                {
                    "candidate_id": candidate_id,
                    "candidate_source": candidate.get("candidate_source"),
                    "candidate_model_generated": bool(candidate.get("candidate_model_generated")),
                    "candidate_heuristic": bool(candidate.get("candidate_heuristic")),
                    "probe_outcome": c_record["probe_outcome"],
                    "behavior_hash": candidate.get("behavior_hash"),
                    "decision": c_record["adjudication"],
                }
            )

        decision = task_decision(metrics, pass_behavior_group_count)
        ledger_entry = {
            "schema_version": "0.1",
            "queue_id": args.queue_id,
            "task_id": task_id,
            "repo": certificate.get("repo"),
            "certificate_id": certificate.get("certificate_id"),
            "bdc_queue_id": args.bdc_queue_id,
            "apply_queue_id": args.apply_queue_id,
            "probe_queue_id": args.probe_queue_id,
            "probe_id": probe_id,
            "probe_description": certificate.get("probe_description"),
            "evidence_type": "behavioral_disagreement_certificate",
            "evidence_status": "gold_blind_issue_probe",
            "metrics": metrics,
            "behavior_groups": groups,
            "candidates": candidates,
            "specification_debt_signal": specification_debt_signal,
            "adjudication_decision": decision,
            "risk_tier": risk_tier(metrics),
            "interpretation": (
                "Visible tests did not collapse visible-passing candidate patches into a single "
                "executable behavior under an issue-derived probe. This is evidence of oracle-gap "
                "risk, not a claim of absolute correctness."
            ),
            "claim_support": [
                "visible_pass_candidates_can_disagree",
                "oracle_free_candidate_conditional_gap_lower_bound",
                "abstain_or_rerank_is_justified_before_gold_evaluation",
            ],
            "source_paths": {
                "bdc_certificates": os.path.join(
                    args.snapshot_run_dir,
                    "bdc_queues",
                    args.bdc_queue_id,
                    "behavior_disagreement_certificates.jsonl",
                ),
                "apply_results": os.path.join(
                    args.snapshot_run_dir,
                    "candidate_apply_queues",
                    args.apply_queue_id,
                    "candidate_apply_results.jsonl",
                ),
                "probe_results": os.path.join(
                    args.snapshot_run_dir,
                    "issue_probe_queues",
                    args.probe_queue_id,
                    "issue_probe_results.jsonl",
                ),
            },
            "gold_used": False,
            "created_at": created_at,
        }
        ledger.append(ledger_entry)
        cc_ogb_records.append(
            {
                "schema_version": "0.1",
                "queue_id": args.queue_id,
                "task_id": task_id,
                "certificate_id": certificate.get("certificate_id"),
                "probe_id": probe_id,
                "formula": "CC-OGB_lb(T) = 1 - max_b |H_T^+(b)| / |H_T^+|",
                "meaning": (
                    "Candidate-conditional lower bound on the fraction of visible-passing "
                    "candidate hypotheses not explained by the majority observed behavior."
                ),
                "assumptions": [
                    "only visible-passing candidate patches in the current candidate pool are conditioned on",
                    "issue-derived probe behavior is executable evidence but not an oracle label",
                    "developer patch and held-out test labels are not used",
                ],
                "metrics": metrics,
                "gold_used": False,
                "created_at": created_at,
            }
        )
        adjudication_records.append(
            {
                "schema_version": "0.1",
                "queue_id": args.queue_id,
                "task_id": task_id,
                "certificate_id": certificate.get("certificate_id"),
                "probe_id": probe_id,
                "task_decision": decision,
                "risk_tier": risk_tier(metrics),
                "specification_debt_signal": specification_debt_signal,
                "candidate_decisions": candidate_decisions,
                "policy": (
                    "Never accept a patch solely because it passes visible tests when a BDC exists; "
                    "use probe behavior to rerank and abstain until audit or held-out evaluation."
                ),
                "gold_used": False,
                "created_at": created_at,
            }
        )
    return ledger, cc_ogb_records, adjudication_records


def summarize(args, ledger, cc_ogb_records, adjudication_records, cert_count, apply_count, probe_count):
    bounds = [record.get("metrics", {}).get("cc_ogb_lower_bound", 0.0) for record in cc_ogb_records]
    pair_rates = [record.get("metrics", {}).get("candidate_pair_disagreement_rate", 0.0) for record in cc_ogb_records]
    pass_fail_tasks = len([record for record in cc_ogb_records if record.get("metrics", {}).get("pass_fail_split")])
    spec_debt_tasks = len([record for record in ledger if record.get("specification_debt_signal")])
    decisions = collections.Counter(record.get("task_decision") for record in adjudication_records)
    risk_tiers = collections.Counter(record.get("risk_tier") for record in adjudication_records)
    total_candidate_observations = sum(record.get("metrics", {}).get("candidate_count", 0) for record in cc_ogb_records)
    return {
        "schema_version": "0.1",
        "queue_id": args.queue_id,
        "snapshot_run_dir": args.snapshot_run_dir,
        "bdc_queue_id": args.bdc_queue_id,
        "apply_queue_id": args.apply_queue_id,
        "probe_queue_id": args.probe_queue_id,
        "ledger_path": os.path.join(args.output_dir, "evidence_ledger.jsonl"),
        "cc_ogb_path": os.path.join(args.output_dir, "cc_ogb_records.jsonl"),
        "adjudication_path": os.path.join(args.output_dir, "adjudication_records.jsonl"),
        "certificate_count_input": cert_count,
        "apply_result_count_input": apply_count,
        "probe_result_count_input": probe_count,
        "task_count": len(ledger),
        "ledger_record_count": len(ledger),
        "cc_ogb_record_count": len(cc_ogb_records),
        "adjudication_record_count": len(adjudication_records),
        "total_candidate_observations": total_candidate_observations,
        "tasks_with_pass_fail_split": pass_fail_tasks,
        "tasks_with_specification_debt_signal": spec_debt_tasks,
        "mean_cc_ogb_lower_bound": round(sum(bounds) / len(bounds), 6) if bounds else 0.0,
        "max_cc_ogb_lower_bound": max(bounds) if bounds else 0.0,
        "mean_candidate_pair_disagreement_rate": round(sum(pair_rates) / len(pair_rates), 6) if pair_rates else 0.0,
        "decision_counts": dict(decisions),
        "risk_tier_counts": dict(risk_tiers),
        "gold_used": False,
        "created_at": utc_now(),
        "records": [
            {
                "task_id": record.get("task_id"),
                "certificate_id": record.get("certificate_id"),
                "probe_id": record.get("probe_id"),
                "candidate_count": record.get("metrics", {}).get("candidate_count"),
                "behavior_group_count": record.get("metrics", {}).get("behavior_group_count"),
                "pass_count": record.get("metrics", {}).get("pass_count"),
                "fail_count": record.get("metrics", {}).get("fail_count"),
                "cc_ogb_lower_bound": record.get("metrics", {}).get("cc_ogb_lower_bound"),
                "pair_disagreement_rate": record.get("metrics", {}).get("candidate_pair_disagreement_rate"),
                "decision": record.get("adjudication_decision"),
                "risk_tier": record.get("risk_tier"),
            }
            for record in ledger
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-run-dir", required=True)
    parser.add_argument("--bdc-queue-id", required=True)
    parser.add_argument("--apply-queue-id", required=True)
    parser.add_argument("--probe-queue-id", required=True)
    parser.add_argument("--queue-id", required=True)
    args = parser.parse_args(argv)

    output_dir = os.path.join(args.snapshot_run_dir, "evidence_ledger_queues", args.queue_id)
    if os.path.exists(output_dir) and os.listdir(output_dir):
        raise RuntimeError("output directory already has files: %s" % output_dir)
    args.output_dir = output_dir

    bdc_path = os.path.join(
        args.snapshot_run_dir,
        "bdc_queues",
        args.bdc_queue_id,
        "behavior_disagreement_certificates.jsonl",
    )
    apply_path = os.path.join(
        args.snapshot_run_dir,
        "candidate_apply_queues",
        args.apply_queue_id,
        "candidate_apply_results.jsonl",
    )
    probe_path = os.path.join(
        args.snapshot_run_dir,
        "issue_probe_queues",
        args.probe_queue_id,
        "issue_probe_results.jsonl",
    )

    certificates = read_jsonl(bdc_path)
    apply_results = read_jsonl(apply_path)
    probe_results = read_jsonl(probe_path)

    ledger, cc_ogb_records, adjudication_records = build_records(
        args, certificates, apply_results, probe_results
    )
    summary = summarize(
        args,
        ledger,
        cc_ogb_records,
        adjudication_records,
        len(certificates),
        len(apply_results),
        len(probe_results),
    )
    write_jsonl(os.path.join(output_dir, "evidence_ledger.jsonl"), ledger)
    write_jsonl(os.path.join(output_dir, "cc_ogb_records.jsonl"), cc_ogb_records)
    write_jsonl(os.path.join(output_dir, "adjudication_records.jsonl"), adjudication_records)
    write_json(os.path.join(output_dir, "evidence_ledger_summary.json"), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
