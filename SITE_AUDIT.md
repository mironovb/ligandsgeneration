# SITE AUDIT — Lanthanide Ligand Generation tracker

**Scope.** Quality-assurance pass over the built site in `site/` (Prompt 5). Every
quantitative claim on every page was cross-checked one more time against
`VERIFICATION_REPORT.md`. This file lists each headline number, the page(s) it appears on,
and its source; flags any mismatch; confirms nothing marked *unverified/partial* in the
verification report is presented as a settled fact; and records gaps under *Gaps to
resolve*.

**Result.** Site builds clean (`bundle exec jekyll build` → 0 errors / 0 warnings, 8 HTML
pages). **One framing mismatch found and fixed** (strategy.md Ln–donor distance, see §3).
No new factual claims were introduced. All project-result numbers trace to the verification
report; all literature numbers trace to `LITERATURE_AND_STRATEGY.md` / the cited papers; all
figures (`assets/figures/*.svg`) regenerate from verified scalars in `make_figures.py`.

Page keys: **idx** = Home (`index.md`), **bg** = Background, **meth** = Methods,
**res** = Results, **log** = Experiment Log, **strat** = Strategy, **conc** = Conclusions,
**chg** = Changelog, **fig** = an SVG figure.

---

## 1. Headline-number traceability

Status legend: ✓ verified & sourced · ⚑ unverified, **flagged on-site** (not a settled
fact) · ◐ partial/cut-off, **labeled on-site**.

### Training

| Number | Appears on | Source (VERIFICATION_REPORT.md) | Status |
|---|---|---|---|
| val_loss start **977.76 / 977.8** | idx, res, strat, chg, fig | `ln_train_h200_12124078.out:76` (§2) | ✓ |
| best **49.913 / 49.9 @ epoch 48** | idx, res, strat, chg, fig | `ln_train_h200_12151181.out:907` (§2) | ✓ |
| **≈95% (94.9%) reduction** | idx, res, strat, chg, fig | derived 977.76→49.91 (§2) | ✓ |
| next-lowest **epoch 57 = 60.78** | res, fig | §2 | ✓ |
| **epoch 63 = 106.37**, early-stop patience 15 | res, meth, fig | `…12151181.out:1490` / `.err` (§2) | ✓ |
| best ckpt **`ln_finetuned_epoch=48.ckpt`** | res, meth, log | `ls` confirmed (§2) | ✓ |
| sampling **0.970 / 0.938 / 0.005** | res, strat | `12151181.out` best_* block (§2) | ✓ |
| **~10 GPU-h (≈9.7 h)**, 3 sessions | res, meth, log | in-log timestamps (§2) | ✓ |
| batch **256**, 335 steps → **~85,760** samples | meth | `finetune_*.sbatch` + logs (§2) | ✓ |
| **5** failed resume jobs (4× param-group bug) | res, meth, log | §2 / Disc. #4 | ✓ |

### Completion (mask 1) and xTB

| Number | Appears on | Source | Status |
|---|---|---|---|
| **126 valid** mask-1 structures | idx, res, strat, conc, fig | job `14292188`, `mask1/noH` (§4) | ✓ |
| **41 valid** (mask1_baseline gen set) | log | job `12207365` (§5) | ✓ |
| xTB **38/41 = 92.7%** converged | idx, res, strat, conc, log | `xtb_results/mask1_baseline/summary.json` (§3) | ✓ |
| xTB r=5 **81/85** | res, log | `repaint_r5/summary.json` (§3) | ✓ |

### RePaint sweep

| Number | Appears on | Source | Status |
|---|---|---|---|
| r=1 **29 / 2,500 = 1.16%** | res, strat, log, fig | job `12329152` (§3) | ✓ |
| r=5 **85 / 2,500 = 3.40%** | res, strat, log, fig | job `12329152` (§3) | ✓ |
| r=10 **57 / 1,500 = 3.80%** | res, strat, log, fig | job `12340606` (§3) | ✓ |
| r=20 **39 / 750 = 5.20%** | res, strat, log, fig | job `12340606` (§3) | ✓ |
| denticity **13.8% / 15.3% / 10.5%** (peaks r=5) | res, strat | `aggregate_r{1,5,10}.txt` (§3) | ✓ |
| r=10 denticity computed on **19 (partial)** | res | `aggregate_r10.txt` (§3) | ◐ labeled |

### Metric caveat (bond graph)

| Number | Appears on | Source | Status |
|---|---|---|---|
| **9/38 = 24%** returned 5 fragments | res | `bond_classification.csv` (§3) | ✓ |
| **29/38 = 76%** returned 3–4 fragments | res, conc | same (§3) | ✓ |
| **23/38 = 60.5%** new cross-ligand bonds | res, conc | same (§3) | ✓ |

> The 60.5% is presented as a **geometry sensitivity check, explicitly "not evidence of
> chemical fusion"** (res §metric-caveat). ✓ — see §2 below.

### Design test (the headline result)

| Number | Appears on | Source | Status |
|---|---|---|---|
| **maskall = 0 valid / 6,300 = 0.00%** | idx, res, strat, conc, log, fig | job `14344725`, `ln_maskall_…out/.err` (§4) | ✓ |
| **6,300 = 150 seeds × 42 partitions** | res, log | §4 | ✓ |
| scaffold gradient **126 → 4 → 0 → 0** | res, strat, conc, fig | jobs `14292188` + `14344725` (§4) | ✓ |
| mask 2 = **4** | res, conc, log | job `14292188`, `mask2/noH` (§4) | ◐ cut-off, labeled |
| mask 3 = **0** | res, log | job `14344725`, empty `mask3/noH` (§4) | ◐ cut-off, labeled |
| N-valence rejections **151/170, ~100% N** | res, strat, conc | `grep -c` on `.err` (§4) | ✓ |

### Corrections to PROJECT_OVERVIEW.md (stated as corrections, never as the old value)

| Correction | Appears on | Source | Status |
|---|---|---|---|
| r=10 is **57/1,500 = 3.80%**, *not* 19/300/6.33% | res, strat, chg | §6 Disc. #1 | ✓ |
| total valid **171** (or 210 w/ r=20), *not* 133 | res, strat, log, chg | §6 Disc. #2 | ✓ |

### Reference complex (literature fact)

| Number | Appears on | Source | Status |
|---|---|---|---|
| Eu(TMMA)₂(NO₃)₃, **CN 10, 5 ligands, 35 heavy atoms, cis**, CCDC VEDTAA01 | bg, papers.yml | Kravchuk 2024 EurJIC (`kravchuk2024ejic`) | ✓ lit |

### Literature benchmarks on the Strategy page (attributed to the Kulik / pydentate papers)

| Number | Appears on | Source | Status |
|---|---|---|---|
| pydentate **75% de-novo DFT success** (overall) | strat | LIT&STRAT §1 / PNAS 2025 | ✓ lit |
| pydentate **88% DFT success when coordination correct** | strat | LIT&STRAT §1 (distinct from the 75%) | ✓ lit |
| pydentate **1.50 Å RMSD** vs CSD | strat | LIT&STRAT §1 | ✓ lit |
| Jiang **~29,891** mononuclear Ln complexes | meth, strat, papers.yml | Li 2025 ICC (`li2025icc`) | ✓ lit |

> The **75%** (overall de-novo) and **88%** (conditional on correct coordination) are two
> different metrics from the same pydentate study and are stated as such — not a
> contradiction.

---

## 2. Unverified / partial claims — confirmed flagged, **not** presented as settled fact

Each item below is something `VERIFICATION_REPORT.md` could **not** confirm from the
download (§6 + "could not be checked"). All are explicitly marked on-site and none is stated
as an established result.

| Claim | On-site treatment | OK? |
|---|---|---|
| CSD pipeline counts (53,333 / 31,979 / 9,306 / 6,563 / 216,509 / 54,946) | meth — inside a `{: .unverified}` callout ("could not be checked from this download … not independently verified") | ✓ |
| Pipeline validation table (53,370; 29,891; donor 65/18/14%; **2.61→2.43 Å**; CN 8 = 9,658) | meth — under the same `{: .unverified}` callout, "Reproduced from PROJECT_OVERVIEW.md §4" | ✓ |
| Architecture internals (5 layers, 192+32 features, ~3.8M params, T=500) | meth — `{: .unverified}` ("from PROJECT_OVERVIEW.md, not independently verified") | ✓ |
| Visual/geometry (Avogadro, TMMA-shaped 5th fragment, Eu–O 2.3–2.6 Å, 0% cross-bonds for pristine ref) | res — `{: .unverified}` callout; used in narrative then immediately caveated in the adjacent block | ✓ |
| DFT validation | conc — `{: .unverified}` ("**No DFT has been run** … only ORCA templates exist"); strat — "do not claim DFT as done" | ✓ |
| `paper/` "Prompts 1–10" artifacts (context-ablation, cross-arch, projection-stack 6.4%, "DFT submitted") | strat — `{: .fails}` "what to leave out"; experiments.yml — five `not-run` rows naming each | ✓ |

**Framing check (Prompt 5 §2) — all pass:**

- **No revert to "side-chain elaboration."** The phrase appears once, on res, inside a
  `{: .caveat}` block that calls it an early framing which "was an artifact and was
  corrected." mask 1 completion is stated to *work* on idx, res, conc, strat — consistently.
- **Bond-graph numbers are a sensitivity check, not fusion.** The 60.5% is explicitly "a
  sensitivity check on geometry … **not** evidence of chemical fusion" (res).
- **The de-novo failure (0/6,300) is the stated real limitation**, identically on idx
  ("✗ fails"), res ("De-novo design fails, with a mechanism"), conc ("cannot compose a
  valence-correct coordination sphere"), and strat ("Result 2").
- **Kulik papers positioned as coordination-representation, not generation.** bg and strat
  both state "all three characterize, predict, or classify … none of them generate," and
  cast them as inputs to Track B (predict-then-build, coordination-aware representation) —
  never as generation methods.

---

## 3. Mismatch found and corrected

**strategy.md, design principle #8 (Ln–donor distance).** The page read
"…contracts smoothly (**project-measured** 2.61 Å (La) → 2.43 Å (Lu))", presenting the
figure as an established project measurement. The **same figure is flagged `{: .unverified}`
on methods.md** (the CSD-pipeline distance trend the verification report lists as
unverifiable from the download, §6). Presenting it as settled on one page and unverified on
another is exactly the inconsistency this audit guards against.

**Fix applied (this prompt):** strategy.md now reads "…the project's CSD pipeline reports
2.61 Å (La) → 2.43 Å (Lu) — an *unverified* pipeline figure, consistent with the lanthanide
contraction; see [Methods](methods.html#the-csd-data-pipeline)." The qualitative point
(contraction as the selectivity handle) is unchanged; the specific numbers now carry the
same caveat as on Methods. No other page states these distances as fact.

No mismatch was found in any verified number — every value in §1 matches the verification
report exactly (including the two corrections, which are presented *as* corrections).

---

## 4. Gaps to resolve

Per the Prompt 5 constraint, a "gap" is a number the site **needs but the verification
report never established**. **The site has no unfilled hole** — every number it presents is
either verified (sourced in §1) or marked unverified/partial (§2) — so **no new placeholder
was required.** The items below are the *tracked* gaps: claims the site relies on that are
not log-verified, already marked on-site, to be closed when the underlying data/logs become
available.

1. **CSD data-pipeline counts** (53,333 / 31,979 / 9,306 / 6,563 / 216,509 / 54,946; donor
   and CN distributions; Ln–donor distances). *Needs:* the source CIFs,
   `prepare_training_data.py` output, or the candidates CSV — none present in the download.
   *Marked:* meth `{: .unverified}`.
2. **Architecture internals** (5 layers, 192+32 features, ~3.8M params, T=500 schedule).
   *Needs:* loading a checkpoint or the training config (deliberately not done).
   *Marked:* meth `{: .unverified}`.
3. **Geometry/visual claims** (Eu–O 2.3–2.6 Å; "0% cross-bonds" for the pristine reference).
   *Needs:* opening `metrics/results/control/pristine_reference.json` and measuring
   generated structures. *Marked:* res `{: .unverified}`.
4. **mask 2 (= 4) and mask 3 (= 0) are partial** (time-limit cut-offs; mask 3's attempt
   count is unknown — only the empty output directory proves 0 valid). *Needs:* a dedicated
   re-run. *Marked:* res / conc / log as "(cut off)" and "partial." (conc already lists the
   mask-2 re-run as next step #1.)

None of these blocks publication of the verified Track-A story; all are either Track-A
polish (item 4) or Track-B groundwork.

---

## 5. Build & hygiene sign-off

- `bundle exec jekyll build` (Homebrew Ruby 4.0.5): **0 errors, 0 warnings**, 8 pages
  (`index, background, methods, results, experiment-log, strategy, conclusions, changelog`).
- Status banner reads its date from a single source (`status_date` in `_config.yml`) via
  `_includes/status.html`. ✓
- `.gitignore` excludes all heavy artifacts (`*.ckpt *.tgz *.tar *.pt *.npy *.npz *.sdf`,
  `design_test_runs/ generated/ xtb_*/ __pycache__/`) plus build output and `vendor/`. ✓
- Figures (`training_curve`, `repaint_sweep`, `design_degradation`) contain only verified
  scalars and regenerate via `python3 assets/figures/make_figures.py`. ✓

*Audit complete. One framing fix applied to strategy.md; no other site changes to claims.
No new facts introduced.*
