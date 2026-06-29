# Phase 35 Final Figure, Code, and Conclusion Polish

Date: 2026-06-29

## User request

The user requested a final full-paper polish after reviewing the Phase 34 PDF:

- add more code-style evidence blocks because other ICSE-style papers often show code in several places;
- re-check template/format consistency;
- fix the quantitative figure issue where the route-stability legend visually interfered with Panel C;
- rewrite the conclusion so it reads like a real conclusion:
  - what the paper did,
  - method flow,
  - main results,
  - outlook;
- comprehensively polish the manuscript without changing the empirical claim boundary.

## Manuscript changes

- Added a third code-facing evidence block:
  - existing Figure 2 remains the core PatchCourt evidence record;
  - existing Figure 4 remains the two-panel SymPy and Seaborn/Qwen public-probe card;
  - new Figure 8 adds a compact Django-16873 full-package public-probe card in the qualitative case section.
- Rewrote the Discussion and Conclusion into four paper-facing paragraphs:
  - visible-test false acceptance as the studied failure mode;
  - PatchCourt method flow from candidate filtering to pre-freeze certificates and post-freeze calibration;
  - headline results on the selected certificate-producing path;
  - operational outlook for inspection, reranking, abstention, broader tasks, more model sources, and multi-rater audit.
- Compressed repeated qualitative-case, related-work, threats, and artifact prose to keep the PDF at 12 pages.
- Regenerated the quantitative figure pack after moving the route-stability legend out of the Panel C bar area.
- Sanitized an old Phase 33 artifact report that contained collaborator-side local template archive paths.

## Final active package

- Active source: `paper/icse2027/latex_ieee_template_20260629/main.tex`
- Active PDF: `paper/icse2027/latex_ieee_template_20260629/main.pdf`
- Submission PDF: `paper/icse2027/submission_20260629_phase35/patchcourt_icse2027_research_track_submission_20260629_phase35.pdf`
- Anonymous ZIP: `paper/icse2027/artifact_bundle_anonymous_20260528/patchcourt_icse2027_anonymous_inspect_only_20260629_phase35.zip`
- Acceptance audit: `paper/icse2027/assets_20260629_phase35_final_polish/phase35_acceptance_audit_20260629.md`
- Secret/path scan: `paper/icse2027/assets_20260629_phase35_final_polish/phase35_secret_path_scan_20260629.txt`
- Clean-room Level 1 output: `paper/icse2027/assets_20260629_phase35_final_polish/phase35_cleanroom_level1_output_20260629.txt`
- Clean-room PDF info: `paper/icse2027/assets_20260629_phase35_final_polish/phase35_cleanroom_pdfinfo_20260629.txt`

## Hashes

- `main.tex` SHA256: `FE9370B43388F84140CD8523A102231817296AE5CE047BDA0019C3D515CDBF80`
- active/submission PDF SHA256: `ACD00E90E8A14AB2C1BECD5EDBAC46665C2E49E612EB7CA08498BB27D56836C3`
- anonymous ZIP SHA256: verify from the distributed ZIP externally; this artifact copy does not embed a self-referential ZIP hash.

## Validation

- Active IEEE template build: PASS, 12 pages, Letter page size.
- Final active LaTeX log scan: PASS; no overfull boxes, undefined citations/references, rerun prompts, fatal errors, emergency stops, or LaTeX errors.
- Visual PDF QA: PASS on:
  - quantitative summary page with fixed Panel C legend,
  - Django code-card page,
  - conclusion/references transition page,
  - final references page.
- ICSE acceptance audit: PASS, `103.0/103`.
- Artifact Level 1 verifier: PASS, `44/44`.
- Artifact LaTeX rebuild: PASS, 12 pages.
- Exact ZIP clean-room strict secret/path scan: PASS, 92 text/source files scanned.
- Exact ZIP clean-room Level 1 verifier: PASS.
- Exact ZIP clean-room LaTeX rebuild: PASS, 12 pages.
- Sanitized upload repository refreshed and locally committed outside the anonymous artifact:
  - path: local sanitized upload repository
  - commit: recorded in external release metadata, not embedded in the anonymous artifact.
  - push status: external upload state; the anonymous artifact only records that local validation passed.
- Upload repository validation: Level 1 PASS, LaTeX rebuild PASS at 12 pages, strict source/text scan PASS.

## Claim boundary

This phase changes presentation, formatting, artifact packaging, and anonymization hygiene only.
It does not change frozen empirical counts, task membership, candidate/probe records, Qwen evidence, manual audit labels, held-out calibration labels, or the selected-path claim boundary.
The `17/30` false-acceptance result and `26/30` specification-debt signal remain conditional on the selected certificate-producing path.
