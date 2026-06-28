# ICSE 2027 IEEEtran Draft (Phase 30 structured patch-record listing, 2026-06-28)

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
The Phase 30 build is 12 pages after replacing the compact edit-record code block with a formal structured patch-record listing, while preserving the quantitative Figures 1-4, the Phase 24 quantitative result summary, and 66 cited references.
