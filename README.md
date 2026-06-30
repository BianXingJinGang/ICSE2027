# PatchCourt

PatchCourt audits repository-repair patches that pass visible tests. The code
keeps a frozen trail of candidate provenance, executable probes, behavior
disagreement certificates, manual audit labels, and post-freeze calibration
checks.

This public repository is the code-and-data slice. The manuscript PDF, LaTeX
source, submission ZIP, and figure build products are kept out of this upload.

## Quick Check

```bash
cd patchcourt
python scripts/verify_level1_tables_20260528.py
```

The command recomputes the frozen headline checks from the packaged CSV, JSON,
JSONL, and Markdown files. A clean run prints `PASS` for 44 checks and refreshes:

- `patchcourt/docs/LEVEL1_TABLE_REGENERATION_REPORT_20260528.md`
- `patchcourt/generated/level1_table_recheck_20260528.json`

## What Is Here

- `patchcourt/scripts/`: candidate materialization, diff normalization, visible-test
  execution, probe execution, BDC construction, ledger building, and table
  verification scripts.
- `patchcourt/tables/`: frozen result tables used by the verifier.
- `patchcourt/certificates/`: JSONL certificate records used in the selected
  audit path and Qwen stress lane.
- `patchcourt/generated/`: verifier output.
- `patchcourt/docs/`: short notes on data layout and claim scope.

Most checks use only the packaged files. The worker scripts that call external
models or run repositories need the original experiment worktrees and runtime
configuration.
