---
layout: default
title: Methods
nav_order: 3
---

# Methods
{: .no_toc }

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

{: .note }
> **Provenance convention.** Quantities confirmed from on-cluster logs or repo files
> (e.g. batch size, discriminative LRs, sample count) are cited to their source. Figures
> that describe the *base model's* design or the *upstream* CSD pipeline — and that could
> **not** be re-checked from the downloaded working directory — are flagged
> **(unverified)** and should not be read as independently confirmed here.

## The base model: multi-LigandDiff

multi-LigandDiff (Jin & Merz, JCTC 2024) is a **3D denoising diffusion model** for metal
coordination complexes. Given a metal center and, optionally, some fixed context ligands,
it generates the 3D coordinates and element identities of new ligand atoms.

- **Type.** An Equivariant Diffusion Model (EDM; Hoogeboom 2022) with a Geometric Vector
  Perceptron graph neural network (GVP-GNN; Jing 2021) as the score function.
- **Equivariance.** Each atom carries scalar features (element, ligand-group membership,
  coordination-site index, timestep) and 3D vector features, processed by separate
  channels that exchange information through the vector norm — giving exact **SE(3)
  equivariance**.
- **Diffusion process.** Variance-preserving Gaussian diffusion on a **cosine schedule,
  T = 500 timesteps**, diffusing atom positions (continuous) and atom types (one-hot, via
  argmax dequantization) jointly.
- **Graph.** Fully connected — every atom attends to every atom, with no distance cutoff.
  This tight coupling between context and generated atoms becomes important in the
  [Results](results.html).
- **Conditioning.** Procedural (no classifier-free guidance); denticity is enforced
  through a partition table of allowed ligand-denticity combinations per coordination
  number.

{: .unverified }
> **Architecture internals — from `PROJECT_OVERVIEW.md`, not independently verified.**
> The depth/width and parameter count (**5 message-passing layers, 192 scalar + 32 vector
> features per layer, ~3.8M parameters**) and the **T = 500 cosine schedule** are as
> described in the project overview. Verifying exact parameter counts would require
> loading a checkpoint, which was deliberately not done. The *adaptation approach* below,
> by contrast, **is** confirmed from `finetune.py`.

**Original scope (as reported for the base model).** Trained on mononuclear octahedral
(CN = 6) transition-metal complexes from the CSD, with combinatorial ligand-masking
augmentation; ligand-atom element set {C, N, O, F, P, S, Cl, Br}; reported metrics around
valid_ligand ≈ 0.95, connected_ligand ≈ 0.93. The base model was **never tested above
CN = 6 and never on f-block elements** — which is the gap this project addresses.

## Adapting the model to lanthanides

The key engineering finding: **the adaptation is minimal because only one layer changes
shape.** The five GVP message-passing layers — the representational engine — transfer
directly from the pretrained transition-metal checkpoint.

{: .works }
> **Confirmed from `finetune.py`.** The script's docstring and flags confirm the core
> approach: it loads the TM weights with `ligand_node_nf` widened **7 → 11 by
> zero-padding**, and trains with **discriminative learning rates** (`--lr_head`,
> `--lr_backbone`) so the transferred backbone is not overwritten.

**The one shape change.** The input projection layer goes from in-dim 7 to in-dim 11
(output stays 192). The four new ligand-group columns are **zero-padded** rather than
randomly re-initialized, so the loaded TM weights stay aligned with the original 7
ligand-group slots. Everything downstream of that projection is reused.

**Code-level changes** (branch `ln-adaptation`; from `PROJECT_OVERVIEW.md` §5 — the
*approach* is confirmed by `finetune.py`, the per-file diff is as described there):

| File | Change | Reason |
|---|---|---|
| `src/const.py` | Added La–Lu (Z = 57–71, except Pm) to the metal registries | Recognize Ln as legal metal centers |
| `src/const.py` | `MAX_LIGANDS = 10`; dynamic `denticity_partitions()` generator replacing hard-coded CN-6 tables | CN 7–10 has far more denticity partitions than CN 6 |
| `src/molecule_builder.py` | Extended donor detection; `BondedOct = False`; added F/Cl/Br donors | molSimplify decomposition silently failed on Ln complexes |
| `generate.py` | Widened ligand-group tensors 7 → 11; removed `assert sum(coord_site)==6`; dynamic partitions | Removed fixed-octahedral assumptions |
| `generate_mask1.py` | Single-ligand masking variant of `generate.py` | The completion (mask 1) experiments |
| `src/edm.py` | Added a RePaint inner loop + `--resample_r` flag | Boundary-resampling for yield (see [Results](results.html)) |
| `train.py`, `src/lightning.py` | Discriminative-LR optimizer groups; checkpoint-resume routing | Preemption-safe fine-tuning |

## The CSD data pipeline

Because Berea College has no CSD Python API license, a custom pipeline was built using
**pymatgen and ASE** instead of the CSD API. Starting from CIF files of lanthanide
complexes (provided by the Jiang group, CSD v5.46), it runs five stages: parse and filter
to mononuclear molecular complexes → identify first-shell donors (within 2.8 Å) →
decompose into ligands via a covalent bond graph → filter to training candidates (CN ∈
{7,8,9,10}, non-Ln elements in {C,N,O,F,P,S,Cl,Br}) → tensorize.

{: .unverified }
> **The pipeline counts could not be checked from this download.** The source CIFs,
> `prepare_training_data.py` output, and candidates CSV are **not present** — only the
> (unreadable) `train_ln.pt` / `val_ln.pt` tensors. The figures below are reproduced from
> `PROJECT_OVERVIEW.md` and are **not independently verified**. (The derived training
> *sample* count, by contrast, **is** corroborated — see Training setup.)

**Headline counts (unverified):** 53,333 CIFs → 31,979 mononuclear complexes →
**9,306 training complexes** (of which 6,563 are O/N-donor only). Ligand inventory:
216,509 coordinating ligand instances, 54,946 unique SMILES.

**Validation against the Jiang group's published CSD analyses (unverified consistency
check).** Reproduced from `PROJECT_OVERVIEW.md` §4:

| Quantity | This pipeline | Jiang group papers |
|---|---|---|
| Total Ln complexes parsed | 53,333 | 53,370 (ICC 2025) |
| Mononuclear complexes | 31,979 | 29,891 (ICC 2025) |
| Donor distribution | 65% O, 18% N, 14% C | O-dominated (Sci. Rep. 2024) |
| Ln–donor distance trend | 2.61 Å (La) → 2.43 Å (Lu) | 2.62 → 2.41 Å (lanthanide contraction) |
| CN distribution peak | CN = 8 (9,658), then CN = 9 | CN = 8 dominant from Sm onward |

The small differences (e.g. 31,979 vs 29,891 mononuclear) are attributed to distance-based
bond detection versus CSD-API coordinate-bond annotations; the *trends* match, which is
what validated the home-built pipeline.

## Training setup

- **Hardware.** Single NVIDIA **H200** GPU on the MIT Engaging cluster, account
  `mit_general`, partition `mit_preemptable` (4 h job limit, preemptible).[^cluster]
- **Initialization.** Fine-tuned **from the pretrained transition-metal checkpoint** (not
  from scratch).
- **Optimizer.** AdamW + cosine annealing, with **discriminative learning rates** — a
  higher rate for the new input projection, ~10× lower for the transferred GVP
  backbone.[^lr]
- **Batch size 256**[^batch]; loss is MSE on noise prediction over masked atoms only;
  EMA 0.999 at validation; **early stopping with patience 15** on validation loss.[^early]
- **Data.** The 9,306 complexes, augmented by ligand masking, give logged **335 steps ×
  256 = ~85,760 training samples per epoch** — corroborating the overview's "~85,000
  samples."[^samples]

See [Results → Training](results.html#training) for the loss trajectory and the
session-by-session run history.

---

[^cluster]: Account/partition confirmed across the sbatch scripts; the 4 h wall on
    `mit_preemptable` shapes several "timed-out" outcomes in the [Experiment
    Log](experiment-log.html). GPU model (H200) is corroborated by the `ln_train_h200`
    job name.

[^lr]: `finetune.py` exposes `--lr_head` and `--lr_backbone`; the discriminative-LR
    optimizer groups are also why four early resume attempts failed with "loaded state
    dict has a different number of parameter groups" (VERIFICATION_REPORT.md §2).

[^batch]: All `finetune_*.sbatch` pass `--batch_size 256` (VERIFICATION_REPORT.md §2).

[^early]: Early stop fired at epoch 63: *"Monitored metric loss/val did not improve in the
    last 15 records. Best score: 49.913"* (`ln_train_h200_12151181.err`).

[^samples]: Logs show `335/335` steps/epoch; 335 × 256 = 85,760 (VERIFICATION_REPORT.md §2).
