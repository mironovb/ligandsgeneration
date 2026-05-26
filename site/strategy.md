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

The plan is two tracks: **publish the honest finding now (Track A)**, and **build a
coordination-aware, rare-earth-native platform next (Track B)**.

## Track A (now) — one honest multi-LigandDiff paper

The minimal, publishable story — every claim below is logged and verified (see
[Results](results.html)):

- **Headline novelty.** *First adaptation of a 3D equivariant diffusion model to f-block
  (lanthanide) coordination chemistry and to high coordination numbers (CN 7–10).* The
  base model was d-block, CN ≤ 6 only — genuinely new ground, and a regime the Kulik tools
  also do not cover.
- **Result 1 — completion works.** Fine-tuning drove val_loss **977.8 → 49.9 @ epoch 48
  (~95% ↓)**, clean early-stop, sampling 0.97 valid-ligand / 0.94 connected. mask 1
  completion yields **126 valid** structures in the fixed pocket, **xTB-stable (38/41 =
  92.7%)**. → The model learned valid *local* lanthanide coordination geometry given
  context.
- **Result 2 — de-novo design fails, with a mechanism.** maskall = **0 valid / 6,300**;
  the scaffold gradient (**126 → 4 → 0 → 0** for mask 1/2/3/all) and the **~100% nitrogen
  explicit-valence rejections** give a clean, citable explanation. *This is the paper's
  most valuable scientific content,* and it sets up Track B.
- **Result 3 — RePaint yield engineering.** Inference-time resampling raises yield
  **monotonically: r = 1 → 5 → 10 → 20 = 1.16 → 3.40 → 3.80 → 5.20%**, with denticity-match
  peaking at r = 5 (15.3%). An honest yield-vs-resampling trade-off: more resampling buys
  yield, not validity.

{: .caveat }
> **Use the corrected numbers.** completed r = 10 = **57 / 1,500 = 3.80%** (not the
> 19/300/6.33% in `PROJECT_OVERVIEW.md`), and total valid ≈ **171** (r1+r5+r10) or **210**
> with r = 20 — *not* "133" or "5.5×".

{: .fails }
> **What to leave out (credibility).** The `paper/` "Prompts 1–10" artifacts
> (context-density ablation, cross-architecture table, projection-stack "6.4%", "DFT
> submitted") have **no supporting job logs and partly contradict the real xTB data** —
> omit them. Do **not** claim DFT validation as done; only ORCA *templates* exist. Keep
> the paper to what actually ran.

**Honest one-line abstract.** *A 3D diffusion model can be fine-tuned to complete
lanthanide coordination spheres but cannot design them de novo; the failure is a specific,
diagnosable coordination-validity (valence) gap, and inference-time resampling buys yield
but not validity — motivating coordination-aware generation.* This is a legitimate
methods-adaptation + diagnostic ("informative negative") contribution.

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

1. **Track A scope / stopping point.** Is the diagnostic result (completion works; de-novo
   fails on valence) publishable on its own as a methods-adaptation + cautionary study, or
   does it need at least one **DFT-validated completion showcase** before writing? (We have
   *not* run DFT — only ORCA templates exist — so this decides remaining compute.)
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
