---
layout: default
title: Code Review
nav_order: 4.5
---

# Code review — where the pipeline can be wrong, and the cheapest path to a positive result
{: .no_toc }

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

{: .note }
> This is a **static read** of the `multi_LigandDiff` repo as adapted for lanthanides — not
> a re-run. Each finding cites the file, function, or job log it comes from. The thesis is a
> direct extension of the project's own [metric caveat](results.html#the-metric-caveat):
> the same bond-detection brittleness that *over-flagged* mask-1 failures is also the
> instrument that produced the headline **de-novo 0 / 6,300**, and it has not been corrected
> there. Several of the changes below are nearly free and could move that number off zero —
> or, just as usefully, prove the limitation is real rather than instrumental.

## What is *not* the problem (verified)

{: .works }
> **The lanthanide transfer loaded cleanly.** The fine-tune log records **227 layers loaded
> exactly, 3 zero-padded** (the 8→12 `ligand_site_embedding`, the 16→20 `h_embedding_out`
> weight and bias — i.e. the documented 7→11 input-projection growth), and **1 recomputed**
> (the noise-schedule `gamma` buffer).[^load] So the de-novo failure is **not** a botched
> checkpoint load or a silently-reinitialised backbone. The architecture critique below is
> about the *sampling, conditioning, and validity* code — not the trained weights.

## Finding 1 — the de-novo "0 / 6,300" is read off the instrument the project already distrusts

The validity gate that defines a "valid complex" lives in `generate.py → generate_ligand`
and is the **same** distance-based bond perception the Results page shows over-flags
mask-1.[^gate] A generated point cloud is counted valid only if **all** of these pass:

1. `molSimplify`'s `mol3D.sanitycheck` reports **no overlapping atoms**, and
2. `ligand_breakdown` recovers **exactly** every atom (`total_atoms == natoms`), and
3. **every** generated-touching fragment passes a bare `Chem.SanitizeMol` (`compute_validity`), and
4. each such fragment is a single connected component.

Gates 1–2 are pure geometry, decided by the **same 1.3× covalent-radii cutoff** the
[metric caveat](results.html#the-metric-caveat) already identified as merging atoms "at
threshold-ambiguous distances … even when no real bond exists." For a from-scratch
~35-heavy-atom sphere this is a stringent joint condition, and **it logs nothing when it
rejects.**

{: .caveat }
> **The "100% nitrogen valence" mechanism is imported from a different, easier run.** The
> "151 of 170 error lines, 100% nitrogen" figure comes from job **14292188** — a run that
> *also* produced **126 mask-1 + 4 mask-2 valid** structures.[^mech2] The headline **maskall
> = 0 / 6,300** is job **14344725**, whose error log contains only **5** sanitization
> messages total.[^maskerr] The generate scripts do **not** disable RDKit logging,[^nolog]
> so if 6,300 attempts produced just 5 sanitize errors, **~6,295 were rejected *before*
> reaching RDKit** — silently, at the molSimplify overlap / exact-atom-count gate (or as
> caught `FoundNaNException` samples). Attributing **0 / 6,300** to "nitrogen in impossible
> 4-bond environments" borrows a statistic from the mask-1/2-dominated run; the bare-metal
> run's own bottleneck is the **silent geometric gate**, not a logged chemical verdict.

The result may still be a real limitation. But as written, **the metric cannot tell model
incapacity apart from instrument brittleness** — exactly the confusion the project already
resolved once, by visual inspection, for mask 1. No bare-metal output was inspected that way.

## Finding 2 — the validity gate cannot pass a nitrate, and the reference is built from three

This is a concrete bug, not a framing issue. `molecule_builder.make_mol_openbabel` rebuilds
every atom as `Chem.Atom(atom.GetSymbol())` — **symbol only** — then copies bonds and calls
`Chem.SanitizeMol`.[^obabel] The comment says this "is a workaround to remove radicals"; it
also **discards every formal charge** OpenBabel perceived.

The reference complex **Eu(TMMA)₂(NO₃)₃** (`eu_tmma_cis.xyz`) is **14 C, 7 N, 13 O, 1 Eu**:
the two TMMA ligands contribute 4 **amide** N (valence 3, fine), and the three nitrates
contribute **3 nitrate N**.[^ref] A nitrate nitrogen is formally **N⁺ with four bonds**
(one N=O, two N–O). Strip its +1 charge and call `Chem.SanitizeMol`, and RDKit raises
exactly:

```
Explicit valence for atom # N, 4, is greater than permitted
```

— which is *verbatim* the only error class in both design logs.[^mech2][^maskerr] In other
words, **a perfectly reconstructed nitrate is guaranteed to fail this gate.** The checker
structurally rejects any nitrate (or deprotonated amide, or any charged donor) that lands in
the generated region.

This single fact reorganises the whole result:

- **It explains why mask 1 "works":** the masked ligand is usually a TMMA, whose amide N has
  valence 3 and sanitizes fine; the 126 valid completions are exactly the **N-valence-safe**
  ones. Nitrate completions are silently filtered out — so even the 3.4% mask-1 yield is
  *suppressed* by this bug.
- **It dooms de-novo by construction:** a bare-Eu run must regenerate the three nitrates, and
  every correct nitrate it produces is thrown away as "valence-broken."

{: .note }
> **Two near-free fixes + a decisive sanity test.**
> 1. In `make_mol_openbabel`, copy `atom.GetFormalCharge()` (and let OpenBabel's charge model
>    run), **or** call the repo's own `reset_dative_bonds` — which already exists and is used
>    in `add_H`, but **not** in the validity gate[^dative] — **or** sanitize with a charge-aware
>    flag set so charged donors aren't auto-rejected.
> 2. **Run the gate on the pristine Kravchuk reference.** If its three nitrate fragments fail
>    `compute_validity` (they will), then the **0 / 6,300** is partly *instrumental*: the
>    instrument rejects the very molecule the model is being graded against. This is a
>    ten-minute check and it is the most important experiment on this page.

## Finding 3 — the attempt denominator is inflated with chemically impossible targets

`6,300 = 150 seeds × 42 partitions`. The 42 comes from `const.denticity_partitions(10)`,
which enumerates **every integer partition of CN = 10** — including `[10]`, `[9,1]`, `[8,2]`,
… down to ten monodentates.[^part] **19 of the 42** contain a part **> 4**, i.e. a single
ligand binding through 5–10 donor atoms — chemically absurd for these systems (the reference
is five **bidentate** ligands). Each such partition is handed to the model as a target, so a
large share of the 6,300 attempts ask for structures **no valid molecule could satisfy**,
then count the inevitable failure against the model.

The original code used curated denticity tables (`cn_oct` / `cn_nonoct`); replacing them with
the complete mathematical generator was necessary for CN 7–10 but **over-generates**. Cap
`max_denticity` (≤ 4 covers real chelates) and/or weight partitions by the **CSD-observed**
denticity distribution already computed in the [dataset](dataset.html). That both shrinks the
denominator and concentrates sampling on targets a correct model could actually hit.

## Finding 4 — the de-novo task is under-specified: denticity is given, composition is not

In `generate.py → reform_data`, each generated ligand is assigned a denticity and an atom
budget drawn **at random**: `g_ligand_size = np.random.randint(num_coord_site, 10)` for
mono/bidentate slots.[^reform] The model is told *"make a bidentate ligand of (say) 3 atoms,
donors here"* — but **never which elements**. It cannot know a slot should be a nitrate
(N + 3 O) versus an amide; for a bidentate slot it may even be handed a 2-atom budget, too
few to form a nitrate at all.

So "de-novo design" as currently posed asks the model to invent **composition and geometry
simultaneously, with neither specified** — an ill-posed prompt, distinct from "the model
cannot compose." This is precisely the gap the [Strategy](strategy.html) calls
*spec-conditioned / predict-then-build*, and it has a concrete code locus: condition on
donor-atom identity (or a target ligand skeleton), and set atom budgets from chemistry rather
than `randint`.

## Finding 5 — the exclusion-shell projection is mis-tuned, and inert exactly where design happens

`src/projection.py` pushes generated atoms to at least `d_min` from **cross-group context**
atoms, with `d_min` annealed **1.5 → 1.3 Å**.[^proj] But bond perception fires far higher —
at ~1.3× covalent-radii sums: **C–C ≈ 1.98, C–N ≈ 1.91, C–O ≈ 1.85, N–O ≈ 1.78, O–O ≈ 1.72 Å**.[^dmin]
A `d_min` of 1.3–1.5 Å sits **below** every one of those thresholds, so the projection can
push two atoms apart and they will **still be perceived as bonded** — it cannot prevent the
cross-ligand "fusion" it was built to prevent.

Two further limits make it a **no-op in the de-novo case**:

- It only acts on **generated ↔ context** pairs and explicitly **skips the metal** (group −1).
  In maskall the context *is* only the metal, so there are **no eligible pairs**.
- It never projects **generated ↔ generated** cross-group pairs — yet when all ligands are
  generated, those are the *only* contacts that matter.

And it was only ever switched on in `sbatches/dblock_cross`, `context_ablation`, and
`projection_stack`[^projused] — the three the [Strategy](strategy.html) page itself flags as
having "no supporting job logs." The real de-novo run used `--resample_r 2` and **no
projection**.[^maskcfg] To make the module do its job: raise `d_min` **above** the bond
cutoff (~1.8–2.2 Å for donor pairs) and extend it to generated–generated cross-group pairs.

## Finding 6 — three different bond conventions across train / generate / validate

The pipeline decides "what is bonded" three incompatible ways:

| Stage | Rule | Source |
|---|---|---|
| Training-data prep | hard **1.9 Å** organic cutoff, **3.0 Å** donor cutoff (CrystalNN when available) | `prepare_training_data.py` (`ORGANIC_BOND_CUTOFF`, `DONOR_CUTOFF`)[^prep] |
| Generation / validity | molSimplify covalent-radii bonds (`ligand_breakdown`) | `molecule_builder.sanitycheck` |
| Molecule build | OpenBabel perception + pm-scaled `BONDS_*` tables (margins 10/5/2 pm) | `molecule_builder.get_bond_order` |

The model learns *"what a ligand is"* under the 1.9 Å rule and is then graded under two
others. A spacing the model was **rewarded** for in training (atoms ~1.9 Å apart = one ligand)
can read as **overlapping or over-bonded** at validation. Unifying the bond/donor definition
across the three stages removes a whole class of train/test mismatch. (Minor: the donor
cutoff is **3.0 Å** in code but quoted as **2.8 Å** in [Methods](methods.html) — worth
reconciling.)

## Smaller things worth fixing

- **`config.yml` is a stale smoke-test template.** It declares `hidden_nf: 32`, `n_layers: 2`,
  `diffusion_loss_type: vlb`, `diffusion_noise_schedule: learned`, `n_epochs: 2`,
  `batch_size: 2` — none of which match the real fine-tune (192 / 5 / `l2` / `polynomial_2`),
  as the 227-layer load against a 192/5 checkpoint proves.[^load][^cfg] Anyone using it to
  reproduce builds the wrong model. Update or delete it.
- **`normalization_factor` mismatch (verify).** `config.yml` uses `100`; `finetune.py` passes
  `1`. It's a constructor argument, not a saved weight, so if the pretrained backbone was
  trained at a different value the transferred weights operate at a different aggregation
  scale. Confirm against the pretrained checkpoint's hyperparameters.[^normf]
- **Divide-by-zero in the sampling metrics.** `sample_and_analyze` computes
  `connected_ligand = connectivity/validity` and `valid_ligand = validity/total_ligands`; a
  batch that yields nothing valid makes these `NaN`, which then pollutes the logged
  averages.[^div]

## What more can be done — a prioritized path to a positive result

Ordered cheapest-leverage first. The first two need **no GPU** and would tell you how much of
the **0 / 6,300** is real.

1. **Re-score with a charge-aware validity gate, and test the pristine reference (Finding 2).**
   Copy formal charges in `make_mol_openbabel` / apply `reset_dative_bonds` in the gate, then
   re-run validity on the **existing** mask-1/2/3/all outputs *and* on the Kravchuk reference.
   If nitrate-bearing structures start passing, the de-novo rate was partly instrumental.
   *Hours, no training.*
2. **Cap denticity partitions to ≤ 4 (or weight by CSD) and re-run maskall (Finding 3).**
   Removes the impossible-target dilution and the inflated 6,300 denominator. *One short run.*
3. **Condition on composition / donor identity (Finding 4).** Give the model the donor-atom
   set (or a target skeleton) and chemistry-derived atom budgets instead of `randint`. Turns
   an ill-posed prompt into the well-posed *"build 2 N + 3 O, neutral, CN 8"* the
   [vision](index.html#the-vision) actually asks for.
4. **Curriculum toward bare-metal / high-mask (Strategy item b).** The masking augmentation
   enumerates all 2ᵏ−1 subsets then samples down to 20 per complex, so the **all-masked**
   config is rare;[^aug] bias augmentation toward high-mask-count and explicit bare-metal
   examples to train the regime that fails.
5. **Fix and actually enable the projection (Finding 5):** `d_min` above the bond cutoff, and
   covering generated–generated pairs — then it can suppress bridging *during* design instead
   of being a no-op.
6. **Unify bond conventions (Finding 6)** across prep, generation, and validation.
7. **Valence-aware / constrained sampling.** Mask the type channel during denoising so N
   cannot acquire > 3 heavy-atom neighbours, and/or **xTB-relax before** the validity gate
   instead of rejecting raw point clouds post-hoc — moving from "generate-and-hope" toward the
   "hard constraints inside the sampler" the [Strategy](strategy.html#track-b-next--a-coordination-aware-rare-earth-native-platform)
   borrows from the Kulik papers.

{: .note }
> **The honest bottom line.** The current **0 / 6,300** conflates two very different things —
> *the model cannot compose a sphere* and *the instrument cannot score one* — and the code
> does not let you separate them. Findings 1–2 show the instrument is demonstrably rejecting
> correct chemistry (nitrate), and Findings 3–4 show much of the denominator is asking for
> impossible or under-specified targets. **Fixing the instrument is nearly free, and it is a
> prerequisite for trusting the negative result at all.** Whatever survives those fixes — a
> real composition gap, most likely — is then a *rigorous* finding that genuinely motivates
> the coordination-aware [Track B](strategy.html#track-b-next--a-coordination-aware-rare-earth-native-platform),
> rather than a number partly manufactured by `Chem.Atom(atom.GetSymbol())`.

---

[^load]: `ln_train_h200_12124078.out` — *"Loaded exactly : 227 layers / Zero-padded : 3 layers
    (`ligand_site_embedding.weight [192,8]→[192,12]`, `h_embedding_out.weight [16,192]→[20,192]`,
    `h_embedding_out.bias [16]→[20]`) / Reinitialized : 1 layers (`edm.gamma.gamma`)."*
    Matches `finetune.py → load_pretrained_weights` (zero-pad on grown dims) and the documented
    7→11 (`MAX_LIGANDS+1`) input growth.

[^gate]: `generate.py → generate_ligand` (~L264–272): `overlapping,liglist = sanitycheck(...)`;
    `total_atoms = sum(len(lig) for lig in liglist)+1`; gate `if not overlapping and
    total_atoms == natoms[i]`; then `compute_validity` (= `Chem.SanitizeMol`) and
    `compute_connectivity`. The identical gate is the training-time metric in
    `lightning.py → sample_and_analyze`, which reported `valid_complex 0.005`.

[^mech2]: `ln_design_14292188.err`: **170** lines, **151** = `Explicit valence for atom # N, 4,
    is greater than permitted` (100% nitrogen, valence 4). This is the run that also wrote
    **126** mask-1 and **4** mask-2 valid structures (`design_test_runs/14292188/`), per
    [Results](results.html#the-design-test-completion-vs-de-novo).

[^maskerr]: `ln_maskall_14344725.err`: **9** lines total, **5** N-valence messages; `.out`:
    *"maskall  context=0/5  attempts=6300  valid=0  yield=0.00%"*. The maskall sbatch ran
    `--mask_k all 3 2 --n_samples 150 --resample_r 2`.

[^nolog]: `generate.py`, `generate_design_test.py`, `generate_mask1.py` contain no
    `disable_rdkit_logging()` call (it *is* called in `finetune.py`). So RDKit sanitize errors
    print to stderr during generation; their near-absence in the maskall log means sanitize was
    rarely reached.

[^obabel]: `molecule_builder.py → make_mol_openbabel` (~L173–181):
    `mol.AddAtom(Chem.Atom(atom.GetSymbol()))` (symbol only — no `SetFormalCharge`), then bonds
    copied and `Chem.SanitizeMol` via `BasicLigandMetrics.compute_validity` (~L191–201).
    Reproducer (run in the project's RDKit env): build N with one `DOUBLE` + two `SINGLE` bonds
    to O, **formal charge 0**, `Chem.SanitizeMol` → "Explicit valence for atom N, 4, greater
    than permitted"; set N `+1` and two O `−1` → sanitizes.

[^ref]: `eu_tmma_cis.xyz` element counts: 14 C, 7 N, 13 O, 1 Eu = 35 heavy atoms. TMMA ×2 → 4
    amide N + 4 carbonyl O; NO₃ ×3 → 3 nitrate N + 9 O. So 3 of 7 N are nitrate N⁺(valence 4).

[^dative]: `molecule_builder.py → reset_dative_bonds` (~L261–289) exists and is applied in
    `generate.py → add_H` before a charge-tolerant `SanitizeMol(... ^ SANITIZE_ADJUSTHS)`, but
    **not** in `compute_validity`, which uses a bare `Chem.SanitizeMol`. The validity gate is
    therefore stricter than the H-adding path on the same molecule.

[^part]: `const.denticity_partitions(10)` → 42 partitions (Python `p(10)=42`); 23 have all
    parts ≤ 4, so **19** contain a part > 4. `reform_data` builds one model-ready `Data` per
    partition, so 150 seeds × 42 = 6,300.

[^reform]: `generate.py → reform_data` (~L199–203): `if num_coord_site < 3:
    g_ligand_size = np.random.randint(num_coord_site, 10)` else
    `get_ligand_size(..., startnum=10, endnum=30)`. Element identities of generated atoms are
    initialised to zeros and produced by the model; they are never conditioned on a target
    composition.

[^proj]: `src/projection.py → d_min_schedule` anneals `d_min_start=1.5 → d_min_end=1.3`;
    `project_exclusion_shell` skips same-group pairs and metal context (`group_id == -1`), and
    only considers generated↔context pairs.

[^dmin]: 1.3× (covalent-radii sum), radii C 0.76, N 0.71, O 0.66 Å → C–C 1.98, C–N 1.91,
    C–O 1.85, N–N 1.85, N–O 1.78, O–O 1.72 Å. All exceed the projection's 1.3–1.5 Å `d_min`.

[^projused]: `grep "project_enabled"` over the sbatches matches only
    `sbatches/dblock_cross.sbatch`, `sbatches/context_ablation.sbatch`,
    `sbatches/projection_stack.sbatch` (all `--project_enabled True`).

[^maskcfg]: `run_design_maskall.sbatch`: `--mask_k all 3 2 --n_samples 150 --resample_r 2`
    (no `--project_enabled`).

[^prep]: `prepare_training_data.py`: `DONOR_CUTOFF = 3.0`, `ORGANIC_BOND_CUTOFF = 1.9`;
    `build_bond_graph` prefers `CrystalNN`, falls back to these distance cutoffs;
    `decompose_ligands` uses the 1.9 Å cutoff for connected components.

[^cfg]: `config.yml`: `hidden_nf: 32`, `n_layers: 2`, `normalization_factor: 100`,
    `diffusion_noise_schedule: learned`, `diffusion_loss_type: vlb`, `n_epochs: 2`,
    `batch_size: 2`. `finetune.py` defaults: `hidden_nf=192`, `n_layers=5`,
    `normalization_factor=1`, `polynomial_2`, `l2`.

[^normf]: `Dynamics(... normalization_factor=...)` is passed to `GVPNetwork` at construction; it
    is configuration, not a checkpoint tensor, so a train/finetune mismatch is not caught by
    the shape-based loader in `load_pretrained_weights`.

[^div]: `lightning.py → sample_and_analyze` (~L326–328): `valid_ligand = validity/total_ligands`,
    `connected_ligand = connectivity/validity` — no guard for zero denominators.

[^aug]: `prepare_training_data.py → generate_masking_augmentations`: enumerates all
    `2ᵏ−1` non-empty ligand subsets, then `random.sample(..., max_augment=20)`. The single
    all-masked subset is 1 of 2ᵏ−1 and is increasingly unlikely to survive downsampling as k
    grows.
