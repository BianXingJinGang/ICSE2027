# PatchCourt ICSE 2027 Inspect-Only Artifact

This anonymous package is the reviewer entry point for checking the paper's frozen evidence chain. It supports inspection and Level 1 table regeneration without external model access.

## Quick Checks

From this directory, run:

```bash
python scripts/verify_level1_tables_20260528.py
```

The verifier recomputes the headline table counts, selection funnel, route-stability values, and pilot-50 drop-reason checks from packaged CSV, JSON, JSONL, and Markdown files.

## Start Here

- `MANIFEST.md`: root map of the package.
- `docs/README.md`: artifact purpose, levels, and anonymization rules.
- `docs/MANIFEST.md`: detailed source-to-package manifest.
- `docs/CLAIM_BOUNDARIES.md`: what each evidence type supports and does not support.
- `docs/LEVEL1_TABLE_REGENERATION_REPORT_20260528.md`: latest packaged Level 1 verification report.
- `latex/main.pdf`: anonymous paper PDF copy.
- `latex/figures/`: figure PDFs needed to rebuild `latex/main.tex` from inside the package.
- `figures/phase26_quant_figures_1_4_manifest_20260622.json`: source-to-role map for the quantitative Figures 1-4; the manifest phase records the Phase 27 structured-edit inset added to Figure 2.
- `figures/phase25_figures_1_4_manifest_20260622.json`: historical source-to-role map for the prior upgraded Figures 1-4.
- `figures/patchcourt_quantitative_figure_manifest_20260622.json`: source-to-chart map for the quantitative figure pack.
- `reports/phase31_subject_aligned_patch_record_report_20260628.md`: explains the subject-aligned Matplotlib ledger record added to the manuscript.

PatchCourt is an audit and triage protocol, not a correctness oracle. The artifact is organized to make the selected certificate-producing path, candidate provenance, probe provenance, audit decisions, and post-freeze calibration inspectable.
