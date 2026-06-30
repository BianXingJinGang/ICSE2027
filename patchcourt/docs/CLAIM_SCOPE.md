# Claim Scope

PatchCourt certificates should be read as executable audit evidence for a
selected certificate-producing path. They show where a visible-test-passing
candidate can be separated by an additional probe or by post-freeze calibration.

The frozen headline counts are scoped as follows:

- `17/30` is the held-out false-acceptance count inside the frozen selected
  audit set.
- `26/30` is the specification-debt count inside the same frozen set.
- `6/10` and `6/10` are the pass/fail BDC yields for the two probe-upgrade
  slices.
- Qwen evidence is reported as one issue-specific pass/fail BDC plus four
  package-integrity pass/fail BDCs.

Read package-integrity BDCs separately from issue-correctness evidence, and keep
pre-freeze probes separate from post-freeze held-out labels.
