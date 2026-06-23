# Anonymous Artifact Appendix Draft 2026-05-28

This appendix is written in double-blind style. Paths are expressed as artifact-relative placeholders. The local repository keeps concrete paths for execution, but the submitted artifact should replace user-specific paths with `<ARTIFACT_ROOT>`.

## Artifact Purpose

The artifact allows reviewers to audit PatchCourt's evidence chain from public issue inputs to candidate patches, visible-test outcomes, probe outcomes, behavior-disagreement certificates, frozen audit indices, and post-freeze held-out calibration.

PatchCourt is not an oracle. The artifact is designed to make that limitation inspectable: every result records whether it is source-isolated, issue-code, full-package, package-integrity, or held-out.

## Gold Boundary

Before the freeze point, the pipeline may use:

- Public issue text.
- Public repository snapshots.
- Public issue snippets or reproducer text.
- Candidate diffs generated from public inputs.
- Visible commands derived from the public benchmark setup.

Before the freeze point, the pipeline must not use:

- Developer patch.
- Test patch.
- FAIL_TO_PASS labels.
- PASS_TO_PASS labels.
- Held-out test outcomes.

Freeze point:

- `<ARTIFACT_ROOT>/server_analysis_workspace/patchcourt_4gpu_smoke_20260524/audit_30plus_20260526/frozen_post_audit_20260526/frozen_certificate_index_20260526.json`

After the freeze point:

- Held-out calibration reads evaluation-only labels and records whether visible/probe-accepted candidates fail FAIL_TO_PASS.

## Directory Map

| Artifact-relative path | Purpose |
| --- | --- |
| `scripts/` | PatchCourt workers and materializers |
| `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/` | Local launchers, reports, result tables, and downloaded summaries |
| `paper/icse2027/assets_20260527/` | Initial paper assets: intervals, figures, cases, artifact note |
| `paper/icse2027/assets_20260528/` | Audited Qwen evidence, main-table plan, polished cases, anonymous appendix, updated figures |
| `docs/RESTART.md` | First-stop restart file for reproducing the current state |
| `WORKLOG.md` | Append-only execution history |
| `DECISIONS.md` | Project and claim decisions |
| `NEXT_STEPS.md` | Operational queue of remaining work |

Remote execution root used during this study:

- `<REMOTE_ROOT>`

The submitted artifact should not require reviewers to use this exact path. It should provide a configuration variable such as `PATCHCOURT_REMOTE_ROOT`.

## Core Evidence Files

| Evidence | File |
| --- | --- |
| Main results report | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/main_results_report_20260526.md` |
| Held-out table | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table1_heldout_false_acceptance_20260526.csv` |
| Main upgraded probes | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table2_upgraded_probe_20260526.csv` |
| Correlation table | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table3_correlation_20260526.csv` |
| Rerank table | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table4_rerank_20260526.csv` |
| Abstain table | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table5_abstain_20260526.csv` |
| Extra full-package probes | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table6_extra_full_package_probe_20260526.csv` |
| Qwen structured frozen-30 report | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen_structured_frozen30_20260527_report.md` |
| Qwen multi-sample report | `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen_multisample_visible11_probe_bdc_20260527_report.md` |
| Qwen BDC audit | `paper/icse2027/assets_20260528/qwen_bdc_audit_20260528.md` |
| Rendered figures | `paper/icse2027/assets_20260528/figures/*.mmd`, `*.svg`, `*.pdf` |

## Reproduction Levels

Level 0: inspect-only reproduction.

- Read frozen tables, certificate JSONL, audit labels, and reports.
- No GPU or external model required.
- Expected time: minutes.

Level 1: local table regeneration.

- Rebuild paper-facing summaries from existing local JSON/CSV files.
- Requires Python and standard packages available in the repository environment.
- Does not regenerate candidate patches.

Level 2: remote probe replay.

- Re-run selected probe queues against already materialized candidate worktrees.
- Requires access to a Linux host with the task-specific runtimes.
- Does not regenerate model outputs.

Level 3: end-to-end candidate regeneration.

- Re-run candidate materialization, apply/visible, probes, BDC builder, ledger, and held-out calibration.
- Requires model access or staged local weights.
- Expected to be the most expensive and least deterministic layer.

## Qwen Independent-Source Configuration

The current independent model source is:

- Backend: OpenAI-compatible local endpoint.
- Endpoint shape: `http://127.0.0.1:<PORT>/v1`.
- Model alias used in records: `qwen2.5-coder-7b-instruct-q4_k_m`.
- Generation format: structured search/replace with programmatic diff export.

Do not include secrets in the artifact. Endpoint URLs, ports, and model aliases are configuration metadata; API keys, tokens, passwords, and cookies are excluded.

## Claim Boundary Data Card

| Claim | Data required | Current status |
| --- | --- | --- |
| Visible acceptance often becomes held-out false acceptance | Frozen 30 held-out table | Supported: 17/30 |
| Full-package probes preserve signal | Main and extra upgrade tables | Supported for selected targets |
| PatchCourt is useful for triage | Correlation, rerank, abstain tables | Preliminary |
| Qwen is a real independent source | Qwen structured materialization/apply/visible records | Supported |
| Qwen broadly reproduces issue-specific BDCs | Multiple issue-specific Qwen pass/fail BDCs | Not supported; only 1 task |
| Qwen reveals independent full-package risk | Package-integrity BDC table | Supported as separate integrity evidence |

## Double-Blind Notes

The submitted artifact should:

- Remove machine-specific usernames from paths.
- Remove any jump-host topology, passwords, tokens, cookies, and private keys.
- Use neutral wording such as "the authors" only where needed.
- Preserve queue IDs because they are essential for auditability and do not identify the authors by themselves.
- Include exact commit hash and environment manifests in the final camera-ready artifact if policy allows.

## Minimal Reviewer Walkthrough

1. Inspect `docs/RESTART.md` for the latest queue IDs and claim boundaries.
2. Open `paper/icse2027/assets_20260528/main_tables_20260528.md`.
3. Verify Table 1 against `table1_heldout_false_acceptance_20260526.csv`.
4. Verify Table 2 and Table 3 against the upgraded-probe CSV files.
5. Verify Qwen counts against `qwen_multisample_visible11_probe_bdc_20260527_report.md`.
6. Verify Qwen audit labels against `qwen_bdc_audit_20260528.md` and the three certificate JSONL files.

## Known Non-Reproduced Pieces

- A second strong independent model source is not staged in the current artifact.
- Qwen issue-specific pass/fail BDC yield remains 1 task after the rescue attempt.
- PASS_TO_PASS regression execution is recorded as counts in the held-out table but is not yet a first-class regression outcome table.
- Mermaid figure sources are available and were rendered to SVG/PDF on 2026-05-28. Final camera-ready sizing should still be checked against the ICSE template.
