# PatchCourt Blocker Resolution Report

Date: 2026-05-26

## Executive State

This pass resolves the held-out execution blocker and converts the two remaining blockers into explicit, auditable gates:

| Blocker | Before | After | Status |
| --- | ---: | ---: | --- |
| Held-out FAIL_TO_PASS executable coverage | `15/30` | `30/30` | Resolved |
| Full-package / issue-code upgrade BDC yield | `2/10` | `6/10` | Partially resolved; remaining failures are candidate/probe or old-dependency issues |
| `llm_batch_direct` independent external baseline | no API key | readiness gate says not ready | Resolved as a reporting/control gate, not as an independent baseline |

The project state is therefore stronger than the previous next-gate report, but the ICSE status remains `Continue, Not Yet Go`: the main evidence is now executable and better layered, while a genuinely independent external model baseline still requires an API key or local model source.

## Held-Out Calibration

Previous queue: `heldout_calibration_queue_20260526_112612`

- `30` frozen audit records.
- `15/30` executable.
- False acceptance labels: `10` true, `5` false, `15` unknown.
- Specification-debt signal: `26/30`.

Resolved queue: `heldout_calibration_queue_20260526_124819`

- `30` frozen audit records.
- `30/30` executable.
- False acceptance labels: `17` true, `13` false, `0` unknown.
- Specification-debt signal remains `26/30`.
- The rebuilt CC-OGB table is in `audit_30plus_20260526/cc_ogb_false_acceptance_table_20260526/`.

Main fixes:

- Added per-task route support for generated version files, source import stubs, compiled-extension copy routing, and compatibility `sitecustomize.py` shims.
- Added held-out fallback execution for parameterized pytest targets and `file -k test_name` fallback.
- Tightened unavailable classification so actual assertion failures are not misclassified as collection/environment failures.
- Added `-x` to pytest held-out commands so known false-acceptance failures do not time out behind later tests.
- Added the isolated dependency runtime `<REMOTE_ROOT>/envs/patchcourt_py310_heldout_deps_20260526`.

## Probe Upgrade

Original upgrade queue: `audit_probe_upgrade_queue_20260526_110134`

- `40` probe results over `10` selected high-signal upgrade targets.
- Upgraded BDC tasks: `2/10`.
- Successful tasks: `mwaskom__seaborn-3407`, `sympy__sympy-23117`.

Final post-fix upgrade queue: `audit_probe_upgrade_queue_20260526_131117`

- BDC queue: `bdc_queue_20260526_131207`.
- `40` probe results over the same `10` targets.
- Upgraded BDC tasks: `6/10`.
- Successful tasks:
  - `django__django-16255`
  - `django__django-16873`
  - `matplotlib__matplotlib-24149`
  - `mwaskom__seaborn-3407`
  - `scikit-learn__scikit-learn-10508`
  - `sympy__sympy-23117`

Remaining non-BDC tasks:

- `astropy__astropy-14365`: still blocked by old Astropy source behavior under NumPy 2.x. Compatibility shims progressed the failure from missing NumPy aliases to NumPy 2.0 copy-semantics incompatibility. A separate NumPy 1.26 venv attempt was started but remote pip hung and was killed; it is not used in current evidence.
- `pytest-dev__pytest-11148`: all four candidates share the same passing outcome under the upgraded probe, so there is no behavioral disagreement certificate.
- `pytest-dev__pytest-8906`: all four candidates share the same expected outcome under the upgraded probe, so there is no behavioral disagreement certificate.
- `sympy__sympy-17655`: all four candidates fail the package-level scalar-multiplication reproducer, so the current candidate pool is not discriminative.

Interpretation: the original `2/10` result was mostly an execution-routing underestimate. The final `6/10` result is a stronger and more honest layer: successful upgrades are true full-package or issue-code probes, while the remaining four should be attacked with either old-dependency routing or a genuinely new candidate source, not with more source-isolated template inflation.

## External Baseline Gate

Readiness report:

- `external_model_baseline_readiness_20260526.json`
- `external_model_baseline_readiness_20260526.md`

Result:

- Local API credential presence: none among checked provider variables.
- Remote API credential presence: none among checked provider variables.
- Remote model-serving commands: no `ollama`, `vllm`, `lmdeploy`, or `sglang`.
- Remote model directories checked under `<REMOTE_ROOT>`: none present.
- Classification: `append_only_direct_batch_lane_only`.

Decision:

`llm_batch_direct` must not be described as an independent external model baseline in the current paper package. It is an append-only direct-batch lane through the current materializer until an actual external API key or local model runtime/weights are provided and candidate records name that backend/model.

## Current Use In Paper Tables

- Use `heldout_calibration_queue_20260526_124819` for held-out calibration: unavailable count is now zero.
- Use `bdc_queue_20260526_131207` as the post-fix upgraded-probe overlay: upgraded full-package/issue-code evidence is `6/10`.
- Keep the frozen audit index as the historical freeze layer; do not silently rewrite it to pretend the upgrades existed before the post-fix pass.
- Report `llm_batch_direct` as source-layer diversity / direct-batch lane, not as an independent external model baseline.

## Next Go/No-Go Work

1. Add a real independent candidate source: API-backed batch model generation or local model serving under `<REMOTE_ROOT>/models`.
2. For the four non-upgraded targets, prioritize new candidates before more probe engineering, except for Astropy where an old-NumPy isolated wheelhouse is the clean next route.
3. Build a post-fix evidence table that separates frozen source-isolated certificates, upgraded full-package/issue-code certificates, and direct-batch certificates.
4. Use the `30/30` held-out calibration table to test whether CC-OGB and specification-debt signals correlate with false acceptance after controlling for probe layer.
