# Level 1 Table Regeneration Report 2026-05-29

Status: **PASS**

This check is run from the anonymous inspect-only artifact. It recomputes the manuscript headline counts, selection-funnel transparency checks, pilot-50 drop-reason counts, and route-stability checks from packaged CSV, JSONL, and Markdown files only. It does not access model endpoints, raw worktrees, private paths, or hidden labels outside the package.

## Recomputed Checks

| metric | expected | observed | status |
| --- | --- | --- | --- |
| heldout_records | 30 | 30 | PASS |
| heldout_executable | 30 | 30 | PASS |
| false_acceptance_true | 17 | 17 | PASS |
| specification_debt_true | 26 | 26 | PASS |
| frozen_source_isolated_original_layer | 26 | 26 | PASS |
| frozen_custom_active_original_layer | 3 | 3 | PASS |
| frozen_issue_code_original_layer | 1 | 1 | PASS |
| frozen_direct_batch_source | 23 | 23 | PASS |
| frozen_codex_source | 7 | 7 | PASS |
| manual_audit_retain | 22 | 22 | PASS |
| manual_audit_downgrade | 8 | 8 | PASS |
| manual_audit_reject | 0 | 0 | PASS |
| main_upgrade_targets | 10 | 10 | PASS |
| main_upgrade_bdc_tasks | 6 | 6 | PASS |
| main_upgrade_pass_fail_bdc_tasks | 6 | 6 | PASS |
| extra_full_package_targets | 10 | 10 | PASS |
| extra_full_package_bdc_tasks | 7 | 7 | PASS |
| extra_full_package_pass_fail_bdc_tasks | 6 | 6 | PASS |
| qwen_issue_full_package_bdc_tasks | 5 | 5 | PASS |
| qwen_issue_full_package_pass_fail_tasks | 1 | 1 | PASS |
| qwen_package_integrity_pass_fail_tasks | 4 | 4 | PASS |
| qwen_rescue_pass_fail_tasks | 0 | 0 | PASS |
| rerank_cc_only_precision_at_10 | 0.4 | 0.4 | PASS |
| rerank_cc_only_precision_at_20 | 0.55 | 0.55 | PASS |
| rerank_audit_weighted_precision_at_10 | 0.6 | 0.6 | PASS |
| rerank_audit_weighted_precision_at_20 | 0.65 | 0.65 | PASS |
| abstain_spec_debt_capture_rate | 1.0 | 1.0 | PASS |
| abstain_spec_debt_residual_false_acceptances | 0 | 0 | PASS |
| correlation_rows | 4 | 4 | PASS |
| pilot50_rows | 50 | 50 | PASS |
| pilot50_snapshot_built | 50 | 50 | PASS |
| pilot50_candidate_slots_total | 200 | 200 | PASS |
| pilot50_frozen_conservative | 27 | 27 | PASS |
| pilot50_broad_not_frozen | 1 | 1 | PASS |
| pilot50_no_conservative_certificate | 22 | 22 | PASS |
| selection_funnel_pilot_tasks | 50 | 50 | PASS |
| selection_funnel_raw_certificates | 37 | 37 | PASS |
| selection_funnel_frozen_certificates | 30 | 30 | PASS |
| selection_funnel_original_layers | 26 / 3 / 1 | 26 / 3 / 1 | PASS |
| selection_funnel_candidate_sources | 23 / 7 | 23 / 7 | PASS |
| route_heldout_before_after | 15/30 executable -> 30/30 executable | 15/30 executable -> 30/30 executable | PASS |
| route_upgrade_before_after | 2/10 upgraded BDC targets -> 6/10 pass/fail BDC targets | 2/10 upgraded BDC targets -> 6/10 pass/fail BDC targets | PASS |
| route_frozen_index_before_after | 30 conservative records -> 30 conservative records | 30 conservative records -> 30 conservative records | PASS |
| qwen_audit_mentions_final_issue_count | True | True | PASS |

## Input File Fingerprints

| file | sha256 | bytes |
| --- | --- | --- |
| tables/table1_heldout_false_acceptance_20260526.csv | 1ec6563a3e328b19 | 6263 |
| tables/table2_upgraded_probe_20260526.csv | a66dc149d8033c6c | 2028 |
| tables/table3_correlation_20260526.csv | 5eaab6b35dcb06e9 | 422 |
| tables/table4_rerank_20260526.csv | 9293db3ab2ba5179 | 682 |
| tables/table5_abstain_20260526.csv | 576110ac5601a3b4 | 492 |
| tables/table6_extra_full_package_probe_20260526.csv | cf1c5583b0b34b76 | 2228 |
| tables/pilot50_drop_reasons_20260529.csv | 116f413c2b6ca41f | 18770 |
| tables/selection_funnel_20260529.csv | 0456466a8af4ebb3 | 1895 |
| tables/route_stability_20260529.csv | c5d5b9a2431cc67c | 578 |
| certificates/bdc_queue_20260527_155027_certificates.jsonl | 87e56ea2e4644b50 | 27469 |
| certificates/bdc_queue_20260527_155342_certificates.jsonl | 6608ec0d4879c49a | 21924 |
| certificates/bdc_queue_20260527_184051_certificates.jsonl | 63b75708f141594a | 9759 |
| tables/qwen_bdc_audit_20260528.md | a9c9c08feed3d351 | 9545 |

## Reviewer Command

```bash
python scripts/verify_level1_tables_20260528.py
```

Output files:

- `docs/LEVEL1_TABLE_REGENERATION_REPORT_20260528.md`
- `generated/level1_table_recheck_20260528.json`
