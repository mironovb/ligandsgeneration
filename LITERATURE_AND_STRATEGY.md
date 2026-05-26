# LITERATURE & STRATEGY — Kulik coordination papers vs. our finding

**Scope.** Reads the three Kulik-group papers Prof. Jiang sent, positions them against the
verified finding in `VERIFICATION_REPORT.md` (completion works; de-novo design fails on
nitrogen-valence violations), and restates Jiang's two-part strategy as an explicit
roadmap. This is a strategy memo, not a website (Prompt 3+). Where I read intent into
Jiang's choices, it is **labeled interpretation**.

**Source note.** All three PDFs were text-extracted (`pypdf`) and read in chunks — no
binaries dumped into context. Papers 2 and 3 are the published ACS versions. **Paper 1's
file in `papers/` is the ChemRxiv preprint (posted 3 Oct 2024)**, not the final PNAS
typeset PDF; I read the full preprint text and cite the published PNAS DOI from Jiang's
metadata. Author names were font-garbled in extraction but body text was clean; numbers
below are from the main text (SI-only values are marked).

---

## 1. Paper summaries

### Paper 1 — GNNs for predicting metal–ligand coordination (the `pydentate` paper)

> Toney, J. W.; St. Michel, R. G.; Garrison, A. G.; Kevlishvili, I.; Kulik, H. J.
> *Graph neural networks for predicting metal–ligand coordination of transition metal
> complexes.* **PNAS 2025, 122, e2415658122.** DOI
> [10.1073/pnas.2415658122](https://doi.org/10.1073/pnas.2415658122).
> Preprint read here: ChemRxiv, DOI
> [10.26434/chemrxiv-2024-nzk5q](https://doi.org/10.26434/chemrxiv-2024-nzk5q).
> Software: `pydentate` — <https://github.com/hjkgrp/pydentate>.

- **Core method.** Curate 70,069 unique, non-hemilabile ligands of *known* coordination
  from CSD mononuclear transition-metal complexes (299,035 unique-connectivity complexes
  → ligands extracted with molSimplify → element/SMILES/denticity filters). Train **two
  directed message-passing neural networks (D-MPNN + feed-forward head)** directly on
  SMILES: (a) a **graph-level model for coordination number** (how many coordinating
  atoms, 1–6 classes) and (b) a **node-level model for coordinating-atom identity** (per
  atom: donor / not-donor).
- **What it predicts / represents.** *A priori* metal–ligand connectivity from a 2-D
  ligand string. CN model: 88.5% accuracy, ROC-AUC 0.98. Donor-identity model: 98.8%
  overall / 96.9% balanced accuracy, and **84.8% "molecular accuracy"** (every atom in
  the ligand correct — the metric that matters for building a structure). Adding explicit
  H or QM descriptors did *not* help — the learned representation already captures it.
  Nitrogen is the dominant donor (52% of all coordinating atoms), then C (19%), O (15%),
  P (7%), S (6%), Si (0.4%).
- **Most relevant idea for us.** The **predict-then-build** workflow. `pydentate` predicts
  the donor set, hands it to molSimplify, which *adds bonds to a user-specified metal and
  builds the 3-D complex* (UFF-optimized, DFT-ready). In a Ti(IV) case study over
  under-sampled symmetries it generated **1,175 de-novo TMCs**, of which **75% optimized
  cleanly in DFT** — and critically, **88% optimized cleanly when the coordination was
  predicted correctly vs. only 25% when it was wrong.** Recreating known CSD structures
  gave 1.50 Å average RMSD. The lesson: *get the coordination right first and physical
  realism follows; get it wrong and the structure falls apart.* This is the exact axis on
  which our diffusion model fails. **Note: entirely d-block; CN capped at 6 — never touches
  the lanthanide / CN 7–10 regime our project lives in.**

### Paper 2 — Classification of hemilabile ligands with ML

> Kevlishvili, I.; Duan, C.; Kulik, H. J. *Classification of Hemilabile Ligands Using
> Machine Learning.* **J. Phys. Chem. Lett. 2023, 14, 11100–11109.** DOI
> [10.1021/acs.jpclett.3c02828](https://doi.org/10.1021/acs.jpclett.3c02828).

- **Core method.** Identify ligands in the CSD crystallized at *more than one denticity*
  (the uncoordinated molecular-graph hash maps to several coordinated graph hashes) →
  4,144 hemilabile ligands; after filtering to C/N/O/P/S donors and |q| ≤ 4, **1,531
  bidentate, 1,069 tridentate, 492 tetradentate**. Build a confident *non*-hemilabile
  negative set with **semi-supervised label-spreading** plus co-occurrence heuristics.
  Train XGBoost classifiers (per denticity class) to predict hemilability (up to ~93%
  accuracy, per the Paper-3 recap).
- **What it predicts / represents.** Whether a given bi/tri/tetradentate ligand *can*
  change its denticity — i.e., dynamic rather than fixed coordination.
- **Most relevant idea for us.** Two things. (1) **Donor-atom identity alone is *not*
  sufficient** to decide coordination behavior — you need a learned model; coordination
  validity is not a lookup table. (2) **Feature-importance analysis shows the 2nd, 3rd,
  and 4th coordination spheres all matter** — coordination behavior is a property of the
  whole ligand environment, not just the first-shell donors. Both points indict any
  generator that reasons only locally. (Caveat for Track B: this model still *requires the
  user to know the denticity class up front* — the limitation Paper 3 removes.)

### Paper 3 — Dynamic coordination modes with ensemble learning

> Toney, J. W.; St. Michel, R. G.; Garrison, A. G.; Kevlishvili, I.; Kulik, H. J.
> *Identifying Dynamic Metal–Ligand Coordination Modes with Ensemble Learning.*
> **JACS 2025, 147, 48218–48234.** DOI
> [10.1021/jacs.5c17169](https://doi.org/10.1021/jacs.5c17169).
> Software: `pydentate` (GitHub above) + no-code web interface "pydentate Lite",
> <https://molsimplify.mit.edu/pydentate.html>.

- **Core method.** The synthesis of Papers 1 + 2. Curate 4,075 hemilabile + 3,212
  non-hemilabile ligands; define **four exhaustive, mutually exclusive types of
  hemilability**: Type 1 (CN changes, low-CN donors ⊂ high-CN donors; e.g. terpyridine
  tri↔bi; **79.1%**), Type 2 (CN changes, distinct donors each mode; **6.9%**), Type 3
  (CN constant, partially overlapping donors; **7.5%**), Type 4 (CN constant, disjoint
  donors; e.g. thiocyanate N- vs S-binding; **6.5%**). **Fine-tune GNNs pretrained on
  Paper 1's 70k-ligand coordination dataset** to classify hemilability, then build an
  **ensemble algorithm that predicts the primary *and* alternative chemically plausible
  coordination modes end-to-end from a single SMILES string.**
- **What it predicts / represents.** The *full set* of realistic coordination modes a
  ligand can adopt — not one assumed mode. Plausibility is checked with DFT via an energy
  difference **ΔE_c** between modes, benchmarked against CSD-observed pairs.
- **Most relevant idea for us.** Paper 3 *names our problem in its introduction*: it cites
  generative TMC models (the DiffSBDD / LigandDiff family, which is exactly
  multi-LigandDiff's lineage) as **"requiring user-specified metal–ligand coordination and
  assuming a constant coordination mode."** That is a one-sentence diagnosis of
  multi-LigandDiff. The constructive answer it offers: an end-to-end model that *outputs*
  valid coordination from structure alone — i.e., the missing oracle a generator could be
  conditioned on or validated against. **Again entirely d-block.**

**The arc across the three.** 2023 → classify *whether* a ligand is hemilabile (needs
denticity given). 2024/25 PNAS → predict CN *and* donor atoms from SMILES, then build
DFT-realistic 3-D complexes (predict-then-build). 2025 JACS → predict *all* plausible
modes end-to-end. Every step is about **encoding coordination-chemistry validity into a
learned representation.** None of the three is a generator.

---

## 2. What Jiang is signaling (interpretation)

The single most telling fact: **all three papers characterize, predict, or classify
metal–ligand coordination — none generate.** Our project is a *generation* project, and
`VERIFICATION_REPORT.md` shows it fails precisely where coordination validity is required
(de-novo design = 0/6,300; ~100% nitrogen-valence violations). Reading these three
together, my interpretation of why Jiang sent *these*:

1. **They are a diagnosis-and-prescription, not background reading.** They locate the exact
   capability our generic diffusion model lacks — a learned model of *what a valid
   coordination environment is* — and show it can be learned from CSD data at high accuracy.
   Paper 3 even spells out the limitation of our model's lineage by name.

2. **They point to the methodological exemplar for the new platform.** Kulik's group sits in
   MIT **Chemical Engineering** — directly aligned with Jiang's stated intent to ground the
   next platform in "chemical-engineering principles." `pydentate`'s predict-then-build
   pipeline is a concrete, open-source architecture (code + web interface) that *structurally
   cannot* emit the valence-impossible structures we observed, because it only ever places
   real, valence-valid ligands. (Interpretation: this is the template he wants Track B to
   start from, extended to rare earths.)

3. **They define the representation philosophy.** Denticity, donor-atom identity,
   hemilability type, dynamic modes, multi-shell features — this is the vocabulary of
   coordination validity our model never learned. (Interpretation.)

Mapping each paper to Jiang's two-part strategy:

| Paper | (a) Salvage a multi-LigandDiff paper (Track A) | (b) Seed the from-scratch platform (Track B) |
|---|---|---|
| **1 — pydentate GNN** | Gives the framing + a literature precedent that *predicting coordination a priori is the bottleneck*; the 88%-vs-25% DFT result lets us explain our 0% de-novo rigorously, and pydentate's 75% de-novo DFT success is the baseline our maskall=0 is measured against. | **Primary.** The blueprint: coordination-aware representation + predict-then-build, to be extended to CN 7–10 and hard-donor lanthanide sets. |
| **2 — hemilabile XGBoost** | Minor — supports "coordination validity is non-trivial / not a lookup." | **Primary.** Denticity is *dynamic*; 2nd–4th coordination spheres matter — both directly relevant to designing labile rare-earth extractants. |
| **3 — dynamic ensemble** | Provides the state-of-the-art benchmark and the explicit, citable statement of the generative-model limitation we hit. | **Primary.** The closest thing to a "coordination-mode oracle" a generator could be conditioned on / validated by; the ΔE_c criterion is a ready-made plausibility filter. |

(Interpretation, stated plainly: Jiang is saying *get the honest multi-LigandDiff paper
out using completion + the de-novo failure as a finding, then build a coordination-aware,
rare-earth-native platform whose core idea is borrowed from Kulik's predict-then-build line
of work.*)

---

## 3. Bridge to our finding

**What the model actually does (from `VERIFICATION_REPORT.md`).** multi-LigandDiff is a
generic 3-D equivariant diffusion model: it diffuses atom *positions* and *types* jointly,
then bond perception (molSimplify/OpenBabel) assigns bonds and RDKit sanitizes. Its only
coordination "knowledge" is implicit (the geometric distribution of training complexes) plus
a procedural denticity partition table. It has **no explicit notion of atomic valence**.

- **With scaffolding (mask1 completion): works.** The fixed Eu + context ligands pin the
  geometry; the model fills one ligand into a well-constrained pocket. Local valence comes
  out right → **126 valid**, xTB-stable (38/41 = 92.7%), Eu–O ≈ 2.3–2.6 Å.
- **Without scaffolding (maskall = 0): fails.** Forced to invent an entire CN≈10 sphere
  (~35 heavy atoms) around a bare Eu in a fully connected graph, atoms crowd; bond perception
  then finds nitrogens with four neighbors within bonding distance → **"explicit valence for
  N, 4, greater than permitted"**, ~100% of logged rejections, **0 valid / 6,300**. The
  scaffold-dependence is sharp: mask1 = 126, mask2 = 4, mask3 = 0, maskall = 0.

**Why coordination-aware representations fix exactly this.** The N-valence error is a
*molecular-graph* error — a property of the organic ligand framework, independent of the
metal. The Kulik models operate at precisely that level (SMILES / molecular graph / donor
identity). A coordination-validity-aware model would differ in three ways:

1. **Valence-valid by construction.** Generate (or select) the ligand as a *chemical graph*
   — where N simply cannot have four bonds — and only then place it in 3-D. This is what
   predict-then-build buys you: molSimplify never produces a 4-valent neutral N because it
   assembles real ligands. Our model produces it because it paints raw 3-D points and hopes
   the post-hoc Lewis structure is legal.
2. **Denticity / CN as an input, not an accident.** pydentate *predicts* "this ligand
   donates through these k atoms"; the builder then satisfies it. Our model has only a
   coarse partition table and no per-atom donor prior, so with no context it has nothing to
   anchor the sphere.
3. **Hard constraints during sampling, not post-hoc rejection.** The repo already contains a
   geometric-projection module (Christopher et al., Projected Diffusion); a coordination-aware
   sampler would project onto valence-/CN-/charge-feasible configurations *at each denoising
   step* instead of generating freely and discarding 99.99% of attempts.

In one line: **our model generates geometry and infers chemistry; a coordination-aware model
fixes chemistry first and then realizes geometry.** That inversion is the whole difference
between 0/6,300 and pydentate's 75% de-novo DFT success.

---

## 4. Two-track roadmap (Jiang's plan, made explicit)

### Track A (now) — get one honest multi-LigandDiff paper out

**The minimal, honest, publishable story** (every claim below is logged/verified; see
`VERIFICATION_REPORT.md`):

- **Headline novelty.** *First adaptation of a 3-D equivariant diffusion model to f-block
  (lanthanide) coordination chemistry and to high coordination numbers (CN 7–10).* The base
  model (multi-LigandDiff / LigandDiff) was d-block, CN ≤ 6 only — so this is genuinely new
  ground, and notably a regime the Kulik tools also do not cover.
- **Result 1 — completion works.** Fine-tuning drove val_loss 977.8 → **49.9 @ epoch 48
  (≈95% reduction)**, clean early-stop; convergence sampling 0.97 valid-ligand / 0.94
  connected. mask1 completion on Eu(TMMA)₂(NO₃)₃ yields **126 valid** ligand fragments in the
  fixed pocket, xTB-stable (38/41 = 92.7%). → The model learned *valid local lanthanide
  coordination geometry given context.*
- **Result 2 — de-novo design fails, with a mechanism.** maskall = 0 gives **0 valid / 6,300
  attempts**; the scaffold gradient (126 → 4 → 0 → 0 for mask1/2/3/all) and the
  **~100% nitrogen explicit-valence rejections** give a clean, citable mechanistic
  explanation: a generic 3-D diffusion model has no valence/denticity constraint, so without
  scaffolding it produces atom clouds that resolve to impossible Lewis structures. *This is
  the paper's most valuable scientific content* and it sets up Track B.
- **Result 3 — RePaint yield engineering.** Inference-time resampling raises yield
  **monotonically: r=1 → 5 → 10 → 20 = 1.16% → 3.40% → 3.80% → 5.20%**, with denticity-match
  peaking at r=5 (15.3%). An honest yield-vs-resampling trade-off (more resampling buys yield,
  not validity). **Use the corrected numbers** from the verification report:
  completed r=10 = **57/1,500 = 3.80%** (not 19/300/6.33%), and total valid ≈ **171** (r1+r5+r10)
  or **210** with r=20 — *not* the "133" or "5.5×" in `PROJECT_OVERVIEW.md`.
- **What to leave out (credibility).** The `paper/` "Prompts 1–10" artifacts
  (context-density ablation, cross-architecture table, projection-stack "6.4%", "DFT
  submitted") have **no supporting job logs and partly contradict the real xTB data** — omit
  them. Do **not** claim DFT validation as done (only ORCA templates exist). Keep the paper to
  what ran.

**Honest one-line abstract for Track A:** *A 3-D diffusion model can be fine-tuned to
complete lanthanide coordination spheres but cannot design them de novo; the failure is a
specific, diagnosable coordination-validity (valence) gap, and inference-time resampling buys
yield but not validity — motivating coordination-aware generation.* This is a legitimate
methods-adaptation + diagnostic ("informative negative") contribution.

### Track B (next) — the new, from-scratch platform

Design principles to borrow, with provenance:

**From the Kulik papers:**

1. **Coordination-aware representation (Papers 1–3).** Learn denticity (donor count) and
   donor-atom identity from molecular graphs — but **extend past pydentate's CN ≤ 6 to the
   lanthanide CN 7–10 regime**, which their models explicitly exclude.
2. **Predict-then-build instead of generate-and-hope (Paper 1).** Produce/seed a
   *valence-valid ligand graph* (SMILES-level, so the N-valence error is impossible by
   construction), predict its donor set, then place it around the Ln with a
   deterministic/constrained 3-D builder. Benchmark: pydentate hit 1.50 Å RMSD vs. CSD and
   88% DFT success when coordination was correct.
3. **Hard valence / CN / charge constraints inside the sampler (Paper 1 + repo's projection
   module).** If a 3-D generative stage is kept, enforce constraints during denoising
   (projection / type-masking), not as post-hoc rejection.
4. **Hemilability & multi-shell awareness (Papers 2–3).** For separations, denticity
   flexibility is a *feature* (extractants must bind *and* release); encode the four
   hemilability types and predict alternative modes, and model beyond the first shell (2nd–4th
   spheres carry signal). The ΔE_c criterion gives a ready-made plausibility filter.
5. **CSD-grounded, synthesizability-biased data (all three).** Train on experimentally
   observed complexes so candidates are synthesizable by construction.

**From rare-earth coordination chemistry (and Jiang group's own CSD analyses):**

6. **Hard-donor preference of trivalent lanthanides.** Ln³⁺ are hard Lewis acids → bias donor
   sets to O and N (the project already used an O/N-only subset). Encode HSAB as a prior.
7. **High coordination numbers (8–10) as a structural prior.** This is the regime pydentate
   omits; the reference Eu(TMMA)₂(NO₃)₃ is CN = 10. The platform must be CN-flexible and
   first-shell-saturating by design.
8. **Lanthanide contraction as the selectivity handle.** Ln–donor distance contracts smoothly
   across the series (project-measured **2.61 Å (La) → 2.43 Å (Lu)**). Because *selectivity*
   between adjacent lanthanides is the actual industrial goal, conditioning on target Ln and
   encoding the contraction lets the model reason about *differential* binding, not just
   single-complex stability.
9. **Predominantly ionic, non-directional Ln–L bonding.** Geometry is governed by denticity +
   sterics/packing + charge balance rather than ligand-field directionality — so the metal
   coordination can be treated more flexibly than d-block, *provided* charge neutrality (Ln³⁺)
   and first-shell saturation are respected.
10. **Counter-ions / solvent in the first shell.** Nitrate and water routinely co-coordinate
    (Jiang group, *Inorg. Chem. Commun.* 2025, ~29,891 Ln complexes; the reference has 3
    bidentate nitrates). Model the *full* first shell, not just the designed organic ligand.
11. **Spec-conditioned generation (Jiang's stated vision).** Make the conditioning target
    explicit — e.g. "2 N + 3 O donors, neutral charge, CN 8, Eu" — i.e., denticity/donor
    composition as the control knob, which is exactly what a coordination-aware representation
    makes addressable.

---

## 5. Open questions for Jiang (for the meeting)

1. **Track A scope / stopping point.** Is the diagnostic result (completion works; de-novo
   fails on valence) publishable on its own as a methods-adaptation + cautionary study, or
   does it need at least one **DFT-validated completion showcase** before we write? (We have
   *not* run DFT — only ORCA templates exist — so this decides remaining compute before
   drafting.)

2. **Track B architecture — which bet?** Should the new platform be **graph-level
   predict-then-build** (pydentate-style, valence-safe by construction) or **constrained 3-D
   generation** (keep diffusion, add hard valence/CN/charge projection)? These are different
   engineering programs and shouldn't be hedged.

3. **What is the generation *objective*?** Is the primary target **selectivity** (differential
   binding of adjacent lanthanides — e.g. Eu vs. Gd, La vs. Lu — exploiting the contraction),
   rather than single-complex stability? If so, the platform must condition on metal *pairs*
   and a selectivity loss, which reshapes the data and training design.

4. **Build vs. reuse the Kulik stack.** Do we extend the open-source `pydentate` (GitHub +
   web interface) to f-block / CN 7–10 / hard-donor sets, or build the coordination-prediction
   layer from scratch on the Jiang group's own ~29,891-complex lanthanide dataset?

5. **How central is hemilability to the separations goal?** Should Track B explicitly model
   denticity switching (bind-and-release kinetics for extractants — Papers 2–3), or is
   equilibrium first-shell selectivity sufficient for v1?

---

*Prepared from: the three PDFs in `papers/`; `VERIFICATION_REPORT.md` (verified results);
`PROJECT_OVERVIEW.md` (lanthanide framing, reference complex, base-model scope). Interpretive
claims about Jiang's intent are labeled as such; all quantitative results trace to the
verification report or the papers' main text.*
