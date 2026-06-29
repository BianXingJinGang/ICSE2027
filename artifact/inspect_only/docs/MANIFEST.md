# Anonymous Artifact Manifest 2026-05-29

Package these files or their artifact-relative equivalents. The inspect-only archive uses sanitized restart/project-state summaries rather than raw operational logs when raw files contain local machine paths.

## Core Project State

- `paper/icse2027/artifact_bundle_anonymous_20260528/ANONYMIZED_RESTART.md`
- `paper/icse2027/artifact_bundle_anonymous_20260528/CLAIM_BOUNDARIES.md`
- `paper/icse2027/artifact_bundle_anonymous_20260528/README.md`
- `paper/icse2027/artifact_bundle_anonymous_20260528/BUILD_AND_SCAN.md`

Raw local project logs (`docs/RESTART.md`, `WORKLOG.md`, `DECISIONS.md`, `NEXT_STEPS.md`, and `docs/HANDOFF.md`) remain in the repository for handoff, but the anonymous inspect-only package should include sanitized summaries unless final artifact policy explicitly requests the raw logs after path scrubbing.

## PatchCourt Scripts

- `scripts/patchcourt_candidate_apply_visible_worker.py`
- `scripts/patchcourt_generic_issue_probe_worker.py`
- `scripts/patchcourt_audit_probe_upgrade_worker.py`
- `scripts/patchcourt_bdc_builder.py`
- `scripts/patchcourt_evidence_ledger_builder.py`
- `scripts/patchcourt_external_candidate_materializer.py`
- `scripts/patchcourt_external_diff_normalizer.py`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/scripts/verify_level1_tables_20260528.py`

## Table Builders And Reports

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/build_patchcourt_main_results_20260526.py`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/build_safe_route_characterization_20260528.py`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/main_results_report_20260526.md`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen_structured_frozen30_20260527_report.md`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/qwen_multisample_visible11_probe_bdc_20260527_report.md`

## Main Result Tables

- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table1_heldout_false_acceptance_20260526.csv`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table2_upgraded_probe_20260526.csv`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table3_correlation_20260526.csv`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table4_rerank_20260526.csv`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table5_abstain_20260526.csv`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/main_results_20260526/table6_extra_full_package_probe_20260526.csv`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/tables/pilot50_drop_reasons_20260529.csv`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/tables/pilot50_drop_reasons_20260529.json`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/tables/pilot50_drop_reasons_20260529.md`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/tables/selection_funnel_20260529.csv`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/tables/selection_funnel_20260529.json`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/tables/route_stability_20260529.csv`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/tables/route_stability_20260529.json`

## Safe-Route Characterization

- `paper/icse2027/assets_20260528/safe_route_characterization_20260528.md`
- `paper/icse2027/assets_20260528/safe_route_characterization_20260528.json`
- `paper/icse2027/assets_20260528/safe_route_*_20260528.csv`
- `paper/icse2027/assets_20260528/submission_table_pack_20260528.md`

## Qwen Audit

- `paper/icse2027/assets_20260528/qwen_bdc_audit_20260528.md`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/bdc_queue_20260527_155027_certificates.jsonl`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/bdc_queue_20260527_155342_certificates.jsonl`
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/bdc_queue_20260527_184051_certificates.jsonl`

## Paper Assets

- `paper/icse2027/latex_ieee_template_20260629/main.tex`
- `paper/icse2027/latex_ieee_template_20260629/references.bib`
- `paper/icse2027/latex_ieee_template_20260629/IEEEtran.cls`
- `paper/icse2027/latex_ieee_template_20260629/main.pdf`
- `paper/icse2027/submission_20260629_ieee_template/patchcourt_icse2027_research_track_submission_20260629_ieee_template.pdf`
- `paper/icse2027/assets_20260629_template_format_phase33/phase33_ieee_template_format_report_20260629.md`
- `paper/icse2027/assets_20260629_template_format_phase33/phase33_ieee_template_acceptance_audit_20260629.md`
- `paper/icse2027/assets_20260622_quant_figures14/figures/*.pdf`
- `paper/icse2027/assets_20260622_quant_figures14/figures/*.png`
- `paper/icse2027/assets_20260622_quant_figures14/phase26_quant_figures_1_4_manifest_20260622.json`
- `paper/icse2027/assets_20260622_quant_figures14/generate_quantitative_figures1_4_20260622.py`
- `paper/icse2027/assets_20260622_structured_edit_example/phase27_structured_edit_example_report_20260622.md`
- `paper/icse2027/assets_20260622_structured_edit_example/phase27_structured_edit_acceptance_audit_20260622.md`
- `reports/phase27_structured_edit_example_report_20260622.md`
- `reports/phase27_structured_edit_acceptance_audit_20260622.md`
- `paper/icse2027/assets_20260623_abstract_example_block/phase28_abstract_example_report_20260623.md`
- `paper/icse2027/assets_20260623_abstract_example_block/phase28_abstract_example_acceptance_audit_20260623.md`
- `reports/phase28_abstract_example_report_20260623.md`
- `reports/phase28_abstract_example_acceptance_audit_20260623.md`
- `paper/icse2027/assets_20260628_structured_patch_record/phase30_structured_patch_record_report_20260628.md`
- `paper/icse2027/assets_20260628_structured_patch_record/phase30_structured_patch_record_acceptance_audit_20260628.md`
- `reports/phase30_structured_patch_record_report_20260628.md`
- `reports/phase30_structured_patch_record_acceptance_audit_20260628.md`
- `paper/icse2027/assets_20260628_subject_aligned_patch_record/phase31_subject_aligned_patch_record_report_20260628.md`
- `paper/icse2027/assets_20260628_subject_aligned_patch_record/phase31_subject_aligned_patch_record_acceptance_audit_20260628.md`
- `reports/phase31_subject_aligned_patch_record_report_20260628.md`
- `reports/phase31_subject_aligned_patch_record_acceptance_audit_20260628.md`
- `paper/icse2027/assets_20260629_core_claim_code_record/phase32_core_claim_code_record_report_20260629.md`
- `paper/icse2027/assets_20260629_core_claim_code_record/phase32_core_claim_code_record_acceptance_audit_20260629.md`
- `reports/phase32_core_claim_code_record_report_20260629.md`
- `reports/phase32_core_claim_code_record_acceptance_audit_20260629.md`
- `paper/icse2027/assets_20260622_figures14_upgrade/figures/*.pdf`
- `paper/icse2027/assets_20260622_figures14_upgrade/figures/*.png`
- `paper/icse2027/assets_20260622_figures14_upgrade/phase25_figures_1_4_manifest_20260622.json`
- `paper/icse2027/assets_20260622_figures14_upgrade/generate_figures1_4_upgrade_20260622.py`
- `paper/icse2027/latex_ieee_20260529/figures/patchcourt_quantitative_summary_20260622.pdf`
- `paper/icse2027/assets_20260622_quant_figures/figures/*.pdf`
- `paper/icse2027/assets_20260622_quant_figures/figures/*.png`
- `paper/icse2027/assets_20260622_quant_figures/patchcourt_quantitative_figure_manifest_20260622.json`
- `paper/icse2027/patchcourt_icse2027_doubleblind_full_draft_20260528.md`
- `paper/icse2027/assets_20260528/qualitative_case_studies_polished_20260528.md`
- `paper/icse2027/assets_20260528/related_work_threats_sources_20260528.md`
- `paper/icse2027/assets_20260528/artifact_appendix_anonymous_20260528.md`
- `paper/icse2027/assets_20260529/phase2_desk_reject_integrity_report_20260529.md`
- `paper/icse2027/assets_20260529/phase3_post_repair_acceptance_audit_20260529.md`
- `paper/icse2027/assets_20260529/phase3_killshot_repair_report_20260529.md`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/docs/LEVEL1_TABLE_REGENERATION_REPORT_20260528.md`
- `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/generated/level1_table_recheck_20260528.json`
- `figures/phase26_quant_figures_1_4_manifest_20260622.json`
- `figures/patchcourt_running_example_20260622.pdf`
- `figures/patchcourt_main_pipeline_20260622.pdf`
- `figures/patchcourt_selection_funnel_20260622.pdf`
- `figures/patchcourt_certificate_evidence_ladder_20260622.pdf`
- `figures/patchcourt_quantitative_summary_20260622.pdf`
- `figures/patchcourt_calibration_rates_with_ci_20260622.pdf`
- `figures/patchcourt_probe_upgrade_yields_20260622.pdf`
- `figures/patchcourt_source_layer_audit_mix_20260622.pdf`
- `figures/patchcourt_route_stability_20260622.pdf`
- `figures/patchcourt_rerank_abstain_20260622.pdf`
- `figures/patchcourt_qwen_generation_funnel_20260622.pdf`
- `figures/patchcourt_repository_false_acceptance_distribution_20260622.pdf`
- `figures/patchcourt_quantitative_figure_manifest_20260622.json`
- `figures/patchcourt_visual_figure_inputs_20260531.json`

## Optional Appendix

- `paper/icse2027/assets_20260528/post_draft_decision_model_expansion_20260528.md`
- `paper/icse2027/assets_20260528/icse_readiness_report_20260528.md`
