# PatchCourt ICSE 2027 Package

This repository contains the sanitized ICSE 2027 submission package for PatchCourt, a protocol for auditing visible-test false acceptance in LLM-based repository repair.

## Contents

- `submission/patchcourt_icse2027_research_track_submission.pdf`: current submission-facing PDF.
- `artifact/inspect_only/`: anonymous inspect-only artifact with scripts, tables, certificates, figures, reports, and LaTeX source.
- `artifact/patchcourt_icse2027_anonymous_inspect_only.zip`: ZIP copy of the same inspect-only artifact.

## Quick Verification

From `artifact/inspect_only`, run:

```bash
python scripts/verify_level1_tables_20260528.py
```

The verifier recomputes the headline table counts, selection funnel, route-stability values, and pilot-50 drop-reason checks from packaged CSV, JSON, JSONL, and Markdown files.

Expected status: `PASS` with 44 checks.

## Current Package Hashes

- Submission PDF SHA256: `47829CC173D0A535F71DBAE3589EE56A0465EAB07B749F0F0575995B69D5718D`
- Inspect-only artifact ZIP SHA256: `6D45C0846DA00306F69106955213FAC0C394FD0BB84D3A10B49C89311BAF576E`

## Claim Boundary

PatchCourt certificates are executable audit evidence for a selected certificate-producing path. They are not correctness oracles and should not be interpreted as population-wide rates over all SWE-bench tasks or all LLM-generated patches.
