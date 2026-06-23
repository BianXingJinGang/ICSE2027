# Qwen Multi-Sample Visible-11 Probe Run - 2026-05-27

## Purpose

Run multi-sample structured Qwen generation on the 11 tasks that previously reached Qwen compatible visible-pass, then run source-isolated generic probes plus issue/full-package and package-integrity probes to obtain independent-source BDCs.

## Queues

| Stage | Queue | Result |
| --- | --- | --- |
| Multi-sample materialization | `candidate_external_materialization_20260527_151130` | 55 records: 29 Qwen model samples, 11 no-op controls, 15 blocked structured edits |
| Apply/visible | `candidate_apply_visible_queue_20260527_154713` | 55 apply records, 40 materialized/control candidates, 94 visible-command results |
| Generic issue probes | `generic_issue_probe_queue_20260527_154825` -> `bdc_queue_20260527_154846` | 28 probe results, 0 BDC |
| Issue/full-package probes | `audit_probe_upgrade_queue_20260527_154942` -> `bdc_queue_20260527_155027` | 35 probe results, 5 BDC tasks |
| Package-integrity probes | `audit_probe_upgrade_queue_20260527_155257` -> `bdc_queue_20260527_155342` | 35 probe results, 4 pass/fail BDC tasks |
| Issue/full-package ledger | `evidence_ledger_queue_20260527_155442` | mean CC-OGB 0.64, pass/fail tasks 1/5 |
| Package-integrity ledger | `evidence_ledger_queue_20260527_155454` | mean CC-OGB 0.575, pass/fail tasks 4/4 |

## Materialization And Visible-Pass Yield

- Target tasks: 11 Qwen compatible visible-pass tasks from the frozen-30 structured run.
- Sampling: 4 structured SEARCH/REPLACE samples per direct_repair request, temperature 0.45, one no-op control per task.
- Model materialization: 29/44 Qwen samples exported as audited diffs.
- Apply/visible summary from the apply queue: 29 applied Qwen samples, 11 applied no-op controls, 15 not materialized.
- Compatible visible-pass model candidates: 26 Qwen samples across 9 tasks.
- Strict visible-pass model candidates: 14 Qwen samples across 5 tasks.

## BDC Results

Generic source-isolated probes remained negative on this multi-sample Qwen pool: 0 BDC from 28 probe results.

Issue/full-package probes produced 5 BDC tasks, but only one has a pass/fail split. The other four are all-fail behavioral divergences and should be reported as weaker evidence:

| Task | Probe | Candidates | Pass | Fail | Strength |
| --- | --- | ---: | ---: | ---: | --- |
| `mwaskom__seaborn-3190` | `upgrade-fullpkg-seaborn-continuous-bool-interval` | 2 | 0 | 2 | weaker all-fail divergence |
| `mwaskom__seaborn-3407` | `upgrade-fullpkg-seaborn-pairplot-multiindex` | 5 | 1 | 4 | strong pass/fail |
| `pallets__flask-5063` | `upgrade-fullpkg-flask-routes-subdomain-column` | 5 | 0 | 5 | weaker all-fail divergence |
| `pylint-dev__pylint-7114` | `upgrade-fullpkg-pylint-namespace-no-missing-init` | 2 | 0 | 2 | weaker all-fail divergence |
| `scikit-learn__scikit-learn-10508` | `upgrade-fullpkg-sklearn-labelencoder-empty-transform` | 5 | 0 | 5 | weaker all-fail divergence |

Package-integrity probes produced 4 pass/fail BDC tasks. These are not issue-specific correctness proofs; they certify that visible-pass Qwen patches can split on full-package import/core-API integrity:

| Task | Probe | Candidates | Pass | Fail | CC-OGB lb |
| --- | --- | ---: | ---: | ---: | ---: |
| `mwaskom__seaborn-3190` | `upgrade-fullpkg-integrity-seaborn-import-core` | 2 | 1 | 1 | 0.5 |
| `mwaskom__seaborn-3407` | `upgrade-fullpkg-integrity-seaborn-import-core` | 5 | 2 | 3 | 0.6 |
| `pallets__flask-5063` | `upgrade-fullpkg-integrity-flask-import-core` | 5 | 2 | 3 | 0.6 |
| `scikit-learn__scikit-learn-10508` | `upgrade-fullpkg-integrity-sklearn-preprocessing-import` | 5 | 2 | 3 | 0.6 |

## Claim Boundary

Claimable after this run:

- Multi-sample Qwen structured generation substantially improves the independent-source visible-pass candidate pool: 26 model visible-pass samples across 9 tasks.
- The target of 3-5 independent-source BDCs is met if full-package integrity BDCs are counted: 4 strong pass/fail integrity BDC tasks, plus 1 issue/full-package pass/fail BDC task.
- The strongest issue-specific Qwen BDC is `mwaskom__seaborn-3407`; the other issue/full-package BDCs are all-fail behavior-divergence certificates and must be separated.

Not claimable yet:

- Do not claim Qwen reproduces the full Codex/bootstrap issue-specific pass/fail BDC signal.
- Do not merge all-fail divergences into the conservative pass/fail BDC count.
- Do not treat package-integrity BDCs as proof of issue correctness; they are full-package regression/integrity certificates over visible-pass patches.

## Next Step

Audit the 4 package-integrity BDCs plus the `mwaskom__seaborn-3407` issue/full-package BDC, then decide whether RQ4 is reported as a partial positive independent-source result: Qwen gives nonzero BDC evidence under multi-sample generation, but the strong issue-specific pass/fail yield remains limited.
