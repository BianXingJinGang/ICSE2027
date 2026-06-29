# Phase 33 IEEE Conference Template Format Report

Date: 2026-06-29.

## Objective

Bind the active ICSE 2027 manuscript to the user-provided IEEE conference template files while preserving the Phase 32 paper story, figures, evidence-record listing, empirical counts, and anonymous artifact checkability.

## Template Sources

- Word template archive: `C:/Users/Administrator/xwechat_files/wxid_m8xidlxvgjqp22_02f1/msg/file/2026-06/Conference-Templates-Word.zip`.
- LaTeX template archive: `C:/Users/Administrator/xwechat_files/wxid_m8xidlxvgjqp22_02f1/msg/file/2026-06/conference-latex-template_10-17-19.zip`.
- Extracted template reference directory: `paper/icse2027/assets_20260629_template_format_phase33/`.
- Supplied LaTeX class copied into the active lane: `paper/icse2027/latex_ieee_template_20260629/IEEEtran.cls`.

## Output Locations

- Active template-bound LaTeX lane: `paper/icse2027/latex_ieee_template_20260629/`.
- Submission PDF copy: `paper/icse2027/submission_20260629_ieee_template/patchcourt_icse2027_research_track_submission_20260629_ieee_template.pdf`.
- Artifact LaTeX copy: `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/latex/`.
- Acceptance audit: `paper/icse2027/assets_20260629_template_format_phase33/phase33_ieee_template_acceptance_audit_20260629.md`.

## Format Changes

- Changed the active manuscript lane to `\documentclass[conference]{IEEEtran}`.
- Added `\IEEEoverridecommandlockouts`.
- Copied the provided `IEEEtran.cls` into the active LaTeX lane and the anonymous artifact LaTeX lane.
- Aligned the preamble with the supplied conference template package pattern: `cite`, `amsmath`, `amssymb`, `amsfonts`, `graphicx`, `textcomp`, and `xcolor`, while retaining paper-required table/listing packages.
- Preserved light float-spacing controls from the prior submission lane so the template-bound build remains 12 pages without changing page margins, column width, font size, or document class.
- Changed the abstract phrase `held-out FAIL_TO_PASS tests` to `held-out issue tests` to avoid fragile underscore handling in the IEEE template path.

## Scientific Boundary

This phase is a presentation and packaging phase only. It does not change:

- the selected certificate-producing path estimand,
- the 50-task pilot and 200 candidate slots,
- the 68 visible-passing candidates,
- the 37 raw certificates,
- the 30 frozen audit records,
- the `17/30` false-acceptance result,
- the `26/30` specification-debt result,
- the `6/10` issue/full-package upgrade result,
- the `6/10` extra full-package probe result,
- the Qwen boundary/stress-evidence framing.

## Validation

- Active template-bound LaTeX build: PASS.
- Final active log scan: no overfull boxes, undefined citations, undefined references, rerun prompts, LaTeX errors, emergency stops, or fatal messages.
- Page count: 12 pages.
- Page size: Letter, 612 x 792 pt.
- Visual render QA: checked pages 1, 2, 3, 11, and 12 after rendering with Poppler; no broken figures, missing captions, obvious overflow, or final-page truncation was observed.
- Artifact LaTeX source was synchronized to the same template-bound `main.tex`, `references.bib`, `IEEEtran.cls`, figures, and PDF.
- Artifact Level 1 verifier: PASS after the template sync.
- Critical artifact source secret/path scan: PASS after removing LaTeX build temporaries from the package directory.
- ICSE acceptance audit: `103.0/103`, decision `ready_for_final_polish`.

## Fingerprints

- `main.tex` SHA256: `3A9729D4400BE0435E5EE5C1003CC2AD39671313E9635D0CD612A4299407E07A`.
- `IEEEtran.cls` SHA256: `C972ACA108FDA004C3514D63658E02816DA2E54D9A1451E870B9BD970E003F55`.
- submission PDF SHA256: `15CA325914DD287342066C81140577E4FFD677D84C23F85F768B48CA2C1630E0`.

## Remaining Non-Format Risk

The largest scientific limitation remains the same as Phase 32: the main empirical estimate is conditional on the selected certificate-producing path rather than a population-wide acceptance-rate estimate. The template migration keeps that boundary explicit in the abstract, introduction, results, and threats.
