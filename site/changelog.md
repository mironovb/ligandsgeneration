---
layout: default
title: Changelog
nav_order: 8
---

# Changelog
{: .no_toc }

{% include status.html %}

A running log of changes to this tracker. Newest first.

- **2026-05-26** — **Audit, hardening & living-tracker setup.** Re-checked every number
  against `VERIFICATION_REPORT.md` and produced `SITE_AUDIT.md` (each headline number →
  page → source). One framing fix: the Ln–donor distance (2.61 → 2.43 Å) on Strategy now
  carries the same *unverified* flag it already had on Methods. Confirmed no revert to the
  discredited "side-chain elaboration" framing, the 60.5% cross-bond rate stated as a
  geometry sensitivity check (**not** chemical fusion), and the three Kulik papers cast as
  coordination-*representation* inputs to Track B (**not** generation methods). Added
  `HOW_TO_UPDATE.md` and a `Makefile` (one-command build/serve); final
  `bundle exec jekyll build` is clean (0 errors / 0 warnings).
- **2026-05-26** — **Content written from verified facts.** All pages filled in:
  Background (objective + grouped key papers, incl. the three Kulik papers), Methods
  (architecture, the 7→11 zero-pad lanthanide adaptation, CSD pipeline, training setup),
  Results (training curve, RePaint sweep, the metric caveat, the de-novo design test),
  the full Experiment Log (every sbatch run), Strategy (two-track roadmap), and
  Conclusions. Added three SVG figures built from verified numbers
  (`assets/figures/`). Numbers sourced from `VERIFICATION_REPORT.md`; papers/strategy
  from `LITERATURE_AND_STRATEGY.md`.
  **Current state:** fine-tuning works (val_loss 977.8 → 49.9, ~95% ↓); mask-1 completion
  works (126 valid, xTB 38/41 = 92.7%); RePaint yield rises monotonically to 5.20% (r=5
  is the working point); **de-novo design fails (0 valid / 6,300)** on nitrogen-valence
  violations. Two corrections to `PROJECT_OVERVIEW.md` are reflected throughout: the
  completed **r=10 = 57/1,500 = 3.80%** (not 19/300/6.33%), and total valid = **171**
  (or 210 with r=20), not 133. Claims not checkable from the download (CSD-pipeline
  counts, exact architecture internals, visual/geometry inspection) are tagged
  *unverified*.
- **2026-05-26** — Site skeleton scaffolded (Jekyll + just-the-docs): `_config.yml`, `Gemfile`, navigation/page stubs, `_data/experiments.yml` + `_data/papers.yml`, status include, and changelog. Page content pending (Prompt 4).
