# ICSE 2027 IEEEtran Draft (Phase 28 abstract framing and example block, 2026-06-23)

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
The Phase 28 build is 12 pages after strengthening the abstract scale sentence and adding a compact structured edit-record code block, while preserving the quantitative Figures 1-4, the Phase 24 quantitative result summary, and 66 cited references.
