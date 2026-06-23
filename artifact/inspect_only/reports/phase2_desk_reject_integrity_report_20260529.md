# Phase 2 Desk-Reject Integrity Report (2026-05-29)

## Objective

Remove predictable desk-reject risks before scientific polishing: reference integrity, double-anonymous compliance, secrets, and PDF metadata.

## Active Surface

- IEEE manuscript: `paper/icse2027/latex_ieee_20260529/main.tex`
- IEEE PDF: `paper/icse2027/latex_ieee_20260529/main.pdf`
- IEEE BibTeX: `paper/icse2027/latex_ieee_20260529/references.bib`
- Anonymous artifact root checked: `paper/icse2027/artifact_bundle_anonymous_20260528/inspect_only_20260528/`

## Reference Integrity

Every BibTeX entry was checked against a public source for title/authors/venue/year/DOI/URL.

| Key | Source Checked | Status | Action |
| --- | --- | --- | --- |
| `jimenez2024swebench` | OpenReview ICLR 2024 page: https://openreview.net/forum?id=VTF8yNQM66 | PASS | Switched URL from arXiv to OpenReview; kept ICLR venue. |
| `yang2024sweagent` | NeurIPS 2024 proceedings page: https://papers.nips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html | PASS | Switched URL to NeurIPS proceedings and DOI to `10.52202/079017-1601`. |
| `zhang2024autocoderover` | DOI record: https://doi.org/10.1145/3650212.3680384 | PASS | Replaced arXiv DOI with ACM DOI; added ISSTA 2024 proceedings and pages `1592--1604`. |
| `wang2025swebenchcorrectness` | ICSE 2026 page and DOI: https://conf.researchr.org/details/icse-2026/icse-2026-research-track/59/Are-Solved-Issues-in-SWE-bench-Really-Solved-Correctly-An-Empirical-Study and https://doi.org/10.1145/3744916.3764576 | PASS | Switched URL to DOI and made the ICSE 2026 proceedings venue explicit. |
| `ye2021automated` | Springer article page: https://link.springer.com/article/10.1007/s10664-020-09920-w | PASS | No change needed. |
| `qi2015plausibility` | DOI record: https://doi.org/10.1145/2771783.2771791 | PASS | Changed from MIT tech report to ISSTA 2015 proceedings; added pages `24--36`; corrected author to `Martin C. Rinard`. |
| `smith2015overfitting` | DOI record: https://doi.org/10.1145/2786805.2786825 | PASS | No change needed. |
| `barr2015oracle` | DBLP/DOI record: https://dblp.uni-trier.de/rec/journals/tse/BarrHMSY15.html and https://doi.org/10.1109/TSE.2014.2372785 | PASS | No change needed. |
| `pezzezhang2014oracles` | ScienceDirect chapter page: https://www.sciencedirect.com/science/article/abs/pii/B9780128001608000012 | PASS | Corrected second author from `Michal Young` to `Cheng Zhang`; renamed cite key from `pezzeyoung2014oracles` to `pezzezhang2014oracles`. |

## Build Validation After Reference Fixes

Command sequence:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Validation:

- Page count: `7`.
- Undefined citations: none detected in final `main.log`.
- Undefined references: none detected in final `main.log`.
- Overfull boxes: none detected in final `main.log`.
- Remaining log noise: underfull boxes caused by IEEE two-column layout; not a blocking format error.

## Double-Anonymous Scan

Checked manuscript source for author fields, acknowledgments, emails, affiliations, local paths, and known machine/server identifiers.

Findings:

- `\author{\IEEEauthorblockN{Anonymous Authors}}` is the only author block.
- No author email or institution is present.
- No acknowledgments section is present.
- No local Windows path, server path, jump-host hostname/IP, username, or project-private connection topology appears in the manuscript source.
- PDF metadata contains no explicit author/title/subject/keywords field printed by `pdfinfo`; visible metadata is generic TeX/MiKTeX production metadata.

## Secret Scan

Critical regex scan over the active IEEE lane and anonymous artifact. The anonymous artifact copy omits the literal local-path and secret-fragment pattern used on the author machine; it is summarized here to avoid embedding environment-specific strings in the review package.

```powershell
rg -n -i "<critical-secret-and-identifying-path-patterns>" <active-paper-and-artifact-surfaces> --glob '!*.svg'
```

Result: PASS; no critical hits.

Broad scan notes:

- Expected non-secret policy text remains, e.g., statements saying the artifact excludes passwords/API keys.
- Expected environment variable names remain in artifact scripts/reports, e.g., `OPENAI_API_KEY`, `HF_TOKEN`, and `HUGGINGFACE_HUB_TOKEN`; these are configuration names, not secret values.
- LaTeX scratch logs contain local MiKTeX installation paths when present; scratch files are not submission artifacts and are removed before commit.

## PDF Metadata

`pdfinfo main.pdf` summary:

- Creator: `TeX`
- Producer: `MiKTeX pdfTeX-1.40.28`
- Pages: `7`
- JavaScript: `no`
- Encrypted: `no`
- Page size: letter
- No author-identifying metadata was printed by `pdfinfo`.

## Current Hashes

- `main.pdf`: `10435E91DBE368892BF6CFE9BDB7DB75AECE88E0D194F448EC85F0A933637B31`
- `main.tex`: `F54B61838FA21D6CC9D8688ECB1AC02291FEC63088761F42460DF227E633C9A2`
- `references.bib`: `030939A94CF60FE23AD689EC57C14FED877D9366E7D7ECC9740C3353DBC02A30`

## Phase 2 Result

PASS for the Phase 2 desk-reject gate. The active IEEE PDF is format-stable, references are source-checked, the manuscript is double-anonymous at the visible source/PDF level, and no critical secrets or identifying paths were found in the current submission surfaces.
