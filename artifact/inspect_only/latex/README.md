# ICSE 2027 IEEE Conference Draft (Phase 33 template-bound format, 2026-06-29)

This directory is the active IEEE conference-template lane for the ICSE 2027 Research Track submission.
It supersedes the historical ACM/acmart lane frozen during Phase 0.

Build target:

```powershell
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The artifact copy of `main.tex` is self-contained within the ZIP layout:
the paper figures are copied into `latex/figures/`, `IEEEtran.cls` is copied from the provided conference LaTeX template, and the manuscript paths match the active submission source.

Format target: `\documentclass[conference]{IEEEtran}` with `\IEEEoverridecommandlockouts` and the package/preamble pattern from the provided IEEE conference LaTeX template.
The Phase 33 build is 12 pages after binding the manuscript to the supplied template class file while preserving the Phase 32 core PatchCourt evidence record for the Matplotlib all-NaN false-acceptance running case. The listing directly names the visible-pass-is-not-oracle claim, visible-test acceptance gate, pre-freeze public-probe split, retained specification-debt audit label, post-freeze false-acceptance outcome, and inspect/rerank action while preserving the quantitative Figures 1-4, the Phase 24 quantitative result summary, and 66 cited references.
