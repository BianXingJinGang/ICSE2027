# Artifact Build and Scan Notes

Date: 2026-06-29.

The inspect-only artifact is curated from paper-facing assets, result tables, selected reports, figure sources, and scripts. It intentionally excludes raw local restart logs that contain machine-specific paths or operational connectivity details.

## Build Layout

Target directory:

- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/`

Archive:

- `paper/icse2027/artifact_bundle_anonymous_20260528/patchcourt_icse2027_anonymous_inspect_only_20260629_corecode.zip`

Current generated package:

- Files in inspect-only directory: 133.
- The archive is rebuilt from this directory after the Level 1 verifier and secret/anonymity scan pass. Exact archive bytes and SHA256 are recorded in the outer `SECRET_SCAN_REPORT_20260528.md` after rebuild to avoid self-referential hash drift inside the ZIP.

Included categories:

- Anonymous README, manifest, claim boundaries, and anonymous restart summary.
- Main result tables from `main_results_20260526/`.
- Paper-facing table packs, safe-route characterization files, Qwen audit, related-work source notes, and polished cases.
- Pilot-50 drop-reason table, selection-funnel table, and route-stability table.
- Current main-paper figure PDFs, the Phase 26 quantitative Figure 1-4 redesign assets with the Phase 27 structured-edit inset, the Phase 32 core-claim PatchCourt code record in LaTeX, figure provenance inputs, and the 2026-06-22 quantitative chart pack.
- Active IEEE LaTeX source, BibTeX, PDF, and build README.
- Phase 2 reference/anonymity/PDF integrity report and Phase 3 acceptance-gauntlet repair reports.
- Selected table-builder scripts plus `scripts/verify_level1_tables_20260528.py` for Level 1 headline-count, pilot-50, selection-funnel, and route-stability regeneration/comparison.

Level 1 self-check command from the inspect-only package root:

```bash
python scripts/verify_level1_tables_20260528.py
```

Latest Level 1 self-check:

- Status: PASS.
- Recomputed and matched 44 checks: `17/30` false acceptance, `26/30` specification debt, source/probe/candidate-source stratification, `6/10` main upgraded pass/fail BDCs, `6/10` extra full-package pass/fail BDCs, `1` Qwen issue-specific pass/fail BDC, `4` Qwen package-integrity pass/fail BDCs, 50-task pilot drop-reason counts, selection-funnel values, and route-stability values.
- Report: `docs/LEVEL1_TABLE_REGENERATION_REPORT_20260528.md`.
- Machine-readable summary: `generated/level1_table_recheck_20260528.json`.

## Scan Scope

The scan checks the curated artifact directory and archive input files for:

- Literal shared-password substrings from the working thread.
- Private-key markers.
- Common token or API-key assignment patterns.
- Author-identifying Windows user paths.
- Known jump-host or local machine identifiers.

Credential words that appear only in policy text, such as "do not include passwords", are not treated as secret leaks.

Latest scan result:

- No literal shared passwords, private-key markers, or author-identifying Windows paths were found.
- Raw remote-root paths in copied evidence were replaced with `<REMOTE_ROOT>` inside the package copy.
- Environment variable names such as `OPENAI_API_KEY`, `HF_TOKEN`, and `HUGGINGFACE_HUB_TOKEN` remain in scripts as configuration names, not secret values.
- The string `hf_router_chat` is a backend name and can match broad token-prefix scans; it is not a credential.
- The exact Phase 32 rebuilt ZIP is extracted into a clean-room directory during final validation; Level 1 verification and LaTeX rebuild both pass.
- The Phase 32 critical secret/path scan passes on both the curated artifact directory and ZIP bytes after separating real token forms from benign task/probe names such as `flask-*`.
