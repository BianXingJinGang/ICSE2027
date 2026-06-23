# Phase 28 Abstract Sample Framing And Example Block Report

Date: 2026-06-23.

## Objective

The user raised two submission-facing issues:

1. The abstract still appeared to emphasize a sample size of 30.
2. The paper needed an explicit example code block, not only a figure inset, for the structured edit record.

## Decision

The abstract should not inflate the calibrated denominator beyond the validated evidence. The scientifically safe framing is:

- name the broader pilot and candidate volume: 50 tasks, 200 candidate slots, 68 visible-passing candidates, and 37 raw certificates;
- keep the calibrated false-acceptance denominator as 30 conservative task-level audit records;
- keep `17/30` and `26/30` conditional on the selected certificate-producing path.

This makes the scale visible without converting a selected-path calibration result into a benchmark-wide rate.

## Implemented Changes

- Rewrote the abstract scale sentence to include the 50-task pilot, 200 candidate slots, 68 visible-passing candidates, and 37 raw certificates before the 30-record conservative selected path.
- Added a compact three-line structured edit-record code block in the PatchCourt overview:
  - task id,
  - source,
  - edited file/replacement,
  - visible/probe evidence state.
- Kept the code block unnumbered and compact to avoid adding a page or turning the paper into an implementation report.

## Validation

- Active IEEE build: PASS, 12 pages.
- Active final LaTeX log scan: PASS, no overfull boxes, undefined citations/references, rerun prompts, LaTeX errors, emergency stops, or fatal messages.
- Visual QA: pages containing the code block and Figure 2 rendered and inspected; no overlap or clipping found.
- ICSE acceptance audit: PASS, `103.0/103`.

## Claim Boundary

This is a presentation and wording phase only. No empirical count, task membership, candidate/probe record, audit label, Qwen evidence, held-out result, or selected-path claim boundary changed. The primary false-acceptance result remains `17/30` over the selected certificate-producing path.
