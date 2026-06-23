# PatchCourt Anonymous Inspect-Only Artifact Bundle

The package root is the submission-facing artifact bundle root. It keeps the small anonymous control files in source control and can build an inspect-only package from the paper-facing result tables, reports, figures, and scripts.

## Purpose

The artifact supports inspection and table regeneration for:

- candidate metadata,
- visible-test outcomes,
- probe outcomes,
- behavior-disagreement certificates,
- manual audit labels,
- frozen certificate index,
- held-out calibration,
- pilot-50 drop reasons,
- selection-funnel and route-stability transparency checks,
- paper tables and figures,
- Phase 27 structured-edit inset on the quantified protocol figure,
- Phase 28 abstract sample framing and compact edit-record code block,
- quantitative Figure 1-4 redesign assets,
- redesigned Figures 1-4 generated for the submission-facing paper,
- quantitative statistical figures generated from the frozen paper tables.

PatchCourt is an audit and triage protocol, not a correctness oracle. The artifact is designed to make that boundary visible.

## Bundle Levels

| Level | Description | Requires Model Access |
| --- | --- | --- |
| 0 | Inspect frozen tables, reports, certificates, and audit labels | No |
| 1 | Regenerate and verify paper headline counts, pilot-50 drop reasons, selection-funnel values, and route-stability values from packaged CSV/JSONL/Markdown files with `python scripts/verify_level1_tables_20260528.py` | No |
| 2 | Replay selected probes against existing candidate worktrees | No model, Linux runtime required |
| 3 | Regenerate candidates and rerun the full pipeline | Yes or staged local weights |

## Required Files To Package

See `MANIFEST.md` for the file list, `CLAIM_BOUNDARIES.md` for what each evidence type supports, and `BUILD_AND_SCAN.md` for the packaging and scan policy.

The current generated inspect-only archive is:

- `patchcourt_icse2027_anonymous_inspect_only_20260623_abstract_example.zip`

## Anonymization Rules

- Remove passwords, API keys, cookies, private keys, and transient authentication material.
- Replace user-specific absolute paths with `<ARTIFACT_ROOT>` or `<REMOTE_ROOT>`.
- Preserve queue IDs because they are needed for auditability.
- Preserve model aliases and endpoint shape, but do not include secrets.
