# Phase 31 Subject-Aligned Patch Record Report

Date: 2026-06-28

## User Request

The user reviewed the Phase 30 structured patch-record listing and said it was still too empty and needed to better fit the paper's main thesis.

## Manuscript Change

- Revised the structured listing in the PatchCourt overview so it is no longer a generic patch schema.
- The listing now uses the Matplotlib all-NaN bar-plot running case, the same case already used to introduce visible-pass behavioral disagreement.
- The record now binds the executable edit to the paper's evidence chain:
  - `visible`: the candidate reaches visible-test pass status,
  - `probe`: the full-package public probe splits the visible-pass pool,
  - `certificate`: the split is recorded as a pass/fail behavior-disagreement certificate,
  - `audit`: the certificate is retained and carries specification-debt evidence,
  - `held_out`: post-freeze calibration marks the selected record as false acceptance.
- The surrounding overview text and caption were rewritten so the figure directly supports the paper's core claim: visible-test acceptance is not an oracle.

## Page-Budget Repair

- A more verbose subject-aligned version pushed the paper to 13 pages.
- The final version keeps the evidence chain but flattens the JSON object and shortens the caption.
- The active submission PDF is back to 12 pages.

## Validation

- Active IEEE LaTeX build: PASS, 12 pages.
- Final LaTeX log scan: PASS, with no overfull boxes, undefined citations/references, rerun prompts, LaTeX errors, emergency stops, or fatal messages.
- Visual QA: rendered and inspected page 2, where the running-example figure and subject-aligned patch record appear together.
- Artifact LaTeX rebuild: PASS, 12 pages.
- Artifact Level 1 verifier: PASS, 44/44 checks.
- ICSE acceptance audit: 103.0/103, `ready_for_final_polish`.

## Claim Boundary

This is a presentation-only phase. It improves how the structured patch record supports the visible-test false-acceptance story, but it does not change frozen empirical counts, task membership, candidate/probe records, audit labels, Qwen evidence, held-out calibration outcomes, or selected-path claim scope. The `17/30` false-acceptance result remains conditional on the selected certificate-producing path.
