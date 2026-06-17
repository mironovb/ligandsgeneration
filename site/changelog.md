---
layout: default
title: Changelog
nav_order: 8
---

# Changelog
{: .no_toc }

{% include status.html %}

A running log of changes to this tracker. Newest first.

- **2026-06-16** — **Added an [AI Context](ai-context.html) export.** A new page bundles every
  content page into one Markdown document — with the `_data`-driven tables (experiment log,
  paper list) fully expanded and the *unverified* / *negative-result* callouts preserved as
  labels — and offers **copy-to-clipboard** and **download-as-`.md`**. The same content is
  served as [`/llms-full.txt`]({{ '/llms-full.txt' | relative_url }}) with a short
  [`/llms.txt`]({{ '/llms.txt' | relative_url }}) index ([llms.txt](https://llmstxt.org/)
  convention). Generated at build time by `_plugins/ai_context.rb`, so it always matches the
  published site. Tooling only — no results changed.
- **2026-05-29** — **Added a [Code Review](code-review.html) page (codebase audit).** A
  static, sourced read of the `multi_LigandDiff` repo asking two things: where the
  validity/sampling pipeline can be wrong, and the cheapest changes toward a positive de-novo
  result. Headline findings, each cited to code or job logs: (1) the de-novo **0 / 6,300** is
  scored by the *same* brittle distance-based gate the [metric caveat](results.html#the-metric-caveat)
  already distrusts, and the maskall log holds only **5** sanitize errors — so ~6,295 attempts
  failed *silently* at the geometric gate, not at nitrogen valence (the "100% nitrogen" stat is
  from a different, mask-1/2-dominated run); (2) `make_mol_openbabel` rebuilds atoms by **symbol
  only**, dropping formal charges, so a correctly-built **nitrate** (the reference has three) is
  *guaranteed* to fail `Chem.SanitizeMol` — which both explains why mask 1 "works" and means part
  of the **0** is the checker, not the model; (3) `denticity_partitions(10)` over-generates — 19
  of 42 partitions are chemically impossible — inflating the 6,300 denominator; (4) the de-novo
  task gives denticity but **no composition**, and a *random* atom budget; (5) the exclusion-shell
  projection's `d_min` (1.3–1.5 Å) sits **below** the bond-detection cutoff (1.7–2.0 Å) and is a
  no-op in the bare-metal case (and was never used in a trusted run); (6) train/generate/validate
  use **three different bond conventions**. Affirms the *verified positive* that the Ln transfer
  loaded cleanly (227/231 layers). Cross-linked from [Results](results.html) and the home nav. No
  results were re-run; this is an analysis, not new data.
- **2026-05-26** — **Dataset added; Track A broadened; numbers solidified; files
  reorganized.** Added a **[Dataset](dataset.html)** page documenting the CSD curation
  (53,333 CIFs → **9,306** training complexes, 6,563 O/N-only; 216,509 ligand instances /
  54,946 unique SMILES), validated against the Jiang group's ICC 2025 / Sci. Rep. analyses
  and backed by committed artifacts `assets/data/summary_by_element.csv` and
  `assets/data/cif_analysis_report.txt`. **Track A** reframed from a single de-novo negative
  into a five-part paper — dataset + first f-block/high-CN adaptation + validated completion
  (with a planned DFT showcase) + RePaint yield + the de-novo diagnostic — with a mask-2 run
  and a DFT-validated completion showcase as the two runs left to finish it. **Corrections
  solidified in place:** `PROJECT_OVERVIEW.md` now carries r = 10 = **57/1,500 = 3.80%** and
  total valid **171** (210 incl. r = 20); the "19/300/6.33% / 5.5× / 133" figures are gone,
  not merely footnoted. Cluster identifiers genericized (no institution named). Repo
  reorganized: internal docs → `reports/`, data artifacts → `site/assets/data/`.
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
