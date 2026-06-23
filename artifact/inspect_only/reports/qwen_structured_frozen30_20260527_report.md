# Qwen Structured Frozen-30 Result 2026-05-27

## Result

| Metric | Count |
| --- | ---: |
| Frozen tasks | 30 |
| Model diffs materialized and applyable | 17 |
| Strict visible-pass model candidates | 6 |
| Compatible visible-pass model candidates | 11 |
| Probe results | 27 |
| BDC tasks | 0 |

## Interpretation

Structured SEARCH/REPLACE generation plus programmatic diff export clears the main applicability blocker from the direct-diff Qwen run. It does not yet clear the independent behavioral-disagreement blocker because no BDC was produced.

Paper boundary: report this as an independent-source negative/partial result, not as successful RQ4 reproduction.

## Compatible Visible-Pass Tasks

- `pylint-dev__pylint-6506`
- `pylint-dev__pylint-7114`
- `pylint-dev__pylint-5859`
- `pydata__xarray-5131`
- `pallets__flask-5063`
- `mwaskom__seaborn-3407`
- `pylint-dev__pylint-7228`
- `scikit-learn__scikit-learn-10508`
- `mwaskom__seaborn-3190`
- `mwaskom__seaborn-3010`
- `pydata__xarray-4094`
