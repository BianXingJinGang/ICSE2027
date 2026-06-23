# PatchCourt Submission Table Pack 2026-05-28

This is the paper-facing table pack for the conservative ICSE route. It converts the earlier table plan into manuscript-ready tables and captions. The tables intentionally separate main evidence, robustness evidence, and claim-boundary evidence.

## Table 1. Frozen Held-Out Calibration

Caption: Held-out calibration after the certificate index is frozen. All 30 frozen certificates execute under the held-out FAIL_TO_PASS layer; 17 visible/probe-accepted cases fail the held-out issue tests.

| Quantity | Value |
| --- | ---: |
| Frozen conservative certificates | 30 |
| Held-out executable tasks | 30/30 |
| Held-out false acceptances | 17/30 |
| Wilson 95% CI for false acceptance | 0.567 [0.392, 0.726] |
| Specification-debt signal | 26/30 |
| Wilson 95% CI for specification debt | 0.867 [0.703, 0.947] |

Source: `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table1_heldout_false_acceptance_20260526.csv`.

## Table 2. Characterization By Audit And Specification Debt

Caption: False acceptance remains common after manual audit. Specification debt is a conservative high-coverage risk signal in the frozen set.

| Stratum | Tasks | False Acceptances | Rate |
| --- | ---: | ---: | ---: |
| Manual audit: retain | 22 | 13 | 0.591 |
| Manual audit: downgrade | 8 | 4 | 0.500 |
| Specification debt: present | 26 | 17 | 0.654 |
| Specification debt: absent | 4 | 0 | 0.000 |

Sources:

- `paper/icse2027/assets_20260528/safe_route_by_manual_audit_status_20260528.csv`
- `paper/icse2027/assets_20260528/safe_route_by_specification_debt_signal_20260528.csv`

## Table 3. Main Full-Package / Issue-Code Probe Upgrade

Caption: Probe-upgrade results for ten high-signal audited certificates. Six produce pass/fail behavior-disagreement certificates under full-package or issue-code execution.

| Quantity | Value |
| --- | ---: |
| Upgrade targets | 10 |
| Probe executions | 40 |
| Pass/fail BDC tasks | 6/10 |
| Wilson 95% CI | 0.600 [0.313, 0.832] |

| Task | Probe |
| --- | --- |
| `django__django-16255` | `upgrade-fullpkg-django-empty-sitemap-lastmod` |
| `django__django-16873` | `upgrade-fullpkg-django-join-autoescape-off` |
| `matplotlib__matplotlib-24149` | `upgrade-fullpkg-matplotlib-bar-all-nan` |
| `mwaskom__seaborn-3407` | `upgrade-fullpkg-seaborn-pairplot-multiindex` |
| `scikit-learn__scikit-learn-10508` | `upgrade-fullpkg-sklearn-labelencoder-empty-transform` |
| `sympy__sympy-23117` | `upgrade-issuecode-sympy-empty-array` |

Source: `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table2_upgraded_probe_20260526.csv`.

## Table 4. Extra Full-Package Probe Layer

Caption: Additional full-package probes over a second target set. Six of ten targets yield pass/fail certificates; one additional target yields all-fail behavioral divergence and is reported separately.

| Quantity | Value |
| --- | ---: |
| Extra full-package targets | 10 |
| Probe executions | 40 |
| BDC tasks | 7/10 |
| Pass/fail BDC tasks | 6/10 |
| All-fail divergence tasks | 1/10 |

Source: `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table6_extra_full_package_probe_20260526.csv`.

## Table 5. Correlation And Risk Ranking

Caption: PatchCourt signals are better interpreted as triage scores than as correctness labels. Specification debt and audit-weighted risk improve top-k prioritization in the frozen 30-task calibration set.

| Signal | Pearson | Spearman | Average Precision |
| --- | ---: | ---: | ---: |
| Raw CC-OGB | -0.116 | -0.144 | 0.557 |
| CC-OGB plus specification debt | 0.146 | 0.115 | 0.612 |
| Audit-weighted risk | 0.129 | 0.107 | 0.617 |
| Specification-debt indicator | 0.449 | 0.449 | 0.612 |

| Score | Precision@10 | Precision@20 |
| --- | ---: | ---: |
| Raw CC-OGB | 0.400 | 0.550 |
| CC-OGB plus specification debt | 0.500 | 0.650 |
| Audit-weighted risk | 0.600 | 0.650 |

Sources:

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table3_correlation_20260526.csv`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table4_rerank_20260526.csv`

## Table 6. Abstention Policies

Caption: Example abstention policies on the frozen set. The specification-debt rule is conservative and high-coverage; raw CC-OGB thresholds alone are under-calibrated at this sample size.

| Rule | Abstain Rate | False-Acceptance Capture | Residual False-Acceptance Rate |
| --- | ---: | ---: | ---: |
| `cc_ogb>=0.50` | 0.167 | 0.118 | 0.600 |
| `cc_ogb>=0.75` | 0.067 | 0.059 | 0.571 |
| `specification_debt_signal` | 0.867 | 1.000 | 0.000 |

Source: `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table5_abstain_20260526.csv`.

## Table 7. Qwen Independent-Source Applicability

Caption: Independent Qwen source applicability. Direct diff prompting fails at the patch-application layer; structured search/replace generation produces a visible-pass candidate pool suitable for PatchCourt probes.

| Qwen Protocol | Materialized / Applyable | Compatible Visible-Pass | Strict Visible-Pass | BDC Tasks |
| --- | ---: | ---: | ---: | ---: |
| Direct unified diff, normalized | 6/28 raw diffs | 1/30 | not used | 0 |
| Structured search/replace, frozen 30 | 17/30 | 11/30 | 6/30 | 0 |
| Structured search/replace, visible-11 multi-sample | 29/44 model samples | 26 model samples across 9 tasks | 14 model samples across 5 tasks | see Table 8 |

Sources:

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen25coder7b_gguf_local_endpoint_frozen30_20260527_report.md`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen_structured_frozen30_20260527_report.md`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen_multisample_visible11_probe_bdc_20260527_report.md`

## Table 8. Qwen BDC Audit

Caption: Audited Qwen BDCs after multi-sample structured generation. Only one Qwen certificate is issue-specific pass/fail; four additional pass/fail certificates are full-package integrity checks and are reported separately.

| Qwen BDC Layer | BDC Tasks | Pass/Fail Tasks | Paper Status |
| --- | ---: | ---: | --- |
| Generic source-isolated probes | 0 | 0 | Negative |
| Issue/full-package probes | 5 | 1 | One main issue-specific case; four downgraded all-fail divergences |
| Package-integrity probes | 4 | 4 | Separate full-package integrity evidence |
| Issue-specific rescue probes | 2 | 0 | Negative rescue result |

Source: `paper/icse2027/assets_20260528/qwen_bdc_audit_20260528.md`.

## Table 9. Claim Boundary

Caption: Claim boundary by evidence type. PatchCourt reports executable risk evidence, not oracle replacement.

| Evidence Type | Supports | Does Not Support |
| --- | --- | --- |
| Frozen held-out false acceptance | Visible/probe acceptance often fails held-out labels in the frozen audit set | Absolute patch correctness |
| Main upgraded pass/fail BDCs | Stronger probes preserve certificate signal for selected targets | General calibrated prediction |
| Extra full-package pass/fail BDCs | Robustness of package-level probe signal | Issue-specific correctness for all tasks |
| Qwen issue-specific pass/fail BDC | A single independent-source issue-specific compatibility case | Broad Qwen reproduction |
| Qwen package-integrity BDCs | Independent-source visible-pass patches can break package behavior | Issue correctness |
| Qwen all-fail divergences | Diagnostic behavior diversity | Positive BDC yield |

## Main-Text Table Recommendation

Use Tables 1, 3, 5, and 9 in the main text if page budget is tight. Move Tables 2, 4, 6, 7, and 8 to appendix or condensed supplementary tables.
