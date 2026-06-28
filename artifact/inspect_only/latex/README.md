# ICSE 2027 IEEEtran Draft (Phase 32 core-claim code record, 2026-06-29)

This directory is the active IEEEtran lane for the ICSE 2027 Research Track submission.
It supersedes the historical ACM/acmart lane frozen during Phase 0.

Build target:

```powershell
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The artifact copy of `main.tex` is self-contained within the ZIP layout:
the paper figures are copied into `latex/figures/`, matching the active manuscript paths.

Format target: `\documentclass[10pt,conference]{IEEEtran}`.
The Phase 32 build is 12 pages after converting Figure 2 into a core PatchCourt evidence record for the Matplotlib all-NaN false-acceptance running case. The listing now directly names the visible-pass-is-not-oracle claim, visible-test acceptance gate, pre-freeze public-probe split, retained specification-debt audit label, post-freeze false-acceptance outcome, and inspect/rerank action while preserving the quantitative Figures 1-4, the Phase 24 quantitative result summary, and 66 cited references.
