# Qwen2.5-Coder-7B GGUF Local Endpoint Frozen-30 Run

Date: 2026-05-27

## Goal

Connect `Qwen2.5-Coder-7B-Instruct-GGUF` to the existing PatchCourt external candidate materializer through an OpenAI-compatible local endpoint, then rerun the frozen 30-task independent-source lane.

## Server Environment Findings

- GPU host direct access to ModelScope and GitHub is blocked or times out.
- An intermediate transfer node can reach both ModelScope and GitHub and has Python 3.9 plus Paramiko, so the working transfer route is:
  - the transfer node downloads large assets,
  - the transfer node pushes them to the GPU execution node over the internal network.
- GPU host has 8x RTX 3090, driver `550.163.01`, reported CUDA capability `12.4`.
- GPU host userspace is old: glibc `2.17`, no `cmake`, no `ninja`, no `git-lfs`, GCC/G++ `5.4.0`.
- Ubuntu `llama.cpp` binaries and CUDA `llama-cpp-python` wheel are not usable on this host because they require newer glibc/libstdc++.
- The compatible runtime is CPU `llama-cpp-python==0.3.23` manylinux2014.

## Runtime And Model Staging

- CPU llama-cpp environment:
  - `<REMOTE_ROOT>/envs/patchcourt_llama_cpp_py310_20260527`
- Model:
  - `<REMOTE_ROOT>/models/Qwen2.5-Coder-7B-Instruct-GGUF/qwen2.5-coder-7b-instruct-q4_k_m.gguf`
  - size: `4,683,073,536` bytes
  - ModelScope SHA-256 from file API: `509287f78cb4d4cf6b3843734733b914b2c158e43e22a7f4bf5e963800894d3c`
- OpenAI-compatible endpoint:
  - base URL: `http://127.0.0.1:18080/v1`
  - model alias: `qwen2.5-coder-7b-instruct-q4_k_m`
  - PID file: `<REMOTE_ROOT>/logs/qwen25coder7b_llama_cpp_server_20260527.pid`
  - log: `<REMOTE_ROOT>/logs/qwen25coder7b_llama_cpp_server_20260527.log`
- Endpoint smoke passed:
  - `/v1/models` returned the model alias.
  - `/v1/chat/completions` returned a unified diff.

## Code Changes

- `scripts/patchcourt_external_candidate_materializer.py`
  - Added explicit `openai_compatible_chat` backend readiness.
  - Allows local endpoint calls with `OPENAI_BASE_URL` and a local placeholder API key.
- `server_analysis_workspace/patchcourt_4gpu_smoke_20260524/launch_external_candidate_materialization.py`
  - Forwards `PATCHCOURT_OPENAI_BASE_URL` and `PATCHCOURT_OPENAI_API_KEY`.
  - Exports those variables for the remote worker process.
  - Adds configurable `PATCHCOURT_LAUNCH_TIMEOUT_SEC`.
- `scripts/patchcourt_external_diff_normalizer.py`
  - New append-only normalizer for raw independent-model diffs.
  - Applies GNU `patch` fuzz, then re-exports a strict git diff.
  - Records `normalization_status`, `normalization_strategy`, and original diff provenance.
- `scripts/patchcourt_candidate_apply_visible_worker.py`
  - Adds an auditable fallback `git apply --ignore-space-change` only for normalized candidates.
  - Records `apply_strategy` plus normalization metadata.

## Frozen-30 Materialization

### Pilot 27

- Raw materialization queue: `candidate_external_materialization_20260526_234715`
- Result:
  - `26/27` model diffs materialized.
  - `1/27` blocked because the model response contained no extractable unified diff.
  - `27` no-op controls carried.

### Smoke 3

- Raw materialization queue: `candidate_external_materialization_20260527_003423`
- Result:
  - `2/3` model diffs materialized.
  - `1/3` blocked because the model response contained no extractable unified diff.
  - `3` no-op controls carried.

### Total

- Raw independent Qwen GGUF diffs: `28/30`.
- Raw blocked tasks: `2/30`.

## Apply, Visible, Probe, BDC, Ledger

### Raw Strict Diff Lane

- Pilot raw apply queue: `candidate_apply_visible_queue_20260527_003849`
  - `26` model diffs all failed strict `git apply --check`.
  - `1` model task not materialized.
  - `27` no-op controls applied.
- Pilot raw probe queue: `generic_issue_probe_queue_20260527_004024`
  - `0` probe results because no model candidate reached visible-pass selection.

### Normalized Pilot Lane

- Normalization queue: `candidate_external_diff_normalization_20260527_005000`
  - `6` model diffs normalized with GNU patch fuzz and re-export.
  - `20` model diffs failed fuzz normalization.
  - `1` model task remained non-materialized.
  - `27` controls carried.
- Normalized apply queue: `candidate_apply_visible_queue_20260527_005019`
  - `6` normalized model candidates applied.
  - Applied model tasks:
    - `pytest-dev__pytest-11148`
    - `pylint-dev__pylint-7114`
    - `pydata__xarray-4094`
    - `psf__requests-2148`
    - `mwaskom__seaborn-2848`
    - `pylint-dev__pylint-5859`
  - `1` model candidate reached compatible visible-pass:
    - `mwaskom__seaborn-2848`
- Probe queue with no-op controls included: `generic_issue_probe_queue_20260527_005511`
  - `17` probe results.
- BDC queue: `bdc_queue_20260527_005531`
  - `0` BDCs.
- Evidence ledger queue: `evidence_ledger_queue_20260527_005602`
  - `0` ledger records because no BDCs were emitted.

### Smoke Normalized Lane

- Normalization queue: `candidate_external_diff_normalization_20260527_005300`
  - `0` normalized model candidates.
  - `2` model diffs failed fuzz normalization.
  - `1` model task remained non-materialized.
- Apply queue: `candidate_apply_visible_queue_20260527_005250`
- Probe queue: `generic_issue_probe_queue_20260527_005312`
  - `0` probe results from model candidates.

## Interpretation

This run resolves the previous RQ4 infrastructure blocker: PatchCourt now has a real, non-Codex, local open-model candidate source wired through an OpenAI-compatible endpoint and evaluated on the same frozen 30 tasks.

It does not yet resolve the RQ4 evidence blocker. Qwen2.5-Coder-7B GGUF direct unified-diff generation is too weak in this prompt format:

- raw model diff extraction is good enough (`28/30`),
- strict patch applicability is poor (`0/28` raw strict apply),
- fuzz normalization recovers only `6/28`,
- visible-pass recovery is only `1/30`,
- BDC yield is `0`.

## Decision

Do not report this run as an independent model baseline with behavioral disagreement evidence. Report it as:

> independent open-model endpoint connected and evaluated; direct diff prompting fails the applicability/visible-pass gate on frozen 30.

The next independent-source attempt should use an apply-aware candidate generator, not more blind direct-diff sampling:

1. Add model self-repair after `git apply --check` failure.
2. Prefer structured edit formats such as search/replace blocks or whole-function replacement, then generate diffs programmatically.
3. Use a smaller context but include exact target snippets and line anchors.
4. Keep the current normalization lane as an auditable fallback, not as the main generation strategy.
