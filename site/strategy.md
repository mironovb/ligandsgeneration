---
layout: default
title: Strategy
nav_order: 6
---

# Strategy — two-track roadmap
{: .no_toc }

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

## The diagnosis behind the plan

Prof. Jiang sent three papers from the **Kulik group** (MIT Chemical Engineering) — see
[Background](background.html#prof-jiangs-reading-list--the-three-kulik-group-papers). The
single most telling fact about them: **all three characterize, predict, or classify
metal–ligand coordination — none of them *generate*.** Read together, they locate the
exact capability our generative model lacks (a learned model of *what a valid coordination
environment is*) and show it can be learned from CSD data at high accuracy. Paper 3 even
names the limitation of our model's lineage by name: generative TMC models "requiring
user-specified metal–ligand coordination and assuming a constant coordination mode."

{: .note }
> **In one line.** Our model *generates geometry and infers chemistry*; a
> coordination-aware model *fixes chemistry first and then realizes geometry*. That
> inversion is the whole difference between our **0 / 6,300** de-novo rate and pydentate's
> reported **75% de-novo DFT success**. (Claims about Prof. Jiang's intent below are
> labeled *interpretation*, following `LITERATURE_AND_STRATEGY.md`.)

The plan is two tracks: **publish the adaptation, the dataset, and the diagnostic now
(Track A)**, and **build a coordination-aware, rare-earth-native platform next (Track B)**.

## Track A (now) — the multi-LigandDiff lanthanide-adaptation paper

A single negative result is unlikely to land on its own. So Track A is **not** "we tried
de-novo design and it failed" — it is a methods-adaptation paper resting on **a reusable
dataset and four standing results, with the de-novo failure as one sharp diagnostic among
them**. Every claim is logged and verified (see [Results](results.html)).

- **Dataset — a validated lanthanide CSD set.** A license-free pymatgen/ASE pipeline turns
  53,333 CIFs into **9,306 training-ready complexes** (6,563 O/N-donor) plus a
  216,509-instance / 54,946-SMILES ligand inventory, and **reproduces the Jiang group's own
  published CSD trends** (donor dominance, the lanthanide contraction, the CN = 8 peak). A
  reusable artifact and a contribution in its own right — see [Dataset](dataset.html).
- **Adaptation — first f-block / high-CN diffusion model.** *First adaptation of a 3D
  equivariant diffusion model to f-block (lanthanide) coordination chemistry and to high
  coordination numbers (CN 7–10)* — the base model was d-block, CN ≤ 6 only, a regime the
  Kulik tools also do not cover. The change is minimal (one input layer reshaped 7 → 11,
  zero-padded); fine-tuning drove val_loss **977.8 → 49.9 @ epoch 48 (~95% ↓)**, clean
  early-stop, sampling 0.97 valid-ligand / 0.94 connected.
- **Completion — works, and we validate it.** mask 1 completion yields **126 valid**
  Eu(TMMA)₂(NO₃)₃ structures in the fixed pocket, **xTB-stable (38/41 = 92.7%)** — the model
  learned valid *local* lanthanide coordination geometry. *To make this a hard positive
  rather than a soft one, Track A adds a **DFT-validated completion showcase*** (PBE0-D3/
  def2-TZVP, Stuttgart ECP28MWB on Eu, SMD dodecane; ORCA templates ready) on the top
  candidates. **Not yet run** — see the experiment list below.
- **Yield engineering — RePaint.** Inference-time resampling raises yield **monotonically:
  r = 1 → 5 → 10 → 20 = 1.16 → 3.40 → 3.80 → 5.20%**, **171 valid** total (r1+r5+r10) or
  **210** with r = 20, denticity-match peaking at r = 5 (15.3%). An honest
  yield-vs-resampling trade-off: more resampling buys yield, not validity.
- **De-novo diagnostic — fails, with a mechanism (one result, not the paper).** maskall =
  **0 valid / 6,300**, with **~100% nitrogen explicit-valence rejections** — a clean,
  citable failure mode that motivates Track B. *To make the cliff rigorous rather than
  anecdotal*, Track A completes the **degradation curve** with a dedicated **mask-2 run**
  (the current mask 2 = 4 is only what survived a 4 h cutoff), turning **126 → 4 → 0 → 0**
  into a measured curve. It sets up Track B — it does not have to carry the paper alone.

{: .fails }
> **What to leave out (credibility).** The `paper/` "Prompts 1–10" artifacts
> (context-density ablation, cross-architecture table, projection-stack "6.4%", "DFT
> submitted") have **no supporting job logs and partly contradict the real xTB data** —
> omit them. The DFT showcase above is a *planned* run: do **not** describe DFT as already
> done until ORCA outputs exist. Keep the paper to what actually ran, plus the two
> sanctioned new runs below.

**Two experiments remain to finish Track A:**

1. **Dedicated mask-2 run** (3 of 5 ligands hidden), to completion — fills the gap between
   mask 1 (works) and mask 3 (0) and makes the degradation curve rigorous. Cheap compute.
2. **DFT-validated completion showcase** — PBE0-D3/def2-TZVP on the top mask-1 candidates,
   upgrading "xTB-stable" to "DFT-confirmed" and turning completion into a hard positive.

**Honest one-line abstract.** *We curate a validated lanthanide CSD dataset and adapt a 3D
equivariant diffusion model to f-block coordination chemistry and high coordination numbers
(CN 7–10): the model completes lanthanide coordination spheres reliably (xTB-stable, with a
DFT showcase) while inference-time resampling tunes yield — but it cannot yet design spheres
de novo, a specific, diagnosable valence-composition gap that motivates coordination-aware
generation.* A methods-adaptation + dataset paper with a sharp diagnostic, not a lone
negative.

## Track B (next) — a coordination-aware, rare-earth-native platform

Design principles to borrow, with provenance.

### From the Kulik papers

1. **Coordination-aware representation** (Papers 1–3). Learn denticity (donor count) and
   donor-atom identity from molecular graphs — but **extend past pydentate's CN ≤ 6 to the
   lanthanide CN 7–10 regime**, which their models explicitly exclude.
2. **Predict-then-build, not generate-and-hope** (Paper 1). Produce a *valence-valid ligand
   graph* (SMILES-level, so the N-valence error is impossible by construction), predict its
   donor set, then place it around the Ln with a constrained 3D builder. Benchmark:
   pydentate hit 1.50 Å RMSD vs. CSD and 88% DFT success *when coordination was correct*.
3. **Hard valence / CN / charge constraints inside the sampler** (Paper 1 + the repo's
   projection module). If a 3D generative stage is kept, enforce constraints *during*
   denoising (projection / type-masking), not as post-hoc rejection of 99.99% of attempts.
4. **Hemilability & multi-shell awareness** (Papers 2–3). For separations, denticity
   flexibility is a *feature* (extractants must bind *and* release); encode the four
   hemilability types, predict alternative modes, and model beyond the first shell. The
   ΔE_c criterion offers a ready-made plausibility filter.
5. **CSD-grounded, synthesizability-biased data** (all three). Train on experimentally
   observed complexes so candidates are synthesizable by construction.

### From rare-earth coordination chemistry

6. **Hard-donor preference.** Ln³⁺ are hard Lewis acids → bias donor sets to O and N
   (the project already used an O/N-only subset). Encode HSAB as a prior.
7. **High coordination numbers (8–10) as a structural prior** — the regime pydentate
   omits; the reference Eu(TMMA)₂(NO₃)₃ is CN = 10. The platform must be CN-flexible and
   first-shell-saturating by design.
8. **Lanthanide contraction as the selectivity handle.** Ln–donor distance contracts
   smoothly (the project's CSD pipeline reports 2.61 Å (La) → 2.43 Å (Lu) — an *unverified*
   pipeline figure, consistent with the lanthanide contraction; see
   [Methods](methods.html#the-csd-data-pipeline)). Since *selectivity* between adjacent
   lanthanides is the actual goal, conditioning on target Ln lets the model reason about
   *differential* binding, not just single-complex stability.
9. **Predominantly ionic, non-directional Ln–L bonding.** Geometry is governed by
   denticity + sterics + charge balance rather than ligand-field directionality — so the
   metal coordination can be treated flexibly, *provided* charge neutrality and first-shell
   saturation are respected.
10. **Counter-ions / solvent in the first shell.** Nitrate and water routinely co-coordinate
    (Jiang group, *Inorg. Chem. Commun.* 2025; the reference has 3 bidentate nitrates).
    Model the *full* first shell, not just the designed organic ligand.
11. **Spec-conditioned generation** (Jiang's stated vision). Make the conditioning target
    explicit — *"2 N + 3 O donors, neutral charge, CN 8, Eu"* — i.e. denticity/donor
    composition as the control knob, which is exactly what a coordination-aware
    representation makes addressable.

## Open questions for Prof. Jiang

1. **Track A scope / stopping point.** Track A now bundles the dataset, the adaptation,
   validated completion, the RePaint trade-off, and the de-novo diagnostic — with two runs
   left (a mask-2 completion and a DFT-validated completion showcase). Is that the right
   stopping point for a first paper, or would you cut or add anything? (The DFT showcase is
   the main remaining compute cost — we have only ORCA *templates*, no DFT outputs yet.)
2. **Track B architecture — which bet?** **Graph-level predict-then-build** (pydentate-style,
   valence-safe by construction) or **constrained 3D generation** (keep diffusion, add hard
   valence/CN/charge projection)? Different engineering programs; shouldn't be hedged.
3. **What is the generation *objective*?** Is the primary target **selectivity**
   (differential binding of adjacent lanthanides — Eu vs. Gd, La vs. Lu) rather than
   single-complex stability? If so, the platform must condition on metal *pairs* and a
   selectivity loss.
4. **Build vs. reuse the Kulik stack.** Extend the open-source `pydentate` to f-block /
   CN 7–10 / hard-donor sets, or build the coordination-prediction layer from scratch on
   the Jiang group's own ~29,891-complex lanthanide dataset?
5. **How central is hemilability?** Should Track B explicitly model denticity switching
   (bind-and-release for extractants), or is equilibrium first-shell selectivity sufficient
   for v1?
