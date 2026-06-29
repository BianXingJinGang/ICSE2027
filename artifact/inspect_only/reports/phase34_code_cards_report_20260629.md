# Phase 34 Code-Facing Probe Cards Report

Date: 2026-06-29

## Objective

This package version includes additional code-facing public-probe examples in the manuscript. The change is intended to make the evidence chain easier to inspect in an ICSE-style paper without changing the artifact data.

## Changes

- Added a two-panel code-facing probe figure to `latex/main.tex` and `latex/main.pdf`.
- Left panel: `SymPy-23117` issue-code reproducer with a `3 pass / 1 fail` candidate split.
- Right panel: `Seaborn-3407` Qwen stress probe with a `1 pass / 4 fail` split for the strongest issue-specific Qwen case.
- Kept the existing core PatchCourt evidence record in the manuscript.
- Kept all result tables, certificate files, Level 1 verifier inputs, and claim boundaries unchanged.

## Validation

- Artifact Level 1 verifier: PASS, all `44/44` checks.
- Artifact LaTeX rebuild: PASS, 12 pages.
- ICSE acceptance audit: PASS, `103.0/103`.

## Claim Boundary

This is a presentation-only artifact refresh. The selected certificate-producing path, `17/30` false-acceptance result, `26/30` specification-debt result, `6/10` main upgrade result, and Qwen boundary counts remain unchanged.
