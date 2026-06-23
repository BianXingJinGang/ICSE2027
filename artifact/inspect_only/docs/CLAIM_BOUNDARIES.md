# Claim Boundaries For Anonymous Artifact

## Supported Claims

1. PatchCourt has a working gold-boundary-aware certificate and calibration pipeline.
2. The selected certificate-producing path yields a frozen 30-task audit set with 30/30 executable held-out calibrations.
3. The selected certificate-producing path yields 17/30 held-out false acceptances in that frozen audit set.
4. Specification-debt signal appears in 26/30 frozen records and stratifies false acceptance in the current set.
5. Full-package or issue-code upgrades preserve pass/fail BDC evidence for selected targets:
   - 6/10 main upgrade targets,
   - 6/10 additional full-package targets.
6. Qwen2.5-Coder-7B is a real independent source ingested through the structured candidate lane.
7. Qwen provides limited independent-source BDC evidence:
   - 1 issue-specific pass/fail BDC,
   - 4 separate package-integrity pass/fail BDCs.

## Unsupported Claims

1. PatchCourt is not a correctness oracle.
2. BDCs are not hidden-test labels.
3. CC-OGB is not a calibrated probability of failure.
4. Package-integrity BDCs are not issue-correctness evidence.
5. Qwen does not broadly reproduce the issue-specific BDC signal.
6. `llm_batch_direct` is not an independent external model baseline.
7. The frozen 30-task false-acceptance rate is not a population estimate over all SWE-bench tasks.
8. The frozen 30-task false-acceptance rate is not a population estimate over all visible-passing LLM patches.

## Required Separation In Tables

- Source-isolated probes must remain separate from issue-code and full-package probes.
- Pass/fail BDCs must remain separate from all-fail divergence.
- Issue-specific Qwen BDCs must remain separate from Qwen package-integrity BDCs.
- Pre-freeze evidence must remain separate from post-freeze held-out labels.
