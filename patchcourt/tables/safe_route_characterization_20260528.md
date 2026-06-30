# Safe-Route Characterization 2026-05-28

This report locks the lower-risk ICSE route: characterize visible-test false acceptance and present PatchCourt as an auditable triage protocol, not as a correctness oracle or a broad independent-model reproduction claim.

## Locked Title

`Visible Tests Are Not Oracles: Characterizing False Acceptance in LLM-Based Repository Repair`

## Core Claim

Visible/probe acceptance leaves substantial residual held-out risk in LLM repository repair. PatchCourt provides a gold-boundary-aware evidence ledger and risk-triage protocol that exposes this risk before held-out labels are read.

## Main Characterization Tables

### By Manual Audit Status

| manual_audit_status | tasks | false_acceptance | false_acceptance_rate |
| --- | --- | --- | --- |
| downgrade | 8 | 4 | 0.5 |
| retain | 22 | 13 | 0.591 |

### By Candidate Source

| calibration_source | tasks | false_acceptance | false_acceptance_rate |
| --- | --- | --- | --- |
| codex_session_bootstrap | 7 | 3 | 0.429 |
| llm_batch_direct | 23 | 14 | 0.609 |

### By Original Probe Layer

| original_probe_layer | tasks | false_acceptance | false_acceptance_rate |
| --- | --- | --- | --- |
| custom_active_probe | 3 | 0 | 0.0 |
| issue_codeblock_full_package | 1 | 0 | 0.0 |
| source_isolated_template | 26 | 17 | 0.654 |

### By Specification Debt

| specification_debt_signal | tasks | false_acceptance | false_acceptance_rate |
| --- | --- | --- | --- |
| False | 4 | 0 | 0.0 |
| True | 26 | 17 | 0.654 |

### By Stronger Probe Overlay

| safe_route_probe_status | tasks | false_acceptance | false_acceptance_rate |
| --- | --- | --- | --- |
| extra_all_fail_divergence | 1 | 1 | 1.0 |
| extra_no_bdc | 3 | 2 | 0.667 |
| extra_pass_fail | 6 | 3 | 0.5 |
| main_no_bdc | 4 | 3 | 0.75 |
| main_pass_fail | 6 | 3 | 0.5 |
| not_upgraded | 10 | 5 | 0.5 |

### By Qwen Status

| safe_route_qwen_status | tasks | false_acceptance | false_acceptance_rate |
| --- | --- | --- | --- |
| not_qwen_positive | 26 | 13 | 0.5 |
| qwen_issue_specific | 1 | 1 | 1.0 |
| qwen_package_integrity | 3 | 3 | 1.0 |

## Top Case Study Candidates

| task_id | score | false_acceptance | probe_status | qwen_status | reason |
| --- | --- | --- | --- | --- | --- |
| mwaskom__seaborn-3407 | 12 | True | main_pass_fail | qwen_issue_specific | heldout_false_acceptance;stronger_probe_pass_fail;retained_audit;qwen_issue_specific |
| scikit-learn__scikit-learn-10508 | 11 | True | main_pass_fail | qwen_package_integrity | heldout_false_acceptance;stronger_probe_pass_fail;retained_audit;qwen_package_integrity |
| matplotlib__matplotlib-24149 | 10 | True | main_pass_fail | not_qwen_positive | heldout_false_acceptance;stronger_probe_pass_fail;retained_audit |
| psf__requests-2148 | 10 | True | extra_pass_fail | not_qwen_positive | heldout_false_acceptance;stronger_probe_pass_fail;retained_audit |
| pydata__xarray-4094 | 10 | True | extra_pass_fail | not_qwen_positive | heldout_false_acceptance;stronger_probe_pass_fail;retained_audit |
| pylint-dev__pylint-7114 | 10 | True | extra_pass_fail | not_qwen_positive | heldout_false_acceptance;stronger_probe_pass_fail;retained_audit |
| mwaskom__seaborn-3190 | 8 | True | not_upgraded | qwen_package_integrity | heldout_false_acceptance;retained_audit;qwen_package_integrity |
| pallets__flask-5063 | 8 | True | extra_no_bdc | qwen_package_integrity | heldout_false_acceptance;retained_audit;qwen_package_integrity |
| astropy__astropy-14365 | 7 | True | main_no_bdc | not_qwen_positive | heldout_false_acceptance;retained_audit |
| mwaskom__seaborn-2848 | 7 | True | extra_all_fail_divergence | not_qwen_positive | heldout_false_acceptance;retained_audit |

## Paper Consequences

- Put the 17/30 held-out false-acceptance result in the abstract and first results table.
- Treat full-package/issue-code BDCs as validation that the signal is not only a source-isolated artifact.
- Treat Qwen as a stress-test and boundary result: one issue-specific BDC plus four package-integrity BDCs.
- Move any claim about broad independent-source reproduction out of the main thesis.
- Use rerank/abstain as a practical triage demonstration, not as a calibrated predictor claim.

## Next Work Under This Route

1. Page-budget the double-blind draft around RQ1-RQ3 as the main spine.
2. Add related work around plausible patches, SWE-bench false acceptance, generated tests, and oracle problem work.
3. Build an anonymous inspect-only artifact bundle.
4. Only after the main empirical story is stable, optionally add a second independent model source or more Qwen issue-specific BDCs.
