# Qwen BDC Audit 2026-05-28

This file is the paper-facing audit of the Qwen2.5-Coder-7B GGUF independent-source evidence after the multi-sample run and the follow-up issue-specific rescue attempt. It is intentionally conservative: package-integrity certificates are not counted as issue-specific correctness evidence, and all-fail behavior divergence is not counted as pass/fail BDC yield.

## Executive Conclusion

Qwen is a real non-Codex candidate source in the current artifact, but the strong issue-specific BDC yield remains limited.

Claimable:

- Qwen structured generation is connected through a local OpenAI-compatible endpoint and produces visible-passing repository patches.
- Multi-sample Qwen generation over the 11 prior visible-pass tasks produced 26 compatible visible-pass model candidates across 9 tasks.
- Qwen produced 1 strong issue/full-package pass/fail BDC: `mwaskom__seaborn-3407`.
- Qwen produced 4 pass/fail package-integrity BDCs: `mwaskom__seaborn-3190`, `mwaskom__seaborn-3407`, `pallets__flask-5063`, and `scikit-learn__scikit-learn-10508`.
- The Pylint rescue run fixed the child-process import-routing question but produced only all-fail divergence, not additional issue-specific pass/fail BDCs.

Not claimable:

- Do not claim that Qwen broadly reproduces the issue-specific BDC signal from the Codex/bootstrap candidate lane.
- Do not count package-integrity BDCs as issue correctness.
- Do not count all-fail divergence as pass/fail BDC yield.
- Do not present `llm_batch_direct` as an independent external model baseline.

Bottom line for RQ4:

- Strong wording: "PatchCourt can ingest a real non-Codex candidate source and finds nonzero independent-source behavioral disagreement after multi-sample structured generation."
- Conservative wording: "The independent Qwen lane is partial-positive for full-package integrity and only one-task-positive for issue-specific pass/fail BDCs."

## Evidence Sources

| Layer | Queue or file |
| --- | --- |
| Multi-sample Qwen report | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen_multisample_visible11_probe_bdc_20260527_report.md` |
| Multi-sample materialization | `candidate_external_materialization_20260527_151130` |
| Multi-sample apply/visible | `candidate_apply_visible_queue_20260527_154713` |
| Generic probe/BDC | `generic_issue_probe_queue_20260527_154825`, `bdc_queue_20260527_154846` |
| Issue/full-package probe/BDC | `audit_probe_upgrade_queue_20260527_154942`, `bdc_queue_20260527_155027` |
| Package-integrity probe/BDC | `audit_probe_upgrade_queue_20260527_155257`, `bdc_queue_20260527_155342` |
| Rescue issue probe/BDC | `audit_probe_upgrade_queue_20260527_184019`, `bdc_queue_20260527_184051` |
| Issue/full-package certificates | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/bdc_queue_20260527_155027_certificates.jsonl` |
| Package-integrity certificates | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/bdc_queue_20260527_155342_certificates.jsonl` |
| Rescue certificates | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/bdc_queue_20260527_184051_certificates.jsonl` |

## Audit Criteria

`retain-main`: usable in the main RQ4 issue-specific table.

- Full-package or issue-code execution.
- Pass/fail split among visible-passing candidates.
- Probe tied to the public issue signal.
- No obvious environment-only or temp-path-only artifact dominates the result.

`retain-integrity`: usable in a separate full-package integrity/regression table.

- Full-package import or core API execution.
- Pass/fail split among visible-passing candidates.
- Demonstrates that visible-passing Qwen patches can damage package behavior.
- Not used as an issue-specific correctness claim.

`downgrade`: useful as supplementary stress evidence only.

- BDC exists but every candidate fails the semantic assertion.
- Behavior groups differ, but the split does not prove any candidate meets the issue behavior.

`reject-for-issue-claim`: do not use as issue-specific positive evidence.

- All candidates fail.
- Probe mainly diagnoses routing, syntax, import, or package breakage.
- May remain in the artifact as negative evidence.

## Audited Certificates

### Issue / Full-Package Layer

| Task | Probe | Candidates | Pass | Fail | Audit label | Paper use |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `mwaskom__seaborn-3190` | `upgrade-fullpkg-seaborn-continuous-bool-interval` | 2 | 0 | 2 | `downgrade` | Appendix only; all-fail divergence |
| `mwaskom__seaborn-3407` | `upgrade-fullpkg-seaborn-pairplot-multiindex` | 5 | 1 | 4 | `retain-main` | Main Qwen issue-specific case |
| `pallets__flask-5063` | `upgrade-fullpkg-flask-routes-subdomain-column` | 5 | 0 | 5 | `downgrade` | Appendix only; all-fail divergence |
| `pylint-dev__pylint-7114` | `upgrade-fullpkg-pylint-namespace-no-missing-init` | 2 | 0 | 2 | `reject-for-issue-claim` | Do not count; temp-path stdout also affects grouping |
| `scikit-learn__scikit-learn-10508` | `upgrade-fullpkg-sklearn-labelencoder-empty-transform` | 5 | 0 | 5 | `downgrade` | Appendix only; all-fail divergence |

Detailed notes:

- `mwaskom__seaborn-3407` is the strongest Qwen issue-specific certificate. One Qwen sample produces the expected pairplot axes shape; other Qwen samples and the no-op fail through distinct full-package paths.
- `mwaskom__seaborn-3190` is not a positive issue certificate because both candidate groups fail. The no-op group exposes the boolean subtraction failure, while the Qwen group breaks import behavior.
- `pallets__flask-5063` is not a positive issue certificate because the route command assertion fails for every group, although the failure modes differ.
- `pylint-dev__pylint-7114` should be excluded from issue-specific claims because both groups fail the assertion and the output includes temp-directory paths.
- `scikit-learn__scikit-learn-10508` should remain a diagnostic divergence unless a later candidate passes the LabelEncoder empty-transform semantic assertion.

### Package-Integrity Layer

| Task | Probe | Candidates | Pass | Fail | Audit label | Paper use |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `mwaskom__seaborn-3190` | `upgrade-fullpkg-integrity-seaborn-import-core` | 2 | 1 | 1 | `retain-integrity` | RQ4 partial-positive integrity evidence |
| `mwaskom__seaborn-3407` | `upgrade-fullpkg-integrity-seaborn-import-core` | 5 | 2 | 3 | `retain-integrity` | RQ4 partial-positive integrity evidence |
| `pallets__flask-5063` | `upgrade-fullpkg-integrity-flask-import-core` | 5 | 2 | 3 | `retain-integrity` | RQ4 partial-positive integrity evidence |
| `scikit-learn__scikit-learn-10508` | `upgrade-fullpkg-integrity-sklearn-preprocessing-import` | 5 | 2 | 3 | `retain-integrity` | RQ4 partial-positive integrity evidence |

Detailed notes:

- These certificates are valuable because visible-passing Qwen patches split on package import and core API sanity checks.
- They are not issue-correctness certificates. They show full-package behavioral damage or preservation in the visible-pass pool.
- They should be reported in a separate RQ4 table headed "independent-source full-package integrity BDCs."

### Qwen Issue Rescue Layer

| Task | Probe | Candidates | Pass | Fail | Audit label | Paper use |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `pylint-dev__pylint-5859` | `qwen-rescue-pylint-punctuation-note-tag` | 4 | 0 | 4 | `reject-for-issue-claim` | Negative rescue result |
| `pylint-dev__pylint-7228` | `qwen-rescue-pylint-regex-property-escape-no-traceback` | 5 | 0 | 5 | `reject-for-issue-claim` | Negative rescue result |

Detailed notes:

- The rescue probes use absolute candidate `PYTHONPATH` so child `python -m pylint` subprocesses import the candidate repository rather than missing the local package.
- The prior environment ambiguity is resolved: the probes execute against the intended candidate repos.
- The result is still all-fail. Therefore Qwen issue-specific pass/fail count remains 1, not 3-5.

## Counts For Paper Tables

| Quantity | Count |
| --- | ---: |
| Qwen model samples requested in multi-sample visible-11 run | 44 |
| Qwen model samples materialized | 29 |
| Compatible visible-pass Qwen samples | 26 |
| Tasks with compatible visible-pass Qwen samples | 9 |
| Strict visible-pass Qwen samples | 14 |
| Tasks with strict visible-pass Qwen samples | 5 |
| Generic source-isolated Qwen BDC tasks | 0 |
| Issue/full-package Qwen BDC tasks | 5 |
| Issue/full-package pass/fail Qwen BDC tasks | 1 |
| Package-integrity pass/fail Qwen BDC tasks | 4 |
| Rescue pass/fail issue-specific Qwen BDC tasks | 0 |
| Final Qwen issue-specific pass/fail BDC tasks after rescue | 1 |

## Recommended Paper Wording

Use:

"Qwen structured generation improves the independent-source candidate pool from an applicability failure into a visible-pass multi-sample pool. On the 11 tasks that reached compatible visible-pass in the frozen-30 run, four-sample generation yields 26 compatible visible-pass Qwen model candidates across 9 tasks. PatchCourt finds one issue-specific pass/fail BDC and four full-package integrity pass/fail BDCs. This is a partial-positive independent-source result: it validates the ingestion and certification pipeline and shows visible-pass full-package risk, but it does not yet establish broad issue-specific reproduction under Qwen."

Avoid:

- "Qwen reproduces the main BDC signal."
- "Qwen produces 5 issue-specific BDCs."
- "Package-integrity BDCs prove issue correctness."
- "The rescue run expanded Qwen issue-specific BDCs to 3-5."
