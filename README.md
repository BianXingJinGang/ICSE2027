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

- Submission PDF SHA256: `4A6AD37D733DB33F5438FF74259EA9CEF3F5C416FD0F00C451AAD71E6340D1E7`
- Inspect-only artifact ZIP SHA256: `08A7F84DFEFE767791D949E3FDBBA81272F6825AC06F3FAFE53FC37D37A05D7B`

## Claim Boundary

PatchCourt certificates are executable audit evidence for a selected certificate-producing path. They are not correctness oracles and should not be interpreted as population-wide rates over all SWE-bench tasks or all LLM-generated patches.
