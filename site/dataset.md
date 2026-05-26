---
layout: default
title: Dataset
nav_order: 2.5
---

# Dataset — the lanthanide CSD curation
{: .no_toc }

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

The first piece of work on this project — done before any model adaptation — was building
the **training dataset** from scratch. Because the host institution has no CSD Python API
license, a custom pipeline (pymatgen + ASE) parses raw CIFs, identifies donor atoms,
decomposes each complex into individual ligands, extracts SMILES, and filters to a
model-ready training set. The full run took ~168 minutes and produced the
[analysis report](#downloads) and [per-element CSV](#downloads) linked below.

{: .works }
> **This curation is a standalone contribution, and it is verifiable.** Its headline
> counts (below) come from the committed analysis report and `summary_by_element.csv` —
> not from a number that "appears in no log." It also **reproduces the Jiang group's own
> published CSD trends** (next section), which is what gives confidence in the home-built,
> license-free pipeline.

## From 53,360 CIFs to 9,306 training complexes

| Stage | Count | Notes |
|---|---:|---|
| CIF files received (Shicheng Li, CSD v5.46) | 53,360 | ICC 2025 reports 53,370 total Ln complexes in CSD v5.46 |
| Successfully parsed | 53,333 (99.9%) | 27 parse failures |
| Mononuclear complexes | 31,979 (60.0%) | the modelable single-center subset |
| multi-LigandDiff-compatible | 36,596 (68.6%) | elements in {C,N,O,F,P,S,Cl,Br} around the Ln |
| **Training candidates (CN 7–10)** | **9,306 (17.4%)** | mononuclear ∩ CN 7–10 ∩ compatible elements |
| — of which O/N-donor only | 6,563 (12.3%) | the hard-donor subset Ln³⁺ prefer |

## Validation against the Jiang group's published CSD analyses

The pipeline uses **distance-based** bond detection (no CSD coordinate-bond annotations),
so exact counts differ slightly — but every published trend reproduces:

| Quantity | This pipeline | Jiang group papers |
|---|---|---|
| Total Ln complexes parsed | 53,333 / 53,360 | 53,370 (ICC 2025) |
| Mononuclear complexes | 31,979 | 29,891 (ICC 2025) |
| Donor distribution | 65.2% O, 17.7% N, 14.4% C | O-dominated across the series (Sci. Rep. 2024) |
| Ln–donor distance trend | 2.61 Å (La) → 2.43 Å (Lu) | 2.62 → 2.41 Å (lanthanide contraction) |
| CN distribution peak | CN = 8 (9,658), then CN = 9 (6,529) | CN = 8 dominant from Sm onward (Sci. Rep. 2024) |
| Common first-shell inorganics | water 8.0%, nitrate 3.7% (of ligand instances) | nitrate & water routinely co-coordinate (ICC 2025) |

The ~7% gap in the mononuclear count (31,979 vs 29,891) is attributed to distance-based
detection vs. CSD-API coordinate bonds; the *trends* — donor dominance, the contraction,
the CN = 8 peak — match, which is what validated the pipeline.

## Coordination-number distribution

Across all parsed complexes, coordination number peaks at **CN = 8 (9,658)**, then
**CN = 9 (6,529)** and **CN = 6 (6,355)** — the lanthanide preference for high CN that the
transition-metal base model (CN ≤ 6) never saw. The training window **CN 7–10** is exactly
where the f-block diverges from the d-block.

| CN | 5 | 6 | 7 | **8** | 9 | 10 | 11 | 12 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Complexes | 5,594 | 6,355 | 5,521 | **9,658** | 6,529 | 3,336 | 2,291 | 1,842 |

Training candidates fall in the CN 7–10 band: **CN 7 = 2,396 · CN 8 = 3,631 · CN 9 = 2,182
· CN 10 = 1,097** (total 9,306).

## Per-element summary

All 14 trainable lanthanides (Pm excluded — no stable isotope, essentially absent from the
CSD). Full columns — parse rates, CN 8/9 counts, total ligand instances — are in
[`summary_by_element.csv`](#downloads).

| El | Total CIFs | Mononuclear | Avg CN | Avg Ln–donor (Å) | Train (CN 7–10) | O/N-only | Unique ligands |
|---|---:|---:|---:|---:|---:|---:|---:|
| La | 4,168 | 2,602 | 7.02 | 2.607 | 768 | 580 | 6,536 |
| Ce | 3,436 | 2,123 | 7.29 | 2.550 | 535 | 389 | 5,390 |
| Pr | 2,368 | 1,287 | 7.17 | 2.562 | 381 | 287 | 3,803 |
| Nd | 4,313 | 2,647 | 7.17 | 2.550 | 747 | 510 | 6,740 |
| Sm | 4,503 | 2,818 | 7.12 | 2.552 | 737 | 385 | 6,946 |
| Eu | 6,348 | 3,538 | 7.10 | 2.498 | 1,258 | 989 | 9,882 |
| Gd | 5,057 | 2,770 | 7.21 | 2.471 | 741 | 568 | 7,537 |
| Tb | 4,921 | 2,629 | 7.25 | 2.455 | 830 | 636 | 7,636 |
| Dy | 6,509 | 3,674 | 7.26 | 2.440 | 1,124 | 840 | 10,128 |
| Ho | 1,858 | 1,041 | 6.98 | 2.430 | 310 | 223 | 3,060 |
| Er | 3,141 | 1,945 | 7.05 | 2.422 | 589 | 410 | 4,968 |
| Tm | 822 | 539 | 7.11 | 2.444 | 159 | 99 | 1,377 |
| Yb | 4,195 | 3,069 | 6.76 | 2.444 | 808 | 462 | 6,596 |
| Lu | 1,721 | 1,297 | 6.83 | 2.434 | 319 | 185 | 2,854 |
| **Total** | **53,360** | **31,979** | — | — | **9,306** | **6,563** | — |

Eu and Dy dominate the training candidates (1,258 and 1,124) — convenient, since
**Eu(TMMA)₂(NO₃)₃** is the project's [reference complex](background.html#the-reference-complex).
The average Ln–donor distance contracts from **2.607 Å (La)** toward **~2.43 Å** at the
heavy end — the lanthanide contraction, and the physical handle that makes adjacent-Ln
*selectivity* possible.

## Ligand inventory

Decomposition yields **216,509 coordinating ligand instances** spanning **54,946 unique
SMILES**. Denticity is dominated by mono- and bidentate ligands (1-dentate 136,199;
2-dentate 36,230; 3-dentate 28,191). The most common coordinating motifs:

| Motif | Instances | Share |
|---|---:|---:|
| 1-donor O organic | 37,124 | 17.1% |
| oxo | 31,198 | 14.4% |
| water | 17,398 | 8.0% |
| amine | 11,129 | 5.1% |
| pyridine | 10,794 | 5.0% |
| nitrate | 8,091 | 3.7% |
| imine | 7,557 | 3.5% |
| amide | 5,530 | 2.6% |
| β-diketone | 3,943 | 1.8% |
| phosphine oxide | 3,558 | 1.6% |

Crucially, the **extractant-relevant chemistries are all present** — amides (the
diglycolamide/diamide family, like the reference TMMA), β-diketones, phosphine oxides, and
phenanthroline derivatives — so the dataset can in principle teach a model the molecular
classes that matter for real rare-earth separations.

## Training-sample budget

The 9,306 candidates average **4.6 ligands each** and **~23 masking combinations** per
complex, forming a pool of **~212,000** maskable training samples (~149,586 for the
O/N-only subset).

{: .note }
> **~212,000 vs. ~85,760.** The ~212,000 figure is the *maskable pool* the curated dataset
> can produce. The fine-tune itself consumed **~85,760 samples per epoch** (335 steps ×
> batch 256, verified from the training logs — see
> [Methods → Training](methods.html#training-setup)). The two numbers describe different
> things: the augmentation *available* vs. the augmentation *applied per epoch*.

## Downloads

- [`summary_by_element.csv`]({{ '/assets/data/summary_by_element.csv' | relative_url }}) —
  per-element breakdown (17 columns: parse rates, CN 7/8/9/10 counts, avg donor distance,
  training candidates, ligand totals) for all 14 lanthanides.
- [`cif_analysis_report.txt`]({{ '/assets/data/cif_analysis_report.txt' | relative_url }}) —
  the full pipeline report (overall summary, CN and donor distributions, denticity, ligand
  types, top-30 SMILES, incompatible-element tally, parse-failure reasons).

See [Methods → The CSD data pipeline](methods.html#the-csd-data-pipeline) for the five
processing stages, and [Strategy → Track A](strategy.html) for how this dataset anchors the
Track A paper.
