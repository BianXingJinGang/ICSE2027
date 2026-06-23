# Phase 27 Structured-Edit Example Report

Date: 2026-06-22.

## Objective

The user supplied an ICSE-style figure showing a JSON-like patch/edit object used as tool input and asked to add a little of that content after learning how similar papers present it. The goal was to make PatchCourt's candidate-edit representation visible without turning the manuscript into an engineering report or adding a page-expensive standalone listing.

## Corpus Signal Used

The local ICSE corpus contains the RepairAgent paper, which uses a compact tool-facing patch object as an example figure for the `write_fix` tool. The useful style signal is not the exact syntax, but the rhetorical role: a small structured record links model output to a downstream repair/evaluation tool.

## Implemented Change

- Added a compact structured-edit record strip to Figure 2, the quantified PatchCourt protocol path:
  - `edit record: {"task", "source", "edit.file", "evidence"}`
  - `candidate -> probe evidence -> frozen ledger`
- Updated the Figure 2 caption and PDF accessibility description to mention the structured-edit strip.
- Updated the Figure 1-4 generator manifest phase to `phase27_structured_edit_inset_on_quantitative_figures_1_4`.
- Synchronized the regenerated figure into the active IEEE manuscript and anonymous artifact LaTeX/figure directories.

## Rejected Alternative

A standalone code/listing-style figure was considered but not kept because it would make the paper read more like an implementation report and would push the tight submission layout toward an extra page. The final version preserves the ICSE-common method-figure vocabulary while showing the edit-record idea inside the existing protocol figure.

## Validation

- Active IEEE build: PASS, 12 pages.
- Active final LaTeX log scan: PASS, no overfull boxes, undefined citations/references, rerun prompts, LaTeX errors, emergency stops, or fatal messages.
- Visual QA: page containing Figure 2 rendered and inspected; the structured-edit strip is visible and does not overlap the quantitative panels.
- ICSE acceptance audit: PASS, `103.0/103`.
- Artifact Level 1 verifier: PASS, `44/44`.
- Artifact LaTeX rebuild: PASS, 12 pages.

## Claim Boundary

This is a presentation-only phase. No frozen empirical count, task membership, candidate/probe record, audit label, Qwen evidence, held-out result, or selected-path claim boundary changed. The `17/30` false-acceptance result remains conditional on the selected certificate-producing path.
