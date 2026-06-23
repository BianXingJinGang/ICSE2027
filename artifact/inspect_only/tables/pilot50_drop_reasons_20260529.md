# Pilot-50 Drop-Reason Table 2026-05-29

This table exposes the path of the 50-task pilot substrate. It is not a SWE-bench population table. The paper-facing frozen 30 contains 27 tasks from this pilot path plus three earlier smoke certificates.

## Summary

| Metric | Value |
| --- | ---: |
| `pilot50_tasks` | 50 |
| `snapshot_built` | 50 |
| `candidate_slots_total` | 200 |
| `frozen_conservative_certificate` | 27 |
| `broad_certificate_not_frozen` | 1 |
| `raw_certificate_not_selected` | 0 |
| `no_conservative_certificate_in_final_audit_index` | 22 |

## Rows

| Rank | Task | Repo | Status | Drop reason |
| ---: | --- | --- | --- | --- |
| 1 | `pytest-dev__pytest-11148` | `pytest-dev/pytest` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 2 | `pytest-dev__pytest-7220` | `pytest-dev/pytest` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 3 | `pytest-dev__pytest-8906` | `pytest-dev/pytest` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 4 | `pytest-dev__pytest-9359` | `pytest-dev/pytest` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 5 | `pytest-dev__pytest-5103` | `pytest-dev/pytest` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 6 | `pytest-dev__pytest-7373` | `pytest-dev/pytest` | `broad_certificate_not_frozen` | broad all-fail behavior disagreement excluded from conservative pass/fail frozen 30 |
| 7 | `pylint-dev__pylint-6506` | `pylint-dev/pylint` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 8 | `pylint-dev__pylint-7114` | `pylint-dev/pylint` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 9 | `pylint-dev__pylint-7228` | `pylint-dev/pylint` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 10 | `pylint-dev__pylint-7993` | `pylint-dev/pylint` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 11 | `django__django-16255` | `django/django` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 12 | `sphinx-doc__sphinx-7738` | `sphinx-doc/sphinx` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 13 | `sphinx-doc__sphinx-8627` | `sphinx-doc/sphinx` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 14 | `sphinx-doc__sphinx-8713` | `sphinx-doc/sphinx` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 15 | `matplotlib__matplotlib-25079` | `matplotlib/matplotlib` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 16 | `mwaskom__seaborn-2848` | `mwaskom/seaborn` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 17 | `pylint-dev__pylint-5859` | `pylint-dev/pylint` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 18 | `sympy__sympy-17655` | `sympy/sympy` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 19 | `django__django-11964` | `django/django` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 20 | `django__django-12708` | `django/django` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 21 | `django__django-15814` | `django/django` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 22 | `django__django-16873` | `django/django` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 23 | `sphinx-doc__sphinx-7686` | `sphinx-doc/sphinx` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 24 | `sphinx-doc__sphinx-8282` | `sphinx-doc/sphinx` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 25 | `sphinx-doc__sphinx-8435` | `sphinx-doc/sphinx` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 26 | `matplotlib__matplotlib-24149` | `matplotlib/matplotlib` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 27 | `mwaskom__seaborn-3010` | `mwaskom/seaborn` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 28 | `mwaskom__seaborn-3190` | `mwaskom/seaborn` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 29 | `pallets__flask-4992` | `pallets/flask` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 30 | `sympy__sympy-16106` | `sympy/sympy` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 31 | `sympy__sympy-16792` | `sympy/sympy` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 32 | `sympy__sympy-22714` | `sympy/sympy` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 33 | `sympy__sympy-23117` | `sympy/sympy` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 34 | `django__django-12113` | `django/django` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 35 | `pydata__xarray-4094` | `pydata/xarray` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 36 | `pydata__xarray-4493` | `pydata/xarray` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 37 | `pydata__xarray-5131` | `pydata/xarray` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 38 | `scikit-learn__scikit-learn-13142` | `scikit-learn/scikit-learn` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 39 | `scikit-learn__scikit-learn-25500` | `scikit-learn/scikit-learn` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 40 | `astropy__astropy-14365` | `astropy/astropy` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 41 | `matplotlib__matplotlib-23299` | `matplotlib/matplotlib` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 42 | `matplotlib__matplotlib-23562` | `matplotlib/matplotlib` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 43 | `matplotlib__matplotlib-23964` | `matplotlib/matplotlib` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 44 | `matplotlib__matplotlib-24265` | `matplotlib/matplotlib` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 45 | `pallets__flask-5063` | `pallets/flask` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 46 | `psf__requests-2148` | `psf/requests` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 47 | `sympy__sympy-13471` | `sympy/sympy` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 48 | `scikit-learn__scikit-learn-10297` | `scikit-learn/scikit-learn` | `no_conservative_certificate_in_final_audit_index` | snapshot and candidate slots existed, but no conservative pass/fail certificate reached the final audit index after candidate/materialization/visible/probe/routing gates |
| 49 | `mwaskom__seaborn-3407` | `mwaskom/seaborn` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
| 50 | `scikit-learn__scikit-learn-10508` | `scikit-learn/scikit-learn` | `frozen_conservative_certificate` | retained in paper-facing frozen 30 selected certificate-producing path |
