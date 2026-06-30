# Data Map

The bundled files are small enough for direct inspection.

## Tables

- Main result tables: `table1_*` through `table6_*`.
- Selection and routing: `selection_funnel_20260529.*`,
  `route_stability_20260529.*`.
- Pilot coverage: `pilot50_drop_reasons_20260529.*`.
- Safe-route summaries: `safe_route_*.csv`, `safe_route_characterization_*.json`,
  and `safe_route_characterization_*.md`.
- Qwen audit note: `qwen_bdc_audit_20260528.md`.

## Certificates

The JSONL files under `certificates/` are the certificate records used by the
verifier. Each row carries the task id, candidate id, probe layer, pass/fail
counts, and the evidence fields needed by the table check.

## Generated Output

Running `python scripts/verify_level1_tables_20260528.py` refreshes:

- `generated/level1_table_recheck_20260528.json`
- `docs/LEVEL1_TABLE_REGENERATION_REPORT_20260528.md`
