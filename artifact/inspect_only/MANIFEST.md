# Root Manifest

This root index makes the inspect-only package self-contained for artifact reviewers.

## Directories

- `certificates/`: frozen certificate and behavior-disagreement records used by the paper-facing audit index.
- `docs/`: artifact documentation, claim boundaries, Level 1 report, build/scan notes, and the detailed manifest.
- `figures/`: rendered paper figures, quantitative Figure 1-4 copies, the Phase 27 structured-edit inset manifest, figure sources, and the 2026-06-22 quantitative chart pack.
- `generated/`: generated Level 1 recheck output.
- `latex/`: anonymous IEEE manuscript source, bibliography, rendered PDF, and figure copies needed for source rebuild.
- `reports/`: paper-facing result, Qwen boundary, audit, and package reports.
- `scripts/`: lightweight artifact verifier.
- `tables/`: packaged CSV/JSON/Markdown tables used by the verifier and manuscript.

## Reviewer Entry Points

- Read `docs/README.md` for artifact scope and levels.
- Run `python scripts/verify_level1_tables_20260528.py` for the Level 1 table-regeneration check.
- Inspect `docs/CLAIM_BOUNDARIES.md` before interpreting Qwen, package-integrity, or selected-path results.
- Build `latex/main.tex` if source-level manuscript reproduction is desired.
- Inspect `figures/phase26_quant_figures_1_4_manifest_20260622.json` to map the quantitative Figures 1-4 to their paper roles; its phase records the Phase 27 structured-edit inset in Figure 2.
- Inspect `figures/phase25_figures_1_4_manifest_20260622.json` only for historical Phase 25 figure provenance.
- Inspect `figures/patchcourt_quantitative_figure_manifest_20260622.json` to map the new statistical figures to their source tables.
- Inspect `reports/phase31_subject_aligned_patch_record_report_20260628.md` to see how the standalone listing now supports the Matplotlib false-acceptance evidence chain rather than a generic patch schema.
- Inspect `reports/phase32_core_claim_code_record_report_20260629.md` to see how Figure 2 now names the core PatchCourt evidence object directly.

The detailed source-to-package manifest remains in `docs/MANIFEST.md`.
