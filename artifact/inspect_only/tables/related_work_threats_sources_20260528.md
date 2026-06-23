# Related Work And Threats Source Notes 2026-05-28

This file records the related-work framing used in the full draft. It is not final BibTeX. It is a source-controlled note so the final LaTeX paper can later resolve citation keys without changing the technical claim boundary.

## Related Work Buckets

### Repository-Level LLM Repair And Agents

Use this bucket to establish the setting, not to compete with agents.

Draft claim:

- SWE-bench-style issue resolution evaluates whether systems can edit real repositories from issue descriptions.
- Agent systems such as SWE-agent and AutoCodeRover improve repository navigation, editing, and command execution.
- PatchCourt is complementary: it audits the acceptance layer after candidate patches exist.
- The sharp boundary is unit-of-analysis: agents optimize patch generation and leaderboard task solving; PatchCourt studies what evidence exists when visible-pass candidate patches are about to be accepted.

Source anchors:

- SWE-bench: `https://arxiv.org/abs/2310.06770`
- SWE-agent: `https://arxiv.org/abs/2405.15793`
- AutoCodeRover: `https://arxiv.org/abs/2404.05427`

### Plausible Patches And Test-Suite Overfitting

Use this bucket to connect visible-test false acceptance to classical APR risk.

Draft claim:

- APR has long distinguished plausible patches from correct patches.
- Test-suite overfitting occurs when a patch passes available tests but fails to generalize to intended behavior.
- PatchCourt does not claim to rediscover APR overfitting.
- The sharper contribution is an auditable pre-freeze protocol for repository-level LLM repair: freeze visible-pass hypotheses, build executable disagreement certificates from public issue evidence, and only then calibrate against held-out labels.

Source anchors:

- Automated patch assessment for program repair at scale: `https://link.springer.com/article/10.1007/s10664-020-09920-w`
- Critical review on APR evaluation: `https://www.sciencedirect.com/science/article/pii/S0164121220302156`

### SWE-Bench Correctness And PatchDiff Boundary

Use this bucket early because reviewers may know the ICSE 2026 PatchDiff/SWE-bench-correctness work.

Draft claim:

- Recent work asks whether SWE-bench "solved" issues are really solved, and uses differential patch testing against human-written patches.
- PatchCourt differs by preserving an inference-time gold boundary: developer patches and held-out labels are excluded until after certificate freeze.
- PatchDiff-style work is stronger for retrospective correctness analysis because it can compare against the developer patch or gold tests.
- PatchCourt is intentionally weaker in truth claim but earlier in availability: it can run before developer patch, FAIL_TO_PASS, or PASS_TO_PASS labels are consulted.

Source anchors:

- Are "Solved Issues" in SWE-bench Really Solved Correctly? `https://arxiv.org/abs/2503.15223`
- ICSE 2026 PDF mirror: `https://software-lab.org/publications/icse2026_SWE-bench-correctness.pdf`

Boundary wording:

- Do not claim PatchCourt supersedes PatchDiff.
- Say PatchCourt is complementary: PatchDiff is stronger when a gold patch is available; PatchCourt is designed for pre-gold audit and triage.
- Use this contrast in rebuttal terms: "PatchDiff is a retrospective correctness lens; PatchCourt is a pre-freeze risk-audit lens."

### Generated Tests And The Oracle Problem

Use this bucket to explain why PatchCourt calls probes evidence, not truth.

Draft claim:

- Generated tests can expose behavior, but the expected-output problem remains a test-oracle problem.
- PatchCourt avoids treating generated probes as absolute truth by layering probe strength and using held-out calibration after freeze.
- Generated probes should be described as evidence-producing instruments, not tests with guaranteed oracle quality.
- The evidence hierarchy is part of the contribution: source-isolated templates < issue-code snippets < full-package issue probes < package-integrity checks for regression risk < post-freeze held-out calibration.

Source anchors:

- The Oracle Problem in Software Testing: A Survey: `https://discovery.ucl.ac.uk/1471263/`
- Automated Test Oracles: A Survey: `https://www.sciencedirect.com/science/article/abs/pii/B9780128001608000012`

### Empirical SE Protocols And Artifacts

Use this bucket to justify the ledger and artifact.

Draft claim:

- The contribution is partly methodological: maintaining a traceable boundary between inference-time evidence and evaluation-time labels.
- The artifact's value is inspectability: candidate metadata, probe results, certificates, audit labels, and held-out rows can be traced.

## Threats To Preserve

Internal validity:

- Probe implementation may be wrong or incomplete.
- Environment routing can change behavior.
- Candidate application fallback and normalization must be auditable.

Construct validity:

- BDC is not correctness.
- CC-OGB is not a probability.
- Package-integrity BDC is not issue-specific correctness.
- All-fail divergence is weaker than pass/fail split.

External validity:

- Frozen 30 is selected, not a benchmark-wide sample.
- Python-heavy/SWE-bench-style tasks may not generalize to other languages.
- Candidate sources are limited.

Conclusion validity:

- N=30 makes correlation/rerank results preliminary.
- Specification-debt strength may depend on selection.
- Wilson intervals should accompany primary proportions.

Independent-source validity:

- Qwen source is real but weak for issue-specific BDC reproduction.
- Qwen package-integrity positives must remain separate.
- Do not present `llm_batch_direct` as an independent external model baseline.

Gold-boundary validity:

- The artifact must prove that developer patch, test patch, FAIL_TO_PASS, and PASS_TO_PASS are excluded before freeze.
- Any future experiment that violates this boundary must be excluded from main claims.
