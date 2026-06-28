# Secret and Anonymization Scan Report

Last updated: 2026-06-29.

Scope:

- The curated inspect-only artifact directory.
- The anonymous ZIP rebuilt from that directory after the Phase 32 core-claim code-record update and sanitization.

Package summary:

- Files in inspect-only directory: 133.
- Exact ZIP bytes and SHA256 are recorded in the outer packaging report after rebuild. They are intentionally not embedded inside this file, because this file is part of the ZIP payload and would otherwise change the ZIP hash.

Critical secret scan:

- No literal shared-password substrings found.
- No private-key markers found.
- No obvious high-entropy GitHub/OpenAI/Slack token prefixes found under tightened token patterns.
- Rebuilt ZIP byte scan: PASS.
- Broad key-name scans still find expected non-secret environment-variable and local-endpoint placeholder names in scripts and reports; these are listed below and are not credential values.

Anonymization scan:

- No author-identifying Windows user paths, workstation names, jump-host text, or raw remote-root paths were found after sanitization.
- Raw remote paths in copied reports/certificates were replaced with `<REMOTE_ROOT>` inside the package copy only. Original source evidence in the repository was not rewritten.

Expected non-secret hits:

- `OPENAI_API_KEY`, `HF_TOKEN`, and `HUGGINGFACE_HUB_TOKEN` appear as environment variable names in scripts and reports.
- `api_key = "patchcourt-local-endpoint"` appears as a local-endpoint placeholder for OpenAI-compatible serving.
- `hf_router_chat` appears as a backend name and can match broad token-prefix scans; it is not a credential.

Level 1 self-check:

- `python scripts/verify_level1_tables_20260528.py` was run from the inspect-only package root and from an extracted clean-room copy of the rebuilt ZIP.
- Output status: PASS.
- The verifier recomputed and matched 44 checks, including headline counts, source/probe stratification, pilot-50 drop reasons, selection funnel, and route-stability values.
- Report: `docs/LEVEL1_TABLE_REGENERATION_REPORT_20260528.md`.

LaTeX clean-room build:

- The rebuilt ZIP was extracted and built with `pdflatex -> bibtex -> pdflatex -> pdflatex`.
- Output status: PASS, 12 pages.
- The final LaTeX log has no overfull boxes, undefined citations/references, rerun prompts, errors, or fatal messages.

Conclusion:

- The inspect-only package is safe for anonymous review at Level 0/Level 1.
- If Level 2/Level 3 replay is requested, reviewers should replace `<REMOTE_ROOT>` with their own configured execution root.
