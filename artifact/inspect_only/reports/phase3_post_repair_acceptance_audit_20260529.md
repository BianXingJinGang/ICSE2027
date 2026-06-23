# ICSE Acceptance Audit

- Manuscript: `latex/main.tex`
- Artifact: `<ARTIFACT_ROOT>`
- Score: `103.0/103` (`100.0%`)
- Decision: `ready_for_final_polish`

Heuristic smoke detector only; use with ICSE acceptance gauntlet and human judgment.

| Check | Status | Weight | Evidence | Advice |
|---|---:|---:|---|---|
| phenomenon_title: Title is phenomenon-first | PASS | 7 | Visible Tests Are Not Oracles: Characterizing False Acceptance in LLM-Based Repository Repair | Lead with the failure phenomenon, not the tool name. |
| opening_case: First page contains a concrete false-acceptance story | PASS | 10 | case+behavior signals in first 900 words | Open the introduction with Matplotlib or Seaborn visible-pass behavioral split before the full pipeline. |
| rq_ladder: RQ1-RQ4 ladder is visible | PASS | 8 | RQ1=3, RQ2=3, RQ3=2, RQ4=2 | Keep RQs as prevalence, stronger evidence, operational value, and boundary. |
| denominators: Headline counts include denominators | PASS | 8 | 19 ratio-like counts found | Every headline result should show denominator and selected-set boundary. |
| patchcourt_counts: PatchCourt headline counts are present | PASS | 7 | present=['17/30', '26/30', '6/10'] | Preserve 17/30, 26/30, and 6/10 with explicit frozen/selected boundaries. |
| claim_boundary: Non-oracle and non-population claim boundaries are explicit | PASS | 10 | 31 boundary signals found | Repeat non-oracle and non-population boundaries in abstract/results/threats. |
| inflated_language: Inflated correctness language is controlled | PASS | 8 | risky_terms=3; protective_boundaries=5 | Remove or negate proof/guarantee/correctness-oracle language unless formally justified. |
| artifact_checkability: Artifact checkability is reviewer-visible | PASS | 10 | manuscript_signals=16; 72 files; verifier=True; scan=True; data_like_files=47 | Name Level 1 verifier and shipped CSV/JSONL/Markdown inputs; keep secret scan current. |
| threats_validity: Threats cover standard ICSE validity dimensions | PASS | 7 | sections=['threats to validity']; validity_terms=8 | Use threats as claim-scope engineering across internal/construct/external/conclusion validity. |
| related_work_wedge: Related work names the right ICSE comparison axes | PASS | 8 | PatchDiff=True, SWE-bench=True, overfitting=True, repair=True, test generation=False | Contrast by timing and label access, not just by keyword overlap. |
| qwen_boundary: Qwen is framed as boundary/stress evidence | PASS | 7 | qwen_seen=True; boundary_signal=True | Do not present Qwen as broad independent-source reproduction unless evidence changes. |
| case_traceability: Case studies include traceable certificate evidence | PASS | 7 | 65 certificate/id-like signals found | Each case should include certificate ID/suffix, behavior split, and non-oracle boundary. |
| table_figure_anchors: Claims are anchored to tables or figures | PASS | 6 | 11 table/figure reference signals found | Every RQ answer should point to a specific table, figure, or case-study evidence. |

## Repair Queue

- No heuristic failures or warnings.
