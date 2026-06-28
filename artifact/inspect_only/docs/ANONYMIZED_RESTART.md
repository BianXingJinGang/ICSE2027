# Anonymous Restart Summary

Last updated: 2026-06-28.

This file is the artifact-facing restart summary. It removes local usernames, passwords, jump-host details, and machine-specific paths while preserving the evidence chain needed for review.

## Objective

Prepare an ICSE 2027 double-blind submission for PatchCourt, a gold-boundary-aware audit protocol for visible-test false acceptance in repository-level LLM repair.

## Main Validated Results

- Frozen audit set: 30 conservative certificates.
- Manual audit: 22 retain, 8 downgrade, 0 reject.
- Held-out calibration: 30/30 executable.
- Held-out false acceptance: 17/30.
- Specification-debt signal: 26/30.
- Main upgraded full-package/issue-code probes: 6/10 pass/fail BDC tasks.
- Extra full-package probes: 7/10 BDC tasks, including 6/10 pass/fail BDC tasks and 1/10 all-fail divergence task.
- Selection boundary: the headline rate is for the selected certificate-producing path, not for all SWE-bench tasks or all visible-passing patches.
- Pilot-50 drop-reason table: 27/50 pilot tasks enter the frozen 30, 1/50 remains only as a broad all-fail disagreement record, and 22/50 do not reach the conservative certificate index.
- Quantitative figure pack: 8 statistical figures generated from frozen paper tables; the main PDF includes the compact 4-panel quantitative summary.
- Phase 27 structured-edit inset: Figure 2 includes a compact JSON-like edit-record strip that shows how candidate edits are represented before probe evidence and ledger freeze. This is presentation-only and does not change any count, task membership, or claim boundary.
- Phase 28 abstract/example block: the abstract now names the broader pipeline scale (50 tasks, 200 candidate slots, 68 visible-pass candidates, 37 raw certificates) while retaining the 30-record calibrated selected path; the PatchCourt overview includes a compact edit-record code block. This is presentation-only.
- Phase 30 structured patch-record listing: the compact edit-record block is replaced by a formal single-column listing with `file_path`, `insertions`, `deletions`, and `modifications` fields. This is presentation-only and does not change any count, task membership, or claim boundary.

## Independent-Source Stress Test

- Independent model source: Qwen2.5-Coder-7B served through a local OpenAI-compatible endpoint.
- Direct unified-diff prompting is a negative applicability baseline: 28/30 raw diffs, 0/28 strict raw apply, 6/28 normalized/applyable, 1/30 visible-pass, 0 BDC.
- Structured search/replace frozen-30 run: 17/30 materialized/applyable, 11/30 compatible visible-pass, 6/30 strict visible-pass, 0 BDC.
- Structured visible-pass multi-sample run: 29/44 materialized samples, 26 compatible visible-pass samples across 9 tasks, 14 strict visible-pass samples across 5 tasks.
- Qwen issue/full-package audit: 5 BDC tasks, only 1 pass/fail issue-specific task.
- Qwen package-integrity audit: 4 pass/fail BDC tasks, reported separately from issue correctness.
- Qwen rescue run: 2 all-fail Pylint BDCs and 0 additional issue-specific pass/fail tasks.

## Claim Boundaries

Claimable:

- PatchCourt has a working gold-boundary-aware certificate and calibration pipeline.
- The frozen audit set shows substantial held-out false acceptance: 17/30.
- Full-package/issue-code upgrades preserve pass/fail BDC evidence for selected targets.
- Qwen validates independent-source ingestion and yields bounded nonzero disagreement evidence.

Not claimable:

- PatchCourt is not a correctness oracle.
- The 30-task rate is not a benchmark-wide population estimate.
- Qwen does not broadly reproduce issue-specific BDCs; the issue-specific pass/fail count remains 1.
- Package-integrity BDCs are not issue-correctness evidence.
- All-fail divergences are not pass/fail BDC yield.

## Artifact Structure

- `tables/`: paper-facing CSV/JSON/Markdown summaries.
- `tables/pilot50_drop_reasons_20260529.*`: 50-task pilot path and drop-reason table.
- `tables/selection_funnel_20260529.*` and `tables/route_stability_20260529.*`: reviewer-facing transparency tables checked by Level 1.
- `figures/`: Mermaid sources, rendered SVG/PDF figures, quantitative Figure 1-4 copies with the Phase 27 structured-edit inset, and the 2026-06-22 quantitative chart pack.
- `figures/phase26_quant_figures_1_4_manifest_20260622.json`: source-to-figure map for the quantitative Figure 1-4 set; its phase records the Phase 27 structured-edit inset.
- `figures/patchcourt_quantitative_figure_manifest_20260622.json`: source-to-chart map for the quantitative chart pack.
- `reports/`: selected paper-facing reports and audit notes.
- `scripts/`: table-building and characterization scripts that operate on existing result files.
- `ANONYMIZED_RESTART.md`: this restart summary.
- `CLAIM_BOUNDARIES.md`: double-blind claim boundary card.

## Validation Status

- The active LaTeX submission draft is the IEEEtran lane copied into `latex/` inside this artifact package.
- The active PDF is 12 pages after the Phase 30 structured patch-record update, with an expanded 66-reference bibliography, a Running Example code panel, and a compact quantitative result summary.
- The latest acceptance audit reports 103/103 with no heuristic warnings.
- The Level 1 verifier now checks 44 metrics, including headline counts, source/probe stratification, pilot-50 drop reasons, selection-funnel values, and route-stability values.
- The inspect-only artifact package is curated rather than a raw repository dump.
- The artifact scan excludes literal shared passwords/private keys and flags author-identifying paths if they appear.
