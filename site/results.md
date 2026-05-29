---
layout: default
title: Results
nav_order: 4
---

# Results
{: .no_toc }

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

{: .note }
> Every number on this page is traceable: footnotes cite the job id, log file, or metrics
> file it came from.

## Training

Fine-tuning drove the validation loss down sharply and then triggered early stopping:

- **Start:** epoch 0 = **977.76**.[^start]
- **Best:** epoch 48 = **49.913** — the global minimum (next-lowest is epoch 57 at
  60.78).[^best] That is a **≈95% reduction** (94.9%).
- Logging continued through epoch 63 (val_loss 106.37), where **early stopping fired**
  (patience 15 on validation loss).[^last]
- **Best checkpoint:** `models/ln_finetuned/ln_finetuned_epoch=48.ckpt`.
- **Convergence sampling metrics:** valid_ligand **0.970**, connected_ligand **0.938**,
  valid_complex **0.005**.[^sampling] The first two (per-fragment chemical validity) are
  strong; the third (whole-complex validity) is low — which set up the generation
  analysis below.

<figure style="margin:1.2em 0;">
  <img src="{{ '/assets/figures/training_curve.svg' | relative_url }}" alt="Validation loss falling from 977.8 at epoch 0 to a minimum of 49.9 at epoch 48, then rising to 106.4 at epoch 63 where early stopping fires." style="max-width:100%; height:auto; border:1px solid #e2e8f0; border-radius:6px;">
  <figcaption style="font-size:0.88em; color:#64748b; margin-top:0.45em;">
    Validation loss at the four epochs the verification report records individually
    (start, global minimum, next-lowest, last). The dashed line is the trajectory through
    these anchors — intermediate epochs were not individually logged here, so none are
    invented. Sources: <code>12124078.out:76</code>, <code>12151181.out:907</code> and <code>:1490</code>.
  </figcaption>
</figure>

**Compute and session history.** Training took **~10 GPU-hours** (≈9.7 h) across three
sessions.[^gpu] The runs were *not* a clean string of resumes, however: only one session
was time-limit-cancelled, one **crashed** (a molSimplify `IndexError` during sampling),
and the third **finished cleanly** via early-stop — and before those, **five** resume
attempts failed at startup (four with "loaded state dict has a different number of
parameter groups," the discriminative-LR resume bug).[^sessions] See the full breakdown
in the [Experiment Log](experiment-log.html).

## RePaint sweep

All sweep generation uses **mask 1** on the Eu(TMMA)₂(NO₃)₃ reference (fix the full
complex, hide one ligand, regenerate it). **RePaint** (Lugmayr 2022) oscillates `r` times
between re-noising and denoising at each step so the generated region re-aligns with the
fixed context; it is ported via `--resample_r` and needs no retraining.

| Sampler | Attempts | Valid | Yield | Denticity match |
|---|---:|---:|---:|---:|
| Baseline (r = 1) | 2,500 | 29 | 1.16% | 13.8% (4/29) |
| **RePaint r = 5** | 2,500 | 85 | 3.40% | **15.3% (13/85) — best** |
| RePaint r = 10 | 1,500 | 57 | 3.80% | 10.5% (2/19, partial)† |
| RePaint r = 20 | 750 | 39 | 5.20% | — |

<small>Sources: r=1, r=5 from job <code>12329152</code>; r=10, r=20 from job
<code>12340606</code>; denticity from <code>metrics/results/aggregate_r*.txt</code>.[^sweep]
† The r=10 denticity rate was computed on a **partial** set of 19 structures (the only
aggregate available), not the 57 from the completed run.</small>

<figure style="margin:1.2em 0;">
  <img src="{{ '/assets/figures/repaint_sweep.svg' | relative_url }}" alt="Bar chart of valid-complex yield: 1.16% at r=1, 3.40% at r=5 (working point), 3.80% at r=10, 5.20% at r=20." style="max-width:100%; height:auto; border:1px solid #e2e8f0; border-radius:6px;">
  <figcaption style="font-size:0.88em; color:#64748b; margin-top:0.45em;">
    Valid-complex yield rises monotonically with the resampling parameter r. But
    donor-placement quality (denticity-match, in the table) peaks at r = 5 and then
    <em>drops</em> at r = 10 — so <strong>r = 5 is the working point</strong>: past it you
    get more structures that clear the coarse validity filter but are no better at the
    fine-grained placement metric.
  </figcaption>
</figure>

**xTB stability.** Under GFN2-xTB optimization, **38/41 (92.7%)** of the mask1_baseline
structures converged, and 81/85 of the r=5 set.[^xtb]

Across the full sweep that is **171 valid structures** (r1 + r5 + r10 = 29 + 85 + 57), or
**210** including r = 20. The story is the monotonic yield rise (1.16 → 3.40 → 3.80 →
5.20%) with denticity-match peaking at r = 5.

## The metric caveat

{: .caveat }
> An early framing of this project claimed the model was *"doing side-chain elaboration,
> not novel ligand design,"* on the basis of a connected-component fragment count: only
> **9 of 38** xTB-converged structures (24%) returned the expected 5 distinct ligand
> fragments; the other **29/38 (76%)** returned 3 or 4.[^bond] **That framing was an
> artifact and was corrected.**

**What actually happened.** Visual inspection in Avogadro showed that most files *do*
contain a clean, separate fifth fragment in the masked position — TMMA-shaped, diamide
backbone present, carbonyl oxygens pointed at the Eu, with Eu–O distances in the expected
2.3–2.6 Å range. The fragment-count metric was an **artifact of the bond-detection
cutoff**: the 1.3× covalent-radii rule merges atoms that sit at threshold-ambiguous
distances to a context ligand, even when no real bond exists.

The same artifact shows up under GFN2-xTB: **60.5% (23/38)** of converged structures
showed "new" cross-ligand bonds after optimization,[^fusion] versus 0% for the pristine
Kravchuk reference under the same protocol. This **60.5% is a sensitivity check on
geometry** (some generated atoms do sit slightly close to context) — **not** evidence of
chemical fusion; xTB simply locks in whatever the bond detector was already flagging at
borderline distances.

{: .unverified }
> The visual-inspection and geometry claims (Avogadro confirmation, "TMMA-shaped" fifth
> fragment, Eu–O 2.3–2.6 Å, "0% cross-bonds for the pristine reference") are **inherently
> not log-verifiable** and were not re-measured here; one example structure read during
> the audit is consistent with a real Eu coordination sphere. The fragment-count and
> cross-bond *rates* (24% / 76% / 60.5%), however, **are** confirmed from
> `bond_classification.csv`.

**Corrected conclusion.** mask 1 *works*: the model regenerates a sensible TMMA in the
right place in most cases. This correction matters because it changed the story from "the
model fails" to "the model completes well — but does it *design*?" — which is exactly what
the next experiment tests.

## The design test (completion vs de-novo)

mask 1 only tests **completion**: giving the model 4 of 5 ligands and asking it to fill in
the fifth is easy, because the training set has many near-homoleptic complexes. To test
**design**, the experiment **sweeps how many ligands are masked at once**, shrinking the
scaffold — until *mask all* leaves only the bare Eu center (true de-novo generation of a
whole coordination sphere).

| Mask level | Context | Attempts | Valid | Yield |
|---|---|---:|---:|---:|
| mask 1 | 4 of 5 ligands | (completion) | **126** | works |
| mask 2 | 3 of 5 ligands | (cut off) | 4 | low, nonzero |
| mask 3 | 2 of 5 ligands | (cut off) | **0** | 0% |
| mask all | 0 ligands (bare Eu) | **6,300** | **0** | **0.00%** |

<small>Sources: mask1 = 126, mask2 = 4 from job <code>14292188</code>; mask3 = 0 and
maskall = 0/6,300 from job <code>14344725</code>.[^design] 6,300 = 150 seeds × 42
denticity partitions. mask 2 = 4 is the handful that exist from the first run before its
time limit; mask 3 was cut off, and only the empty output directory proves 0 valid.</small>

<figure style="margin:1.2em 0;">
  <img src="{{ '/assets/figures/design_degradation.svg' | relative_url }}" alt="Bar chart: 126 valid at mask 1, 4 at mask 2, 0 at mask 3, 0 at mask all (0 of 6,300 attempts)." style="max-width:100%; height:auto; border:1px solid #e2e8f0; border-radius:6px;">
  <figcaption style="font-size:0.88em; color:#64748b; margin-top:0.45em;">
    Validity collapses as context is removed: 126 → 4 → 0 → 0. With two ligands hidden
    (mask 3) the model already produces nothing valid; from a bare Eu it produces
    <strong>0 valid out of 6,300 attempts</strong>.
  </figcaption>
</figure>

{: .fails }
> **De-novo design fails, with a mechanism.** The rejections are overwhelmingly *"Explicit
> valence for atom # N (nitrogen), 4, is greater than permitted"* — **151 of 170** error
> lines in the design run, **100% nitrogen**.[^mech] These are not geometric near-misses;
> they are **valence-broken molecules**. Forced to invent an entire ~35-heavy-atom sphere
> around a bare Eu in a fully connected graph, atoms crowd, and bond perception then finds
> nitrogens with four neighbors within bonding distance. The model learned local "fill the
> gap consistent with neighbors," but has **no notion of composing a valence-correct
> fragment from scratch.**

This is a clean negative result — but **before** reading it as a pure model-capability
verdict, see the [Code Review](code-review.html): the same validity instrument flagged here
also structurally **rejects a correctly-built nitrate** (the reference has three), and the
"100% nitrogen" statistic is from a different run — so part of this **0** is the *checker*,
not the model. The code review lists the cheapest fixes that would either move the number off
zero or make the negative result rigorous. It directly motivates the [Strategy](strategy.html).

---

[^start]: epoch 0 = 977.76: `ln_train_h200_12124078.out:76`.

[^best]: epoch 48 = 49.913, the global minimum (next-lowest epoch 57 = 60.78):
    `ln_train_h200_12151181.out:907`.

[^last]: Logged through epoch 63 (val_loss 106.37), `...12151181.out:1490`; early stop:
    *"Monitored metric loss/val did not improve in the last 15 records. Best score:
    49.913"* (`12151181.err`).

[^sampling]: "best_*" block at the end of `12151181.out`: best_valid_ligand 0.970,
    best_connected_ligand 0.938, best_valid_complex 0.005.

[^gpu]: Sum of the three sessions' wall windows ≈ 9.7 h (12124078 ≈ 29 min; 12138834
    ≈ 4.0 h; 12151181 ≈ 5.2 h), from timestamps printed inside the logs.

[^sessions]: VERIFICATION_REPORT.md §2 / Discrepancy #4: 12124078 crashed at epoch 9
    (molSimplify); 12138834 hit the 4 h TIME LIMIT (epochs 9–29); 12151181 finished
    cleanly via early-stop (epochs 26–63). Five additional jobs (12130545, 12131531,
    12131768, 12133526, 12136600) failed at startup.

[^sweep]: r=1 ("29 valid / 2500 attempted") and r=5 ("85 valid / 2500") from job
    `12329152`; r=10 ("Totally 57 valid", 1,500 attempts) and r=20 (39 valid / 750) from
    job `12340606`; directory `.xyz` counts corroborate. Denticity "Exact match" from
    `metrics/results/aggregate_r{1,5,10}.txt`. The r=10 denticity aggregate covers only the
    partial 19-structure set that was saved, not the full 57; the completed-run yield
    (57/1,500 = 3.80%) is exact.

[^xtb]: `xtb_results/mask1_baseline/summary.json` = 41 entries, 38 `xtb_success:true`
    (92.7%); `repaint_r5/summary.json` = 81/85.

[^bond]: `metrics/results/bond_classification.csv` (38 rows): n_ligands_raw = 5 in 9/38
    (24%); = 3 or 4 in 29/38 (76%).

[^fusion]: Same file: `added_cross_ligand ≥ 1` in 23/38 = 60.5%.

[^design]: `design_test_runs/14292188/` (mask1 = 126 in `mask1/noH`, mask2 = 4 in
    `mask2/noH`); `design_test_runs/maskall_14344725/` — `ln_maskall_14344725.out`:
    *"maskall context=0/5 attempts=6300 valid=0 yield=0.00%"*; `mask3/noH` empty.

[^mech]: `grep -c` on `ln_design_14292188.err` = 151 of 170 lines are the N-valence error,
    100% nitrogen; `ln_maskall_14344725.err` = 5/5, all N (VERIFICATION_REPORT.md §4).
