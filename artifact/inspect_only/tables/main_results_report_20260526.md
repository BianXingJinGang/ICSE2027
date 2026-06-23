# PatchCourt Main Results 2026-05-26

## Summary

| created_at | gold_boundary | heldout_queue | heldout_records | heldout_executable | false_acceptance_true | false_acceptance_false | specification_debt_signal | upgrade_probe_queue | upgrade_probe_target_count | upgrade_probe_execution_count | upgrade_probe_layer_counts | upgrade_bdc_queue | upgrade_bdc_task_count | upgrade_bdc_pass_fail_task_count | extra_full_package_probe_queue | extra_full_package_probe_target_count | extra_full_package_probe_execution_count | extra_full_package_bdc_queue | extra_full_package_bdc_task_count | extra_full_package_bdc_pass_fail_task_count | external_model_baseline_classification | external_model_baseline_ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-05-26T14:07:33Z | held-out labels were read only after frozen_certificate_index_20260526.json was written | heldout_calibration_queue_20260526_124819 | 30 | 30 | 17 | 13 | 26 | audit_probe_upgrade_queue_20260526_131117 | 10 | 40 | {'full_package_behavioral_probe': 24, 'issue_codeblock_full_package': 16} | bdc_queue_20260526_131207 | 6 | 6 | audit_probe_upgrade_queue_20260526_140600 | 10 | 40 | bdc_queue_20260526_140640 | 7 | 6 | append_only_direct_batch_lane_only | False |

## Table 1: Held-Out False Acceptance

| freeze_id | task_id | repo | calibration_source | manual_audit_status | original_probe_layer | original_cc_ogb_lower_bound | specification_debt_signal | heldout_status | heldout_f2p_pass | false_acceptance_label | fail_to_pass_count | pass_to_pass_count | upgrade_bdc_available | specification_debt_reasons |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | astropy__astropy-14365 | astropy/astropy | codex_session_bootstrap | retain | source_isolated_template | 0.250 | True | executed | False | True | 1 | 8 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 2 | django__django-16255 | django/django | codex_session_bootstrap | retain | source_isolated_template | 0.250 | True | executed | True | False | 1 | 36 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 3 | django__django-16873 | django/django | codex_session_bootstrap | retain | source_isolated_template | 0.250 | True | executed | True | False | 2 | 12 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 4 | marshmallow-code__marshmallow-1343 | marshmallow-code/marshmallow | llm_batch_direct | retain | custom_active_probe | 0.750 | False | executed | True | False | 1 | 24 | False |  |
| 5 | marshmallow-code__marshmallow-1359 | marshmallow-code/marshmallow | llm_batch_direct | retain | custom_active_probe | 0.250 | False | executed | True | False | 1 | 76 | False |  |
| 6 | matplotlib__matplotlib-23562 | matplotlib/matplotlib | llm_batch_direct | downgrade | source_isolated_template | 0.250 | True | executed | False | True | 2 | 136 | False | manual_audit_downgrade;source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 7 | matplotlib__matplotlib-24149 | matplotlib/matplotlib | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | False | True | 1 | 767 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 8 | mwaskom__seaborn-2848 | mwaskom/seaborn | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | False | True | 1 | 50 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 9 | mwaskom__seaborn-3010 | mwaskom/seaborn | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | True | False | 1 | 2 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 10 | mwaskom__seaborn-3190 | mwaskom/seaborn | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | False | True | 1 | 84 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 11 | mwaskom__seaborn-3407 | mwaskom/seaborn | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | False | True | 1 | 120 | True | not_main_table_ready_after_audit |
| 12 | pallets__flask-4992 | pallets/flask | codex_session_bootstrap | retain | source_isolated_template | 0.500 | True | executed | True | False | 1 | 18 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 13 | pallets__flask-5063 | pallets/flask | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | False | True | 2 | 54 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 14 | psf__requests-2148 | psf/requests | codex_session_bootstrap | retain | source_isolated_template | 0.250 | True | executed | False | True | 10 | 118 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 15 | pvlib__pvlib-python-1072 | pvlib/pvlib-python | llm_batch_direct | retain | custom_active_probe | 0.250 | False | executed | True | False | 1 | 18 | False |  |
| 16 | pydata__xarray-4094 | pydata/xarray | codex_session_bootstrap | retain | source_isolated_template | 0.500 | True | executed | False | True | 1 | 862 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 17 | pydata__xarray-5131 | pydata/xarray | codex_session_bootstrap | downgrade | source_isolated_template | 0.250 | True | executed | True | False | 10 | 24 | False | manual_audit_downgrade;source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 18 | pylint-dev__pylint-5859 | pylint-dev/pylint | llm_batch_direct | downgrade | source_isolated_template | 0.500 | True | executed | True | False | 1 | 10 | False | manual_audit_downgrade;source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 19 | pylint-dev__pylint-6506 | pylint-dev/pylint | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | False | True | 2 | 6 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 20 | pylint-dev__pylint-7114 | pylint-dev/pylint | llm_batch_direct | retain | source_isolated_template | 0.750 | True | executed | False | True | 1 | 56 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 21 | pylint-dev__pylint-7228 | pylint-dev/pylint | llm_batch_direct | downgrade | source_isolated_template | 0.250 | True | executed | False | True | 2 | 10 | False | manual_audit_downgrade;source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 22 | pylint-dev__pylint-7993 | pylint-dev/pylint | llm_batch_direct | downgrade | source_isolated_template | 0.250 | True | executed | True | False | 1 | 10 | False | manual_audit_downgrade;source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 23 | pytest-dev__pytest-11148 | pytest-dev/pytest | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | False | True | 2 | 129 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 24 | pytest-dev__pytest-8906 | pytest-dev/pytest | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | False | True | 1 | 84 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 25 | scikit-learn__scikit-learn-10508 | scikit-learn/scikit-learn | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | False | True | 2 | 18 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 26 | sphinx-doc__sphinx-7686 | sphinx-doc/sphinx | llm_batch_direct | downgrade | source_isolated_template | 0.250 | True | executed | False | True | 2 | 15 | False | manual_audit_downgrade;source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 27 | sphinx-doc__sphinx-8713 | sphinx-doc/sphinx | llm_batch_direct | downgrade | source_isolated_template | 0.250 | True | executed | True | False | 1 | 45 | False | manual_audit_downgrade;source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 28 | sympy__sympy-16106 | sympy/sympy | llm_batch_direct | downgrade | source_isolated_template | 0.250 | True | executed | False | True | 1 | 55 | False | manual_audit_downgrade;source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 29 | sympy__sympy-17655 | sympy/sympy | llm_batch_direct | retain | source_isolated_template | 0.250 | True | executed | True | False | 2 | 9 | False | source_isolated_not_yet_upgraded;not_main_table_ready_after_audit |
| 30 | sympy__sympy-23117 | sympy/sympy | llm_batch_direct | retain | issue_codeblock_full_package | 0.250 | False | executed | True | False | 1 | 3 | True |  |

## Table 2: Upgraded Full-Package / Issue-Code Probes

| task_id | repo | probe_id | probe_layer | probe_executions | pass_count | fail_count | timeout_count | upgrade_bdc_available | upgrade_behavior_group_count | upgrade_cc_ogb_lower_bound | certificate_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| astropy__astropy-14365 | astropy/astropy | upgrade-fullpkg-astropy-qdp-lowercase-read | full_package_behavioral_probe | 4 | 0 | 4 | 0 | False | 0 | 0.000 |  |
| django__django-16255 | django/django | upgrade-fullpkg-django-empty-sitemap-lastmod | full_package_behavioral_probe | 4 | 3 | 1 | 0 | True | 2 | 0.250 | django__django-16255::upgrade-fullpkg-django-empty-sitemap-lastmod::57386192cdec |
| django__django-16873 | django/django | upgrade-fullpkg-django-join-autoescape-off | full_package_behavioral_probe | 4 | 3 | 1 | 0 | True | 2 | 0.250 | django__django-16873::upgrade-fullpkg-django-join-autoescape-off::3f215078cc87 |
| matplotlib__matplotlib-24149 | matplotlib/matplotlib | upgrade-fullpkg-matplotlib-bar-all-nan | full_package_behavioral_probe | 4 | 3 | 1 | 0 | True | 2 | 0.250 | matplotlib__matplotlib-24149::upgrade-fullpkg-matplotlib-bar-all-nan::6d71aa269334 |
| mwaskom__seaborn-3407 | mwaskom/seaborn | upgrade-fullpkg-seaborn-pairplot-multiindex | full_package_behavioral_probe | 4 | 3 | 1 | 0 | True | 2 | 0.250 | mwaskom__seaborn-3407::upgrade-fullpkg-seaborn-pairplot-multiindex::c360f3811a8c |
| pytest-dev__pytest-11148 | pytest-dev/pytest | upgrade-issuecode-pytest-importlib-namespace | issue_codeblock_full_package | 4 | 4 | 0 | 0 | False | 0 | 0.000 |  |
| pytest-dev__pytest-8906 | pytest-dev/pytest | upgrade-issuecode-pytest-module-skip-message | issue_codeblock_full_package | 4 | 4 | 0 | 0 | False | 0 | 0.000 |  |
| scikit-learn__scikit-learn-10508 | scikit-learn/scikit-learn | upgrade-fullpkg-sklearn-labelencoder-empty-transform | full_package_behavioral_probe | 4 | 3 | 1 | 0 | True | 2 | 0.250 | scikit-learn__scikit-learn-10508::upgrade-fullpkg-sklearn-labelencoder-empty-transform::40b7bfac5420 |
| sympy__sympy-17655 | sympy/sympy | upgrade-issuecode-sympy-point-left-scalar | issue_codeblock_full_package | 4 | 0 | 4 | 0 | False | 0 | 0.000 |  |
| sympy__sympy-23117 | sympy/sympy | upgrade-issuecode-sympy-empty-array | issue_codeblock_full_package | 4 | 3 | 1 | 0 | True | 2 | 0.250 | sympy__sympy-23117::upgrade-issuecode-sympy-empty-array::659ab52dbadd |

## Table 6: Extra Full-Package Probe Layer

| task_id | repo | probe_id | probe_layer | probe_executions | pass_count | fail_count | timeout_count | upgrade_bdc_available | upgrade_behavior_group_count | upgrade_cc_ogb_lower_bound | certificate_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| marshmallow-code__marshmallow-1343 | marshmallow-code/marshmallow | upgrade-fullpkg-marshmallow-nested-invalid-validate | full_package_behavioral_probe | 4 | 2 | 2 | 0 | True | 3 | 0.500 | marshmallow-code__marshmallow-1343::upgrade-fullpkg-marshmallow-nested-invalid-validate::45bee22438ea |
| marshmallow-code__marshmallow-1359 | marshmallow-code/marshmallow | upgrade-fullpkg-marshmallow-list-datetime-load | full_package_behavioral_probe | 4 | 4 | 0 | 0 | False | 0 | 0.000 |  |
| mwaskom__seaborn-2848 | mwaskom/seaborn | upgrade-fullpkg-seaborn-pairplot-hue-order-filter | full_package_behavioral_probe | 4 | 0 | 4 | 0 | True | 2 | 0.000 | mwaskom__seaborn-2848::upgrade-fullpkg-seaborn-pairplot-hue-order-filter::a00ae0775a3e |
| pallets__flask-4992 | pallets/flask | upgrade-fullpkg-flask-config-from-file-mode | full_package_behavioral_probe | 4 | 2 | 2 | 0 | True | 2 | 0.500 | pallets__flask-4992::upgrade-fullpkg-flask-config-from-file-mode::ea3d4feab212 |
| pallets__flask-5063 | pallets/flask | upgrade-fullpkg-flask-routes-subdomain-column | full_package_behavioral_probe | 4 | 0 | 4 | 0 | False | 0 | 0.000 |  |
| psf__requests-2148 | psf/requests | upgrade-fullpkg-requests-socket-error-wrapped | full_package_behavioral_probe | 4 | 2 | 2 | 0 | True | 3 | 0.500 | psf__requests-2148::upgrade-fullpkg-requests-socket-error-wrapped::e932f1c7454d |
| pvlib__pvlib-python-1072 | pvlib/pvlib-python | upgrade-fullpkg-pvlib-fuentes-tz-aware-index | full_package_behavioral_probe | 4 | 3 | 1 | 0 | True | 2 | 0.250 | pvlib__pvlib-python-1072::upgrade-fullpkg-pvlib-fuentes-tz-aware-index::cd30c1d7f12f |
| pydata__xarray-4094 | pydata/xarray | upgrade-fullpkg-xarray-unstacked-dataset-drop-level-coord | full_package_behavioral_probe | 4 | 3 | 1 | 0 | True | 2 | 0.250 | pydata__xarray-4094::upgrade-fullpkg-xarray-unstacked-dataset-drop-level-coord::b77786865f9c |
| pylint-dev__pylint-6506 | pylint-dev/pylint | upgrade-fullpkg-pylint-unrecognized-option-no-traceback | full_package_behavioral_probe | 4 | 0 | 4 | 0 | False | 0 | 0.000 |  |
| pylint-dev__pylint-7114 | pylint-dev/pylint | upgrade-fullpkg-pylint-namespace-no-missing-init | full_package_behavioral_probe | 4 | 3 | 1 | 0 | True | 4 | 0.250 | pylint-dev__pylint-7114::upgrade-fullpkg-pylint-namespace-no-missing-init::001dea940168 |

## Table 3: Correlation Signals

| signal | pearson_with_false_acceptance | spearman_with_false_acceptance | average_precision |
| --- | --- | --- | --- |
| original_cc_ogb_lower_bound | -0.116 | -0.144 | 0.557 |
| risk_cc_plus_debt | 0.146 | 0.115 | 0.612 |
| risk_audit_weighted | 0.129 | 0.107 | 0.617 |
| specification_debt_signal | 0.449 | 0.449 | 0.612 |

## Table 4: Rerank Triage

| score | k | reviewed | false_acceptances_found | precision_at_k | recall_at_k |
| --- | --- | --- | --- | --- | --- |
| risk_cc_only | 5 | 5 | 2 | 0.400 | 0.118 |
| risk_cc_only | 10 | 10 | 4 | 0.400 | 0.235 |
| risk_cc_only | 15 | 15 | 8 | 0.533 | 0.471 |
| risk_cc_only | 20 | 20 | 11 | 0.550 | 0.647 |
| risk_cc_plus_debt | 5 | 5 | 2 | 0.400 | 0.118 |
| risk_cc_plus_debt | 10 | 10 | 5 | 0.500 | 0.294 |
| risk_cc_plus_debt | 15 | 15 | 9 | 0.600 | 0.529 |
| risk_cc_plus_debt | 20 | 20 | 13 | 0.650 | 0.765 |
| risk_audit_weighted | 5 | 5 | 2 | 0.400 | 0.118 |
| risk_audit_weighted | 10 | 10 | 6 | 0.600 | 0.353 |
| risk_audit_weighted | 15 | 15 | 9 | 0.600 | 0.529 |
| risk_audit_weighted | 20 | 20 | 13 | 0.650 | 0.765 |

## Table 5: Abstain Triage

| rule | total_tasks | abstain_count | accept_count | abstain_rate | false_acceptances_captured | false_acceptance_capture_rate | residual_false_acceptances | residual_false_acceptance_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cc_ogb>=0.25 | 30 | 30 | 0 | 1.000 | 17 | 1.000 | 0 | 0.000 |
| cc_ogb>=0.50 | 30 | 5 | 25 | 0.167 | 2 | 0.118 | 15 | 0.600 |
| cc_ogb>=0.75 | 30 | 2 | 28 | 0.067 | 1 | 0.059 | 16 | 0.571 |
| specification_debt_signal | 30 | 26 | 4 | 0.867 | 17 | 1.000 | 0 | 0.000 |
| spec_debt_or_cc_ogb>=0.25 | 30 | 30 | 0 | 1.000 | 17 | 1.000 | 0 | 0.000 |

## Reading Notes

- `llm_batch_direct` remains classified by the readiness gate; it is not treated as an independent external model baseline unless the readiness report says so.
- Table 2 separates probe execution success from BDC formation; the current upgraded layer executes 10 targets and yields stable BDCs for 6 tasks.
- Table 6 is an append-only extra full-package layer; pass/fail BDCs are stronger than all-fail behavioral splits.
- Correlation and rerank rows are preliminary risk-signal analyses over the frozen 30-task audit set.
