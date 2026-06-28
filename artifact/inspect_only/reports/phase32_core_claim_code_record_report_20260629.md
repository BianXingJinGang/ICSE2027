# Phase 32: Core-Claim Code Record

Date: 2026-06-29

## Objective

Revise the paper's code/listing figure so that it directly represents the paper's core evidence object rather than reading as a generic patch or edit schema.

## Manuscript Change

- Updated Figure 2 in `paper/icse2027/latex_ieee_20260529/main.tex`.
- Replaced the previous patch-shaped JSON record with a compact PatchCourt evidence record.
- The listing now explicitly exposes:
  - `claim`: `visible_pass_is_not_oracle`
  - `accepted_by`: visible-test pass
  - `pre_freeze`: public-probe behavior split and `pass_fail_bdc`
  - `audit`: retained specification-debt risk
  - `post_freeze`: held-out failure and false-acceptance outcome
  - `review_action`: inspect or rerank before acceptance
- Rewrote the surrounding paragraph and caption so the figure is tied to false acceptance, pre-freeze evidence, and post-freeze calibration.

## Validation

- Rebuilt the active IEEE manuscript with `pdflatex`, `bibtex`, `pdflatex`, `pdflatex`.
- Active PDF remains 12 pages.
- Final LaTeX log scan found no overfull boxes, undefined references, undefined citations, LaTeX errors, emergency stops, or fatal errors.
- Rendered page 2 for visual QA; Figure 2 is readable in the right column and does not disrupt the page flow.
- Ran ICSE acceptance audit:
  - score: `103.0/103`
  - decision: `ready_for_final_polish`

## Current Artifacts

- Active source: `paper/icse2027/latex_ieee_20260529/main.tex`
- Active PDF: `paper/icse2027/latex_ieee_20260529/main.pdf`
- Submission PDF: `paper/icse2027/submission_20260629_corecode/patchcourt_icse2027_research_track_submission_20260629_corecode.pdf`
- Acceptance audit: `paper/icse2027/assets_20260629_core_claim_code_record/phase32_core_claim_code_record_acceptance_audit_20260629.md`

## Hashes

- `main.tex` SHA256: `2CFC69FC062FA870A539E3AAA5CC83EFC5017DC522440CEAEF25723536458827`
- `main.pdf` SHA256: `47829CC173D0A535F71DBAE3589EE56A0465EAB07B749F0F0575995B69D5718D`
- submission PDF SHA256: `47829CC173D0A535F71DBAE3589EE56A0465EAB07B749F0F0575995B69D5718D`

## Claim Boundary

This is a presentation and reviewer-comprehension revision only. It changes no candidate generation, no visible/probe execution, no certificate audit labels, no held-out calibration labels, and no quantitative claims. The headline empirical statements remain conditional on the selected certificate-producing path.
