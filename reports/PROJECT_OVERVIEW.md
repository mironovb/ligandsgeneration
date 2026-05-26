# Lanthanide Ligand Generation Project

**A conditional 3D generative model for lanthanide coordination complexes**

Bogdan Mironov (Berea College) · in collaboration with Prof. De-en Jiang (Vanderbilt)
Project documentation as of 23 May 2026

---

## Table of contents

1. [Motivation and objective](#1-motivation-and-objective)
2. [Scientific background and key papers](#2-scientific-background-and-key-papers)
3. [The base model: multi-LigandDiff](#3-the-base-model-multi-liganddiff)
4. [Phase 1 — CSD data pipeline](#4-phase-1--csd-data-pipeline)
5. [Phase 2 — Adapting the model to lanthanides](#5-phase-2--adapting-the-model-to-lanthanides)
6. [Phase 3 — Training](#6-phase-3--training)
7. [Phase 4 — Generation and the RePaint sweep](#7-phase-4--generation-and-the-repaint-sweep)
8. [Phase 5 — Validity analysis and the metric caveat](#8-phase-5--validity-analysis-and-the-metric-caveat)
9. [Phase 6 — The design test (completion vs de-novo)](#9-phase-6--the-design-test-completion-vs-de-novo)
10. [Consolidated results](#10-consolidated-results)
11. [Current conclusion](#11-current-conclusion)
12. [Open questions and next steps](#12-open-questions-and-next-steps)
13. [Infrastructure and reproducibility](#13-infrastructure-and-reproducibility)
14. [Reference list](#14-reference-list)

---

## 1. Motivation and objective

Lanthanide (Ln) separations — separating individual rare-earth elements from each
other — are a major industrial and strategic challenge. The chemistry that drives
selectivity lives in the **ligand**: the organic molecule that wraps around the metal
ion. Designing new ligands that bind one lanthanide more tightly than its neighbors is
slow, expensive, and largely driven by chemical intuition.

The objective of this project is to build a **conditional generative model** that can
propose new ligand structures for a specified lanthanide coordination environment. The
long-term vision, articulated by Prof. Jiang, is:

> Train a model on the tens of thousands of known Ln complexes in the Cambridge
> Structural Database (CSD), then ask it to generate ligands meeting a target
> specification — for example "generate ligands with 2 N donors and 3 O donors,
> neutral charge" — producing a pool of candidates that can be screened
> computationally and ultimately synthesized.

This document records the full arc of the work: data preparation, model adaptation,
training, generation experiments, and the diagnostic experiments that established what
the model can and cannot currently do.

---

## 2. Scientific background and key papers

### The application domain

- **Li, S.; Jansone-Popova, S.; Jiang, D.-e.** *Advancing Rare-Earth Separation by
  Machine Learning.* JACS Au, 2022. The foundational separations-ML paper from the
  Jiang group; the dataset and problem framing originate here.
- **Li, S.; Jansone-Popova, S.; Jiang, D.-e.** *Sci. Rep.* 2024. CSD-wide analysis of
  lanthanide coordination trends (donor distributions, coordination numbers across the
  series). Points toward ML/generative directions for ligand design.
- **Li, S.; Jansone-Popova, S.; Jiang, D.-e.** *Nitrate and water in the first
  coordination shells of lanthanide complexes.* Inorganic Chemistry Communications,
  2025, 179, 114844. Follow-up analysis of ~29,891 mononuclear Ln complexes.

### The generative-modeling methods

- **Jin, H.; Merz, K. M.** *multi-LigandDiff.* J. Chem. Theory Comput. (JCTC), 2024.
  DOI 10.1021/acs.jctc.4c00775. The base model adapted in this project (see §3). Builds
  on the same group's earlier **LigandDiff** (2023).
- **Hoogeboom, E. et al.** *Equivariant Diffusion for Molecule Generation in 3D (EDM).*
  ICML 2022. The diffusion formulation multi-LigandDiff is built on.
- **Jing, B. et al.** *Geometric Vector Perceptrons (GVP-GNN).* ICLR 2021. The
  equivariant network architecture used as the score function.
- **Lugmayr, A. et al.** *RePaint: Inpainting using Denoising Diffusion Probabilistic
  Models.* CVPR 2022. arXiv:2201.09865. The inference-time resampling technique ported
  into the sampler to improve yield (see §7).
- **Schneuing, A. et al.** *Structure-based drug design with equivariant diffusion
  models (DiffSBDD).* Nat. Comput. Sci., 2024. DOI 10.1038/s43588-024-00737-x. Precedent
  for applying RePaint to 3D molecular generation; reported ~3x yield improvement.
- **Christopher, J. et al.** *Projected Diffusion (constrained sampling).* NeurIPS 2024.
  arXiv:2402.03559. Hard geometric-projection technique implemented in the repo as a
  candidate fix for placement errors.

### The reference complex used throughout

- **Kravchuk, D. et al.** *Eu(TMMA)₂(NO₃)₃.* Eur. J. Inorg. Chem. (EurJIC), 2024.
  DOI 10.1002/ejic.202300632. CCDC VEDTAA01 / deposit 2296300. TMMA is
  N,N,N',N'-tetramethylmalonamide, a diamide chemically adjacent to the
  diglycolamide-type extractants relevant to separations. Used as the standard
  reference complex for all generation experiments: Eu center, 2 TMMA (each bidentate
  through two carbonyl O) + 3 nitrate (each bidentate) = 5 ligands, coordination
  number 10, 35 heavy atoms, cis configuration.

---

## 3. The base model: multi-LigandDiff

multi-LigandDiff is a **3D denoising diffusion model** for metal coordination
complexes. Given a metal center and (optionally) some fixed context ligands, it
generates the 3D coordinates and element identities of new ligand atoms.

### Architecture in brief

- **Type:** Equivariant Diffusion Model (EDM) with a Geometric Vector Perceptron graph
  neural network (GVP-GNN) as the score function.
- **Depth/width:** 5 message-passing layers, 192 hidden scalar features + 32 vector
  features each. ~3.8M parameters.
- **Graph:** fully connected (every atom to every atom, no distance cutoff). This tight
  coupling between context and generated atoms matters later.
- **Equivariance:** each atom carries scalar features (element, ligand-group membership,
  coordination-site index, timestep) and 3D vector features. Scalars and vectors are
  processed by separate channels that exchange information through the vector norm,
  giving exact SE(3) equivariance.
- **Diffusion:** variance-preserving Gaussian process, cosine schedule, T = 500
  timesteps. Diffuses atom positions (continuous) and atom types (one-hot, via argmax
  dequantization) jointly.
- **Conditioning:** procedural (no classifier-free guidance). Denticity is enforced via
  a partition table of allowed ligand-denticity combinations per coordination number.

### Original scope

Trained on **30,118 mononuclear octahedral (CN = 6) transition-metal complexes** from
the CSD, with combinatorial ligand-masking augmentation (~404,000 samples). Element set
for ligand atoms: {C, N, O, F, P, S, Cl, Br}. Reported metrics on transition metals:
valid_ligand ≈ 0.95, connected_ligand ≈ 0.93, valid_complex ≈ 0.89–0.91. **Never tested
above CN = 6, and never on f-block (lanthanide) elements.** This project is the first
attempt to extend it to lanthanides and to CN 7–10.

---

## 4. Phase 1 — CSD data pipeline

**Input:** 53,333 CIF files of lanthanide complexes (provided by Shicheng Li from the
Jiang group; CSD v5.46). Because Berea College has no CSD Python API license, a
custom pipeline was built using pymatgen and ASE instead of the CSD API.

**Five-stage pipeline:**

1. **Parse** all 53,333 CIFs (pymatgen). Filter out disorder and polymeric structures.
   → 31,979 mononuclear molecular complexes.
2. **Donor identification:** atoms within 2.8 Å of the Ln center classified as
   first-shell donors.
3. **Ligand decomposition:** build covalent bond graph (1.3x sum of covalent radii),
   remove the Ln node, take connected components; components with at least one donor are
   coordinating ligands.
4. **Filter** to training candidates: mononuclear, molecular, CN ∈ {7,8,9,10},
   all non-Ln elements in {C,N,O,F,P,S,Cl,Br}. → **9,306 training complexes**
   (of which 6,563 are O/N-donor only).
5. **Tensorize** each complex (positions, one-hot types, nuclear charges, ligand-group,
   coordination-site).

**Validation against the Jiang group's published CSD analyses** (consistency check):

| Quantity | This pipeline | Jiang group papers |
|---|---|---|
| Total Ln complexes parsed | 53,333 / 53,360 | 53,370 (ICC 2025) |
| Mononuclear complexes | 31,979 | 29,891 (ICC 2025) |
| Donor distribution | 65% O, 18% N, 14% C | O-dominated (Sci. Rep. 2024) |
| Ln–donor distance trend | 2.61 Å (La) → 2.43 Å (Lu) | 2.62 → 2.41 Å (lanthanide contraction) |
| CN distribution peak | CN = 8 (9,658), then CN = 9 (6,529) | CN = 8 dominant from Sm onward |

The small differences (e.g. 31,979 vs 29,891 mononuclear) are attributed to
distance-based bond detection versus CSD-API coordinate-bond annotations. Trends match,
which validated the home-built pipeline.

**Ligand inventory:** 216,509 coordinating ligand instances, 54,946 unique SMILES. The
extractant-relevant chemistries (amides, beta-diketones, phosphine oxides,
phenanthroline derivatives) are all present.

**Training-sample budget.** The 9,306 candidates (avg 4.6 ligands each, ~23 masking
combinations per complex) form a pool of **~212,000** maskable training samples; the
fine-tune in §6 drew **~85,760 per epoch** (335 steps × batch 256). A per-element
breakdown — parse rates, CN distribution, average Ln–donor distance, training candidates,
and ligand counts for all 14 lanthanides — is tabulated in `summary_by_element.csv`
(published under the site's `assets/data/`).

---

## 5. Phase 2 — Adapting the model to lanthanides

The key engineering finding: **the adaptation is minimal because only one layer changes
shape.** The five GVP message-passing layers (the representational engine) transfer
directly from the pretrained transition-metal checkpoint.

Code-level changes (branch `ln-adaptation` of `github.com/mironovb/multi_LigandDiff`):

| File | Change | Reason |
|---|---|---|
| `src/const.py` | Added La–Lu (Z = 57–71, except Pm) to metal registries | Recognize Ln as legal metal centers |
| `src/const.py` | `MAX_LIGANDS = 10`; replaced hard-coded CN-6 partition tables with a dynamic `denticity_partitions()` generator | CN 7–10 has far more denticity partitions than CN 6 |
| `src/molecule_builder.py` | Extended donor detection; `BondedOct=False`; added F/Cl/Br donors | molSimplify decomposition silently failed on Ln complexes; halide donors occur |
| `generate.py` | Widened ligand-group tensors 7 → 11 columns; removed `assert sum(coord_site)==6`; dynamic partitions | Removed fixed-octahedral assumptions |
| `generate_mask1.py` | Single-ligand masking variant of `generate.py` | Completion (mask1) experiments |
| `src/edm.py` | Added RePaint inner loop + `--resample_r` flag | Boundary-resampling for yield (see §7) |
| `train.py`, `src/lightning.py` | Discriminative LR optimizer groups; checkpoint-resume routing | Preemption-safe fine-tuning |

**The one shape change:** the input projection layer goes from in-dim 7 to in-dim 11
(output stays 192), adding ~25k parameters. The new columns were **zero-padded** (rather
than randomly re-initialized) so the loaded TM weights stay aligned with the original 7
ligand-group slots.

---

## 6. Phase 3 — Training

- **Hardware:** single NVIDIA H200 (143 GB) on a university HPC cluster, on a
  preemptible partition (4 h job limit).
- **Fine-tuning from** the pretrained transition-metal checkpoint.
- **Optimizer:** AdamW + cosine annealing. **Discriminative learning rates:** 1e-4 for
  the new input projection, 1e-5 for the pretrained GVP backbone (10x lower so the
  transferred features are not overwritten).
- **Batch size:** 256. **Loss:** MSE on noise prediction, masked atoms only. **EMA:**
  0.999 at validation. **Early stopping:** patience 15 on validation loss.
- **Data:** 9,306 complexes, augmented by ligand masking (up to 20 mask configs each) to
  ~85,000 training samples; validation split *by complex* (no leakage between mask
  configs of the same molecule).

**Result:** validation loss dropped **95%, from 977.8 (epoch 0) to 49.9 (epoch 48)**.
Early stopping fired at epoch 63. Total ~10 GPU-hours across three preemption-interrupted
sessions (jobs 12124078, 12138834, 12151181), resumed cleanly via PyTorch Lightning
checkpoints.

**Best checkpoint:** `models/ln_finetuned/ln_finetuned_epoch=48.ckpt`.

**Convergence sampling metrics** (on ~1,000 generated complexes per validation step):
`valid_ligand 0.97`, `connected_ligand 0.94`, `valid_complex 0.005`. The first two
(per-fragment chemical validity) are strong; the third (whole-complex validity) is low,
which set up the generation analysis below.

---

## 7. Phase 4 — Generation and the RePaint sweep

All generation uses **mask1 mode** on the Eu(TMMA)₂(NO₃)₃ reference: fix the full
complex as context, hide one ligand, ask the model to regenerate it.

**RePaint** (Lugmayr 2022) is an inference-time modification: at each of the 500
denoising steps, oscillate `r` times between adding noise back and denoising forward, so
the generated region re-aligns with the fixed context. It addresses "boundary
disharmony" (generated atoms drifting away from context). No retraining needed; ported
via the `--resample_r` flag.

**The r-sweep** (yield = valid complexes / attempts):

| Sampler | Attempts | Valid | Yield | Denticity match |
|---|---|---|---|---|
| Baseline (r = 1) | 2,500 | 29 | 1.16% | 13.8% |
| RePaint r = 5 | 2,500 | 85 | 3.40% (2.9x) | **15.3% (best)** |
| RePaint r = 10 | 1,500 | 57 | 3.80% | 10.5%† |
| RePaint r = 20 | 750 | 39 | 5.20% | — |
| **Total** | | **171** (r1+r5+r10); **210** incl. r = 20 | | |

† The r = 10 denticity-match (10.5%) was computed on a partial 19-structure aggregate (the
only one saved), not the full 57; the completed-run yield (**57 / 1,500 = 3.80%**) is exact.
The earlier "19 valid / 300 attempts / 6.33% (5.5×)" figure came from that interrupted
partial run and is superseded by the completed `finish_sweep` job (12340606).

**Reading:** yield rises monotonically with r (1.16 → 3.40 → 3.80 → 5.20%), but
donor-placement quality
(denticity-match rate) peaks at r = 5 and *drops* at r = 10. So **r = 5 is the working
point** — past it you get more structures that clear the coarse validity filter but are
not better at the fine-grained placement metric.

---

## 8. Phase 5 — Validity analysis and the metric caveat

**Important methodological correction made during the project.** An early framing
claimed the model was "doing side-chain elaboration, not novel ligand design," based on
a connected-component fragment count: only 9 of 38 xTB-converged structures (24%)
returned the expected 5 distinct ligand fragments; 76% returned 3 or 4.

**Visual inspection in Avogadro overturned that framing.** Opening representative
structures showed that **most files do contain a clean separate fifth fragment** in the
masked position — TMMA-shaped, diamide backbone present, carbonyl oxygens pointed at Eu,
Eu–O distances in the expected 2.3–2.6 Å range. The fragment-count metric was an
**artifact of the bond-detection cutoff**: the 1.3x covalent-radii rule merges atoms
placed close to a context ligand at threshold-ambiguous distances, even when no real
bond exists.

The same artifact appears under GFN2-xTB post-processing (the Jin/Merz validity
protocol): 60.5% of converged structures showed "new" cross-ligand bonds after
optimization, versus 0% for the pristine Kravchuk reference under the same protocol. xTB
simply locks in whatever the bond detector was already flagging at borderline distances.

**Corrected conclusion of Phase 5:** mask1 works. The model regenerates a sensible TMMA
in the right place in most cases. The graph-level "fusion" numbers are a sensitivity
check on geometry (some generated atoms do sit slightly close to context), not evidence
of chemical fusion. This correction matters because it changed the entire story from
"the model fails" to "the model completes well — but does it design?"

**xTB convergence:** 38/41 baseline structures converged under GFN2-xTB
(`--opt normal --uhf 6 --cycles 500`), 92.7%, consistent with the literature.

---

## 9. Phase 6 — The design test (completion vs de-novo)

The crucial realization: **mask1 only tests *completion*, not *design*.** Giving the
model 4 of 5 ligands and asking it to fill in the fifth is an easy task — the training
set has many homoleptic complexes, so reproducing a TMMA-shaped ligand is the *correct*
response to that prompt, not evidence of creative design.

To test design ability, the experiment **sweeps how many ligands are masked at once**,
shrinking the scaffold the model can lean on. This is reachable through the existing
`generate.py` code path (which already enumerates ligand subsets); a wrapper
(`generate_design_test.py`) was written to control the mask size exactly and tag outputs
by it. Masking *all* ligands leaves only the Eu center as context — true de-novo
generation of a whole coordination sphere.

| Mask level | Context given | Meaning |
|---|---|---|
| mask 1 | 4 of 5 ligands | Completion control (known to work) |
| mask 2 | 3 of 5 ligands | Partial design |
| mask 3 | 2 of 5 ligands | Partial design |
| mask all | 0 ligands (just Eu) | **Full de-novo design** |

**Results:**

| Mask level | Attempts | Valid | Yield |
|---|---|---|---|
| mask 1 | 2,500 | ~85 (130 incl. all CN partitions) | ~3.4% |
| mask 2 | (cut off by time limit) | ≥4 | low, nonzero |
| mask 3 | ~1,500+ (cut off) | **0** | **0%** |
| mask all | **6,300** | **0** | **0.00%** |

**The model's validity collapses to zero as context shrinks.** With 2 ligands hidden
(mask 3) it produces nothing valid; with all ligands hidden it produces **0 valid out of
6,300 attempts.**

**Mechanism (from the error logs):** the rejections are overwhelmingly *"Explicit
valence for atom # N (nitrogen) is greater than permitted"* — the model places nitrogen
in chemically impossible 4-bond environments. These are not geometric near-misses; they
are valence-broken molecules. The model learned local "fill the gap consistent with
neighbors" but has no notion of composing a valence-correct fragment from scratch.

**Note on mask2:** the only mask2 structures that exist are the handful (≥4) from the
first full run (job 14292188) before its time limit; the focused design run never
reached mask2. A complete degradation curve would benefit from a dedicated mask2 run,
but the headline (maskall = 0/6300) is already conclusive.

---

## 10. Consolidated results

**What works:**

- First 3D diffusion model trained on f-block (lanthanide) coordination chemistry.
- Clean transfer from the transition-metal checkpoint: only one layer reshaped,
  ~10 GPU-hours of fine-tuning, 95% validation-loss reduction.
- RePaint successfully ported; 2.9x yield lift at r = 5, which is the working point.
- mask1 completion works: 171 valid Eu(TMMA)₂(NO₃)₃ structures across the sweep (210
  including r = 20), visually confirmed to contain correctly-placed TMMA-shaped ligands.

**What does not work (yet):**

- De-novo design. Generating a coordination sphere from just the metal yields 0 valid
  structures out of 6,300 attempts. Validity collapses once more than one ligand is
  hidden (0 valid at mask 3 already).

**A methodological lesson:**

- Graph-level fragment-count and xTB cross-bond metrics over-flagged "failures" due to a
  bond-detection cutoff artifact. Visual inspection was necessary to get the story right.
  Always corroborate automated metrics with direct inspection.

---

## 11. Current conclusion

**In its current form the model is a completion tool, not a designer.** It reliably
regenerates a single missing ligand when the rest of the complex is present, but it
cannot compose a valence-correct coordination sphere from the metal alone. The failure
is chemical (impossible valences), not merely geometric, and it sets in as soon as the
scaffold is reduced to two context ligands.

This is a clean, defensible negative result with a mechanistic explanation. It directly
motivates the architectural question: the inpainting objective, as trained, teaches
local consistency but not global composition. Whether multi-LigandDiff can be pushed to
true design — or whether a different architecture is needed — is the central open
question.

---

## 12. Open questions and next steps

In rough priority order:

- **(a) Complete the degradation curve.** Run a dedicated mask 2 experiment (3 of 5
  hidden) to locate exactly where between mask 1 (works) and mask 3 (0%) the cliff
  falls. Cheap; sharpens the result for a paper.
- **(b) Training-data augmentation toward harder masks.** The model was trained with up
  to 20 mask configs per complex; few of those hide most ligands. Increasing the
  fraction of high-mask-count training examples directly targets the deficiency.
- **(c) Cross-class conditioning.** Test whether the model follows context toward a
  different donor class (phosphine oxide, Schiff base) or reverts to the dominant
  amide/nitrate training prior.
- **(d) Hard geometric projection during sampling** (Christopher 2024, already
  implemented). Projects generated atoms out of an exclusion shell around context atoms;
  addresses the "placed slightly too close" tendency and may improve placement quality.
- **(e) Architecture decision.** If (b)–(d) do not enable de-novo generation, consider
  alternatives (e.g. flow-matching or autoregressive composition) better suited to
  building structure without a scaffold.
- **(f) Validation pipeline upgrade.** Once a candidate set is trusted, tighten the xTB
  protocol (frozen context, `--alpb dodecane`, `--opt tight`) and run DFT validation
  (PBE0-D3/def2-TZVP, Stuttgart ECP28MWB on Eu, SMD dodecane; ORCA templates prepared)
  on the top candidates.

---

## 13. Infrastructure and reproducibility

- **Code:** `github.com/mironovb/multi_LigandDiff`, branch `ln-adaptation`.
- **Checkpoint:** `models/ln_finetuned/ln_finetuned_epoch=48.ckpt`.
- **Cluster:** a university HPC cluster, preemptible partition, NVIDIA H200 GPUs.
- **Environment:** `module load miniforge/25.11.0-0` then `conda activate ligdiff`.
- **Key scripts:** `generate.py` (full / multi-mask generation), `generate_mask1.py`
  (single-ligand completion), `generate_design_test.py` (mask-size sweep for the design
  test), `analyze_gen.py` (per-structure coordination-sphere inspector), `xtb_opt.py`
  (xTB post-processing).
- **Reference complex:** `eu_tmma_cis.xyz` (Eu(TMMA)₂(NO₃)₃, CCDC VEDTAA01).
- **Structure bundle:** `report_2_ln_diffusion_2026-04-23.tgz` — 171 valid structures
  (29 baseline + 85 r=5 + 57 r=10; 210 including 39 from r=20), pristine reference,
  figures, metrics files.
- **Cluster caveats learned:** the preemptible partition has a 4 h wall limit; long sweeps must
  put the most important experiment first. Avoid `set -euo pipefail` with `source
  ~/.bashrc` (the `nounset` flag trips on an unset variable in `/etc/bashrc`). Use
  `python -u` for unbuffered live logging.

---

## 14. Reference list

1. Jin, H.; Merz, K. M. *multi-LigandDiff.* JCTC 2024. DOI 10.1021/acs.jctc.4c00775.
2. Hoogeboom, E. et al. *Equivariant Diffusion for Molecule Generation in 3D.* ICML 2022.
3. Jing, B. et al. *Learning from Protein Structure with Geometric Vector Perceptrons.*
   ICLR 2021.
4. Lugmayr, A. et al. *RePaint: Inpainting using DDPMs.* CVPR 2022. arXiv:2201.09865.
5. Schneuing, A. et al. *Structure-based drug design with equivariant diffusion models
   (DiffSBDD).* Nat. Comput. Sci. 2024. DOI 10.1038/s43588-024-00737-x.
6. Christopher, J. et al. *Projected (constrained) Diffusion.* NeurIPS 2024.
   arXiv:2402.03559.
7. Li, S.; Jansone-Popova, S.; Jiang, D.-e. *Advancing Rare-Earth Separation by Machine
   Learning.* JACS Au 2022.
8. Li, S.; Jansone-Popova, S.; Jiang, D.-e. *(CSD coordination-trend analysis.)*
   Sci. Rep. 2024. DOI 10.1038/s41598-024-62074-3.
9. Li, S.; Jansone-Popova, S.; Jiang, D.-e. *Nitrate and water in the first coordination
   shells of lanthanide complexes.* Inorg. Chem. Commun. 2025, 179, 114844.
10. Kravchuk, D. et al. *Eu(TMMA)₂(NO₃)₃.* EurJIC 2024. DOI 10.1002/ejic.202300632.
    CCDC VEDTAA01 / deposit 2296300.

---

*Document compiled 23 May 2026. All quantitative results traceable to on-cluster runs
and the uploaded metrics files (aggregate taxonomies, bond_classification.csv,
pristine_reference.json, xtb_summary.csv) plus the design-test job logs
(14292188, 14344725).*
