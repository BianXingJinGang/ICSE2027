# Phase 3 Reviewer Kill-Shot Repair Report (2026-05-29)

## Objective

Clear reviewer kill-shot risks that could make the paper look overclaimed or under-anchored:

- proof/guarantee/correctness/oracle wording,
- RQ claims without explicit table/figure/case anchors,
- weak related-work boundary against PatchDiff, SWE-bench correctness, and APR overfitting.

## Inputs

- Active IEEE manuscript: `paper/icse2027/latex_ieee_20260529/main.tex`
- Pre-repair audit: `paper/icse2027/assets_20260529/phase3_pre_repair_acceptance_audit_20260529.md`
- Post-repair audit: `paper/icse2027/assets_20260529/phase3_post_repair_acceptance_audit_20260529.md`

## Repairs Applied

### Claim Boundary

- Added an abstract-level boundary: PatchCourt does not guarantee patch correctness and does not prove that a patch is wrong.
- Added a construct-validity boundary: a certificate is not a guarantee of incorrectness; it is an executable reason to inspect acceptance risk.
- Replaced stronger wording such as treating PatchCourt as a `correctness oracle` with the weaker phrase `correctness judge`.

### RQ Anchors

- Finding 1 now explicitly points to Table `\ref{tab:heldout}`.
- Finding 2 now explicitly points to Table `\ref{tab:upgrades}`.
- Finding 3 now explicitly points to Table `\ref{tab:triage}`.
- Finding 4 now explicitly points to Table `\ref{tab:claim-boundary}`.
- The qualitative-case section now connects the case narratives back to Tables `\ref{tab:heldout}`--`\ref{tab:claim-boundary}` and artifact certificate evidence.

### Related Work Wedge

- APR overfitting: clarified that PatchCourt does not rediscover plausible-patch overfitting; the contribution is the timing and evidence boundary for repository-level LLM visible-pass acceptance.
- PatchDiff/SWE-bench correctness: sharpened the distinction between retrospective correctness analysis after labels/gold patches are available and PatchCourt's weaker but earlier pre-freeze risk audit.
- Generated tests/oracles: preserved the explicit position that probes are evidence-producing instruments, not truth.

## Audit Result

ICSE acceptance audit:

- Before repair: `96/103` (`93.2%`), warnings on inflated language and table/figure anchors.
- After repair: `103/103` (`100.0%`), no heuristic warnings.

Post-repair key lines:

- `inflated_language`: PASS, `risky_terms=3; protective_boundaries=5`.
- `table_figure_anchors`: PASS, `11 table/figure reference signals found`.

## Build Validation

Command sequence:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Validation:

- PDF: `paper/icse2027/latex_ieee_20260529/main.pdf`
- Page count: `7`
- Undefined citations/references: none detected in final `main.log`.
- Overfull boxes: none detected in final `main.log`.
- Remaining log noise: underfull boxes only.

## Current Hashes

- `main.pdf`: `6FD5E6E7B0B6B03B75BB2A0E2320C9D694CAF507444DC2223A899364694F1498`
- `main.tex`: `2D2E0E2D35397D3E8A721B54F0EFC72D333F788141856DDE24D8FADF0AC6F856`
- `references.bib`: `030939A94CF60FE23AD689EC57C14FED877D9366E7D7ECC9740C3353DBC02A30`

## Phase 3 Result

PASS. The paper is now less vulnerable to the main reviewer kill-shots: overclaiming, unanchored RQ claims, and vague related-work differentiation.
