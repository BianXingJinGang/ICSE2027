# PatchCourt Main Tables 2026-05-28

This file is the table plan for the double-blind ICSE draft. It separates main evidence, supplementary evidence, and claim-boundary tables so the paper does not overclaim the current Qwen results.

Safe-route characterization outputs are now available and should be integrated into the main or appendix table plan:

- `paper/icse2027/assets_20260528/safe_route_characterization_20260528.md`
- `paper/icse2027/assets_20260528/safe_route_characterization_20260528.json`
- `paper/icse2027/assets_20260528/safe_route_*_20260528.csv`

## Table 1: Frozen Held-Out Calibration

Purpose: establish the phenomenon.

Source:

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table1_heldout_false_acceptance_20260526.csv`

Paper-facing summary:

| Quantity | Value |
| --- | ---: |
| Frozen conservative certificates | 30 |
| Held-out executable tasks | 30/30 |
| Held-out false acceptances | 17/30 |
| Wilson 95% CI for false acceptance | 0.567 [0.392, 0.726] |
| Specification-debt signal | 26/30 |
| Wilson 95% CI for specification debt | 0.867 [0.703, 0.947] |

Caption draft:

"Held-out calibration after the certificate index is frozen. All 30 frozen certificates execute under the held-out FAIL_TO_PASS layer; 17 visible/probe-accepted cases fail the held-out issue tests."

## Table 2: Main Full-Package / Issue-Code Probe Upgrade

Purpose: show that the source-isolated signal survives stronger probes for a nontrivial subset.

Source:

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table2_upgraded_probe_20260526.csv`

Paper-facing summary:

| Quantity | Value |
| --- | ---: |
| Upgrade targets | 10 |
| Probe executions | 40 |
| Pass/fail BDC tasks | 6/10 |
| Wilson 95% CI | 0.600 [0.313, 0.832] |

Pass/fail upgraded tasks:

| Task | Probe |
| --- | --- |
| `django__django-16255` | `upgrade-fullpkg-django-empty-sitemap-lastmod` |
| `django__django-16873` | `upgrade-fullpkg-django-join-autoescape-off` |
| `matplotlib__matplotlib-24149` | `upgrade-fullpkg-matplotlib-bar-all-nan` |
| `mwaskom__seaborn-3407` | `upgrade-fullpkg-seaborn-pairplot-multiindex` |
| `scikit-learn__scikit-learn-10508` | `upgrade-fullpkg-sklearn-labelencoder-empty-transform` |
| `sympy__sympy-23117` | `upgrade-issuecode-sympy-empty-array` |

Caption draft:

"Probe-upgrade results for ten high-signal audited certificates. Six produce pass/fail behavior-disagreement certificates under full-package or issue-code execution."

## Table 3: Extra Full-Package Probe Layer

Purpose: provide robustness evidence without merging weaker all-fail divergences into the main count.

Source:

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table6_extra_full_package_probe_20260526.csv`

Paper-facing summary:

| Quantity | Value |
| --- | ---: |
| Extra full-package targets | 10 |
| Probe executions | 40 |
| BDC tasks | 7/10 |
| Pass/fail BDC tasks | 6/10 |
| All-fail divergence tasks | 1/10 |

Caption draft:

"Additional full-package probes over a second target set. Six of ten targets yield pass/fail certificates; one additional target yields all-fail behavioral divergence and is reported separately."

## Table 4: Correlation And Risk Ranking

Purpose: support PatchCourt as a risk triage substrate, not a replacement oracle.

Sources:

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table3_correlation_20260526.csv`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table4_rerank_20260526.csv`

Paper-facing summary:

| Signal | Pearson | Spearman | Average precision |
| --- | ---: | ---: | ---: |
| Raw CC-OGB | -0.116 | -0.144 | 0.557 |
| CC-OGB plus specification debt | 0.146 | 0.115 | 0.612 |
| Audit-weighted risk | 0.129 | 0.107 | 0.617 |
| Specification-debt indicator | 0.449 | 0.449 | 0.612 |

Rerank summary:

| Score | Precision@10 | Precision@20 |
| --- | ---: | ---: |
| Raw CC-OGB | 0.400 | 0.550 |
| CC-OGB plus specification debt | 0.500 | 0.650 |
| Audit-weighted risk | 0.600 | 0.650 |

Caption draft:

"PatchCourt signals are better interpreted as triage scores than as correctness labels. Specification debt and audit-weighted risk improve top-k prioritization in the frozen 30-task calibration set."

## Table 5: Abstention Policies

Purpose: show review-budget and risk-control use.

Source:

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table5_abstain_20260526.csv`

Paper-facing summary:

| Rule | Abstain rate | False-acceptance capture | Residual false-acceptance rate |
| --- | ---: | ---: | ---: |
| `cc_ogb>=0.50` | 0.167 | 0.118 | 0.600 |
| `cc_ogb>=0.75` | 0.067 | 0.059 | 0.571 |
| `specification_debt_signal` | 0.867 | 1.000 | 0.000 |

Caption draft:

"Example abstention policies on the frozen set. The specification-debt rule is conservative and high-coverage; raw CC-OGB thresholds alone are under-calibrated at this sample size."

## Table 6: Qwen Independent-Source Applicability

Purpose: show that Qwen is a real independent source and that structured edits solve the direct-diff apply failure.

Sources:

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen25coder7b_gguf_local_endpoint_frozen30_20260527_report.md`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen_structured_frozen30_20260527_report.md`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen_structured_frozen30_summary_20260527.json`

Paper-facing summary:

| Qwen protocol | Materialized/applyable | Compatible visible-pass | Strict visible-pass | BDC tasks |
| --- | ---: | ---: | ---: | ---: |
| Direct unified diff, normalized | 6/28 raw diffs | 1/30 | not used | 0 |
| Structured search/replace, frozen 30 | 17/30 | 11/30 | 6/30 | 0 |
| Structured search/replace, visible-11 multi-sample | 29/44 model samples | 26 model samples across 9 tasks | 14 model samples across 5 tasks | see Table 7 |

Caption draft:

"Independent Qwen source applicability. Direct diff prompting fails at the patch-application layer; structured search/replace generation produces a visible-pass candidate pool suitable for PatchCourt probes."

## Table 7: Qwen BDC Audit

Purpose: report RQ4 without overclaiming.

Sources:

- `paper/icse2027/assets_20260528/qwen_bdc_audit_20260528.md`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/bdc_queue_20260527_155027_certificates.jsonl`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/bdc_queue_20260527_155342_certificates.jsonl`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/bdc_queue_20260527_184051_certificates.jsonl`

Paper-facing summary:

| Qwen BDC layer | BDC tasks | Pass/fail tasks | Paper status |
| --- | ---: | ---: | --- |
| Generic source-isolated probes | 0 | 0 | Negative |
| Issue/full-package probes | 5 | 1 | One main issue-specific case, four downgraded all-fail divergences |
| Package-integrity probes | 4 | 4 | Separate full-package integrity evidence |
| Issue-specific rescue probes | 2 | 0 | Negative rescue result |

Caption draft:

"Audited Qwen BDCs after multi-sample structured generation. Only one Qwen certificate is issue-specific pass/fail; four additional pass/fail certificates are full-package integrity checks and are reported separately."

## Table 8: Claim Ledger Boundary

Purpose: make the paper reviewer-proof on what each evidence type supports.

| Evidence type | Supports | Does not support |
| --- | --- | --- |
| Frozen held-out false acceptance | Visible/probe acceptance often fails held-out labels | Absolute patch correctness |
| Main upgraded pass/fail BDCs | Stronger probes preserve certificate signal | General calibrated prediction |
| Extra full-package pass/fail BDCs | Robustness of package-level probe signal | Issue-specific correctness for all tasks |
| Qwen issue-specific pass/fail BDC | A single independent-source issue-specific compatibility case | Broad Qwen reproduction |
| Qwen package-integrity BDCs | Independent-source visible-pass patches can break package behavior | Issue correctness |
| Qwen all-fail divergences | Diagnostic behavior diversity | Positive BDC yield |

Caption draft:

"Claim boundary by evidence type. PatchCourt reports executable risk evidence, not oracle replacement."
