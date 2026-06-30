# PatchCourt Code Package

Start here if you want to inspect or rerun the lightweight checks.

```bash
python scripts/verify_level1_tables_20260528.py
```

The verifier reads the frozen tables and certificate JSONL files in this
directory. It does not call a model endpoint or open a repository worktree. The
expected result is a 44-check `PASS`.

## Directory Map

- `scripts/verify_level1_tables_20260528.py` recomputes the published counts
  from packaged files.
- `scripts/patchcourt_external_candidate_materializer.py` connects an
  independent model source through structured edits or unified diffs.
- `scripts/patchcourt_external_diff_normalizer.py` normalizes generated edits
  before application.
- `scripts/patchcourt_candidate_apply_visible_worker.py` applies candidates and
  runs visible-test commands.
- `scripts/patchcourt_generic_issue_probe_worker.py` and
  `scripts/patchcourt_audit_probe_upgrade_worker.py` run the probe layers.
- `scripts/patchcourt_bdc_builder.py` builds pass/fail behavior disagreement
  certificates.
- `scripts/patchcourt_evidence_ledger_builder.py` records certificate evidence
  and lower-bound summaries.
- `scripts/build_patchcourt_main_results_20260526.py` and
  `scripts/build_safe_route_characterization_20260528.py` are table builders
  from the original run layout.

## Data Files

- `tables/table1_heldout_false_acceptance_20260526.*` through
  `tables/table6_extra_full_package_probe_20260526.*` hold the main result
  slices.
- `tables/selection_funnel_20260529.*` records the selected-path funnel.
- `tables/route_stability_20260529.*` records the before/after routing checks.
- `tables/pilot50_drop_reasons_20260529.*` records why pilot tasks entered or
  left the conservative audit set.
- `certificates/*.jsonl` stores the frozen BDC records consumed by the verifier.

## Runtime Notes

The Level 1 verifier only needs Python 3.10 or newer and the standard library.
Pipeline workers need the repository snapshots, task environments, and model
endpoints used during the original runs.
