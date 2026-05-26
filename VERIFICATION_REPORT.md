# VERIFICATION REPORT — Lanthanide Ligand Generation repo

**Scope:** Independent, read-only audit of the downloaded working directory
(`/Users/mironovb/ligandgen`), verifying what actually ran and what the results were,
directly from files. `PROJECT_OVERVIEW.md` was used only for narrative context; every
number below was checked against logs, directories, and metrics files.

**Method note:** No `FILE_MANIFEST.txt` / `JOB_LOG_SUMMARY.txt` exist anywhere
(`find . -name FILE_MANIFEST.txt` → empty), so everything was verified from primary
files. Large binaries (`.ckpt`, `.pt`, `.tgz`, `.xyz`, `xtbopt.log`) were never read into
context — only sized/counted. Job logs were inspected with `head`/`tail`/`grep -c`, never
`cat` on the large ones. The real project lives in `multi_LigandDiff/`, which is itself a
git repository.

---

## 1. Repo map

Top level of `/Users/mironovb/ligandgen` (`ls -la`):

| Entry | What it is |
|---|---|
| `PROJECT_OVERVIEW.md` (23.6 KB) | The narrative doc under audit |
| `multi_LigandDiff/` | The actual project + code + results (a git repo) |
| `papers/` | 3 PDFs (chemrxiv 10.3 MB, ensemble-learning 4.6 MB, hemilabile 3.0 MB) |
| `prompts/` | The five task prompts |
| `.arun/`, `.DS_Store` | harness / macOS cruft |

`multi_LigandDiff/` totals 3,091 files / 472 dirs. Key subdirectories:
`data/` (training tensors), `model/` (TM pretrained ckpt), `models/ln_finetuned/`
(Ln finetune ckpts + wandb), `generate/` `generated/` `design_test_runs/`
(sampled structures), `xtb_results/` `xtb_opt/` (xTB post-processing),
`metrics/results/` (failure-mode analysis), `sbatches/` (extra job scripts),
`paper/` `report_2_ln_diffusion_2026-04-23/` `*_download/` (write-ups & bundles),
`src/` (the model code).

### Large binaries (sized, not read — `find … | xargs stat`)

| Path | Size | Type |
|---|---|---|
| `multi_LigandDiff/data/train_ln.pt` | 485 MB | training tensor set |
| `multi_LigandDiff/data/val_ln.pt` | 53 MB | validation tensor set |
| `multi_LigandDiff/model/pre_trained.ckpt` | 51.8 MB | TM pretrained checkpoint |
| `multi_LigandDiff/models/ln_finetuned/ln_finetuned_epoch={02,03,04,08,25,48,55,57}.ckpt` | 51.6 MB each | Ln finetune checkpoints (epoch=48 is best) |
| `.../.git/objects/pack/*.pack` | 61.5 MB | git history |
| `multi_LigandDiff/data/train_smiles_diff_ligands.json` | 6.9 MB | original TM-repo SMILES (not Ln) |
| `multi_LigandDiff/data/{ppr.pt, sco_615.pt}` | 6.8 / 4.2 MB | original-repo artifacts |
| `multi_LigandDiff/xtb_results/**/xtbopt.log` | many ≈0.5–1.5 MB | xTB optimization traces |
| `multi_LigandDiff/image/toc.png` | 11.9 MB | figure |

### Major `.py` scripts (header + `argparse` flags only)

| Script | Purpose (from docstring) | Key flags |
|---|---|---|
| `train.py` | Base multi-LigandDiff training entry | `--config --exp_name --resume --n_epochs --data --diffusion_steps --lr --batch_size` |
| `finetune.py` | **Fine-tune on Ln data**; loads TM weights (ligand_node_nf 7→11) by **zero-padding**, uses **discriminative LRs** | `--pretrained --epochs --batch_size --lr_head --lr_backbone --early_stop_patience --resume_from_checkpoint` |
| `prepare_training_data.py` | Convert CIFs → `train_ln.pt`/`val_ln.pt` | `--cif_dir --candidates --max_augment --val_fraction --workers --resume --consolidate_only` |
| `generate.py` | Full / multi-mask generation; RePaint + projection | `--complex --model --n_samples --ligand_sizes --resample_r --project_enabled --d_min_start/end` |
| `generate_mask1.py` | Single-ligand completion (mask1) | same flag set as `generate.py` |
| `generate_design_test.py` | **Mask-size sweep** (mask1/2/3/all) for the design test | `--mask_k --n_samples --resample_r --add_Hs` |
| `generate_bare.py` | Total generation from a bare metal (CN_c=0) | `--target_cn --n_samples --resample_r --project_enabled` |
| `xtb_opt.py` / `xtb_pipeline.py` | GFN2-xTB optimization (single / batched, multiprocessing) | pipeline: `--input-dir --output-dir --nproc --charge --uhf --aggregate` |
| `dft_pipeline.py` | Prepare/submit ORCA PBE0-D4/def2-TZVP (Stuttgart ECP on Eu) | `--xtb-results-dir --reference --mult --work-dir` |
| `analyze_repaint_sweep.py` / `analyze_gen.py` | Sweep metrics & per-structure coordination-sphere inspector | (positional / dir args) |

Generated structures are heavy-atom XYZ (`noH`). One example confirmed
(`generated/repaint_r5_epoch48/noH/0_10_eu_tmma_cis_[2, 2, 2, 2]_[2].xyz`, 26 atoms):
an Eu center surrounded by O/N/C donors — a coordination sphere in the masked position.

---

## 2. Training — VERIFIED ✓ (with one mischaracterization)

Evidence: `grep -nE "val_loss|Resuming|Start:" ln_train_h200_*.out`, `.err` tails.

**val_loss trajectory** (`=======current epoch on validation:N and current val_loss:V`):

- **Start: epoch 0 = 977.76** (`ln_train_h200_12124078.out:76`).
- **Best: epoch 48 = 49.913** (`ln_train_h200_12151181.out:907`) — the global minimum (next-lowest epoch 57 = 60.78). Reduction = (977.76−49.91)/977.76 = **94.9% ≈ 95%** ✓.
- Logged through **epoch 63** (val_loss 106.37, last line `…12151181.out:1490`).
- **Early stopping fired** — `12151181.err`: *"Monitored metric loss/val did not improve in the last 15 records. Best score: 49.913. Signaling Trainer to stop."* Best at ep48 + patience 15 ⇒ stop after ep63 ✓.
- **Best checkpoint exists:** `models/ln_finetuned/ln_finetuned_epoch=48.ckpt` (51.6 MB, `ls` confirmed). Saved checkpoints: epochs 02,03,04,08,25,48,55,57 (top-k by val_loss; **no epoch-63 ckpt** because 63 is not in the top-k).

**Convergence sampling metrics** (`12151181.out` end, "best_*" block):
`best_valid_ligand 0.970`, `best_connected_ligand 0.938`, `best_valid_complex 0.005` ✓
(overview: 0.97 / 0.94 / 0.005).

**Session chaining** (all three share `-J ln_train_h200`):

| Job | Wall window (from log) | Epochs | Resumed from | Ended by |
|---|---|---|---|---|
| 12124078 | Apr 17 17:54 → 18:23 (~29 min) | 0–9 | pretrained | **crash** — `.err` ends in molSimplify `IndexError: list index out of range` (`findMetal`) during sampling; saved ckpts 02–08 |
| 12138834 | Apr 17 21:55 → Apr 18 01:55 (4.0 h) | 9–29 | ep=08 | **TIME LIMIT** — `.err`: *"JOB 12138834 … CANCELLED … DUE TO TIME LIMIT"*; saved ckpt 25 |
| 12151181 | Apr 18 04:13 → 09:25 (~5.2 h) | 26–63 | ep=25 | **clean early-stop**; "Done: Apr 18 09:25:10"; saved ckpts 48,55,57 |

Sum ≈ 9.7 GPU-h ⇒ overview's "~10 GPU-hours" ✓.

**Five additional failed jobs (not in overview):** 12130545, 12131531, 12131768, 12133526 all died at startup with `ValueError: loaded state dict has a different number of parameter groups` (the discriminative-LR resume bug); 12136600 died with the same molSimplify `IndexError`. So the resume path **did not work cleanly at first** — see Discrepancy #4.

**Training-set size (indirect):** logs show `335/335` steps/epoch; all `finetune_*.sbatch` pass `--batch_size 256` ⇒ 335×256 = **85,760 ≈ "~85,000 samples"** ✓.

---

## 3. Generation / RePaint sweep

Authoritative numbers come from the **sweep job logs** (the generator prints
`Totally N valid complexes …` and a `--- r=X done: N valid / M attempted ---` line).
Directory `.xyz` counts (`find generated/<dir> -name '*.xyz' | wc -l`) corroborate.

| r | Source job | Log line | Attempts | Valid | Yield | Dir count |
|---|---|---|---|---|---|---|
| 1 | overnight_repaint **12329152** | "29 valid / 2500 attempted" | 2,500 | 29 | **1.16%** | 29 (`repaint_r1/noH`) ✓ |
| 5 | overnight_repaint **12329152** | "85 valid / 2500 attempted" | 2,500 | 85 | **3.40%** | 85 (`repaint_r5/noH`; +85 in `add_H` = 170) ✓ |
| 10 | finish_sweep **12340606** | "Totally 57 valid … repaint_r10" | 1,500 | **57** | **3.80%** | 57 (`repaint_r10/noH`) ✓ |
| 20 | finish_sweep **12340606** | "Totally 39 valid … repaint_r20" | 750 | 39 | **5.20%** | 39 (`repaint_r20/noH`) ✓ |

The overnight job (12329152) ran the smoke test + r=1 + r=5, then **started r=10 and was cut
off** (last line: "2500 samples will be generated", no result) — the 4 h wall. `finish_sweep`
(12340606) then ran r=10 (1,500) and r=20 (750) to completion ("All done: Apr 22 15:21:43").

**Denticity-match rate** (`metrics/results/aggregate_r*.txt`, "Exact match"):
r=1 **4/29 = 13.8%**, r=5 **13/85 = 15.3%**, r=10 **2/19 = 10.5%** ✓ (all match overview).
Note the r=10 aggregate analysed only **19** structures (the partial overnight r=10), not the
57 from the completed run — this is the origin of the overview's "19 valid" (Discrepancy #1).

**Where the overview's numbers came from:** r=1/r=5 valid counts and all three denticity
percentages trace cleanly to logs + `aggregate_r*.txt`. The overview's **r=10 row
(300 attempts / 19 valid / 6.33%) does NOT** — `grep -rniE "19 valid|300 attempt"` over all
`.out`/`.err` returns nothing. See Discrepancy #1.

**xTB convergence:** `xtb_results/mask1_baseline/summary.json` = 41 entries, 38 `xtb_success:true`
⇒ **38/41 = 92.7%** ✓. (`repaint_r5/summary.json` = 81/85.) The two `xtb_batch` jobs match:
12329159 reports 3 failures (2 IEEE + 1 xtb) on baseline, 12340608 reports 4 (2 IEEE + 2 xtb) on r=5.

**Phase-5 bond metrics** (`metrics/results/bond_classification.csv`, 38 rows):
n_ligands_raw = 5 in **9/38 (24%)**; = 3-or-4 in **29/38 (76%)** ✓; `added_cross_ligand ≥ 1`
in **23/38 = 60.5%** ✓. All three match the overview exactly.

---

## 4. Design test — VERIFIED ✓

| Run | Job | mask all | mask 3 | mask 2 | mask 1 |
|---|---|---|---|---|---|
| `design_test_runs/maskall_14344725/` | **14344725** | **0 valid / 6,300 attempts (0.00%)** | started, **0 valid** (`mask3/noH` empty) | — (not reached) | — |
| `design_test_runs/14292188/` | **14292188** | — | — | **4 valid** (`mask2/noH`) | **126** (`mask1/noH`) |

Evidence:
- `ln_maskall_14344725.out`: *"maskall  context=0/5  attempts=6300  valid=0  yield=0.00%"* (the per-line "150 sampling attempts" = 1 subset × 150 seeds; 6,300 = 150 seeds × 42 denticity partitions). Then *"MASK 3 … 1500 sampling attempts"* and the log ends — `.err`: *"JOB 14344725 … CANCELLED … DUE TO TIME LIMIT"* at 09:40. `mask3/noH` directory is empty ⇒ 0 valid. mask2 never reached.
- `ln_design_14292188.err`: *"JOB 14292188 … CANCELLED … DUE TO TIME LIMIT"* at 23:37 — explains mask1=126 / mask2=4 then cutoff.

**Dominant rejection reason — CONFIRMED:** `grep -c` on the `.err` logs →
`ln_design_14292188.err` = **151 of 170 lines** are *"Explicit valence for atom # N N, 4, is greater than permitted"*, **100% nitrogen** (`atom # … N, 4`); `ln_maskall_14344725.err` = 5/5 valence errors, all N. Matches the overview's mechanism claim exactly.

A first design attempt **14289937 failed at startup** — `.err`: *"/etc/bashrc: line 12:
BASHRCSOURCED: unbound variable"* (the `set -euo pipefail` + `source ~/.bashrc` bug the
overview's §13 warns about) — produced no output directory.

---

## 5. Completed sbatches

`-J` (job-name), `-p` (partition) read from each sbatch; outcomes from matching `<jobname>_<jobid>.out/.err`.

| sbatch | job id(s) | partition | outcome | key result |
|---|---|---|---|---|
| `finetune_h200/preempt/normal.sbatch` (all `-J ln_train_h200`) | 12124078 | mit_preemptable / mit_normal_gpu | **errored** (crash ep9, molSimplify) | saved ckpts 02–08 |
| ″ | 12130545, 12131531, 12131768, 12133526 | mit_preemptable | **errored at startup** | "different number of parameter groups" (resume bug) |
| ″ | 12136600 | mit_preemptable | **errored** | molSimplify `IndexError` |
| ″ | 12138834 | mit_preemptable | **timed out** (4 h) | epochs 9–29, ckpt 25 |
| ″ | 12151181 | mit_normal_gpu / preempt | **completed cleanly** (early-stop ep63) | **best val_loss 49.9 @ ep48** |
| `quicktest.sbatch` (`ln_quick`) | 12113735 | mit_quicktest | **completed** | setup smoke test |
| `gpu_test.sbatch` (`gpu_smoke`) | 14082659 | mit_preemptable | **completed** | "PASS: GPU is working" |
| `generate.sbatch` (`ln_gen`) | 12185735 | mit_preemptable | **timed out** | 31 combos/620 samples, cut off |
| `generate_clean.sbatch` (`ln_gen_clean`) | 12194449 | mit_preemptable | **incomplete** (no "Done") | 1550 samples, cut off |
| `generate_mask1.sbatch` (`ln_gen_m1`) | 12207365 | mit_preemptable | **completed** | 41 valid → `eu_tmma_mask1_epoch48` |
| `generate_minimal.sbatch` (`ln_gen_min`) | 12214531 | mit_preemptable | **completed** | 3 valid (minimal test) |
| `generate_big.sbatch` (`ln_gen_big`) | 12216914 | mit_preemptable | **completed** | 1 valid (big test) |
| `sbatches/overnight_repaint.sbatch` | 12329152 | mit_preemptable | **timed out** (4 h) | smoke + r=1 (29) + r=5 (85); r=10 cut off |
| `sbatches/finish_sweep.sbatch` | 12340606 | mit_preemptable | **completed** | r=10 (57/1500) + r=20 (39/750) |
| `sbatches/xtb_batch.sbatch` | 12329159 | mit_preemptable | **completed** | mask1_baseline xTB 38/41 |
| `sbatches/xtb_batch.sbatch` | 12340608 | mit_preemptable | **completed** | repaint_r5 xTB 81/85 |
| `xtb_opt.sbatch` (`xtb_opt`) | 12211401 | mit_preemptable | **completed** (w/ per-struct xtb failures) | early xTB opt test |
| `run_design_test.sbatch` (`ln_design`) | 14289937 | mit_preemptable | **errored at startup** | bashrc `nounset` bug, no output |
| `run_design_test.sbatch` (`ln_design`) | 14292188 | mit_preemptable | **timed out** (4 h) | mask1=126, mask2=4 |
| `run_design_maskall.sbatch` (`ln_maskall`) | 14344725 | mit_preemptable | **timed out** (4 h) | **maskall 0/6300**, mask3 0 |
| `sbatches/sweep_repaint.sbatch` | — | mit_preemptable | **no log / not run** | superseded by overnight+finish |
| `sbatches/context_ablation.sbatch` | — | mit_preemptable | **no log / not run** | (see Disc. #5) |
| `sbatches/dblock_cross.sbatch` | — | mit_preemptable | **no log / not run** | (see Disc. #5) |
| `sbatches/projection_stack.sbatch` | — | mit_preemptable | **no log / not run** | (see Disc. #5) |
| `sbatches/dft_orca.sbatch` | — | mit_normal | **no log / not run** | only ORCA template exists |

(Account is `mit_general` throughout; the three finetune variants can't be told apart by
output filename since they share `-J ln_train_h200`.)

---

## 6. Discrepancies & unverifiable claims

### Files disagree with PROJECT_OVERVIEW.md

1. **RePaint r=10 sweep (material).** Overview §7: *r=10 = 300 attempts, 19 valid,
   6.33% (5.5×), 10.5% denticity*. **Files:** the completed r=10 (`finish_sweep` 12340606)
   = **57 valid / 1,500 attempts = 3.80%**, and `generated/repaint_r10_epoch48/noH` holds
   exactly **57** xyz. The "19 valid" is the count of an **early/partial** r=10 analysed in
   `metrics/results/aggregate_r10.txt` ("Structures analysed: 19"); "300 attempts" and "6.33%"
   appear in **no log**. (The 10.5% denticity is correctly from those 19 structures.) The
   qualitative claims survive — yield still rises monotonically (1.16→3.40→3.80→5.20%) and
   denticity-match still peaks at r=5 — but the r=10 yield figure and "5.5×" are wrong.

2. **"133 total valid structures" (§7/§10/§13).** = 29+85+**19**, i.e. built on the partial
   r=10. Completed runs give 29+85+**57 = 171** (r1+r5+r10), or **210** including r=20.

3. **r=20 omitted.** `finish_sweep` completed **r=20 = 39 valid / 750 (5.20%)** (log + 39 xyz),
   but the overview's Phase-4 table lists only r=1/5/10.

4. **Training session characterization (§6).** "Three preemption-interrupted sessions …
   resumed cleanly" is imprecise: only **12138834** was time-limit-cancelled; **12124078**
   *crashed* (molSimplify), **12151181** *finished cleanly* via early-stop. And resume did
   **not** work cleanly at first — **five** unlisted jobs failed, four with
   "different number of parameter groups." (The "~10 GPU-h" total is fine.)

5. **The `paper/` artifacts are not backed by data (largest credibility issue) —
   but the overview does not rely on them.** `paper/executive_summary.md` and
   `paper/tables/table{1,2,3}*.csv` describe completed "Prompt 1–10" experiments that have
   **no job logs** and partly **contradict** real files:
   - **Context-density ablation** (table2: 31/15/9/6% valid) — no job output (`context_ablation.sbatch` never logged); CSV says *"Re-run analyze_context_ablation.py."*
   - **Cross-architecture** (table3: d-block vs Ln numbers) — the raw `cross_arch_summary.csv`
     has **every field empty, status "pending"** for all 4 rows; no `dblock_cross` log.
   - **Projection-stack / "6.4% valid"** (table1 row) — no `projection_stack` log.
   - **xTB "4/7 converge, 57%"** (exec summary) — **contradicts** the real xTB runs
     (38/41 = 92.7% baseline; 81/85 r=5). The 57% is table1's projection-row value.
   - **DFT "submitted, results pending"** — only `orca_templates/pbe0_eu.inp` exists; no
     `dft_work/`, no ORCA outputs, no submission log.
   - table1's own valid-rates (0.005/0.018/… on 500-sample runs) don't match the real
     log yields (0.0116/0.034 for r1/r5).
   These read as **templates / placeholder (likely synthetic) numbers**. Notably,
   `PROJECT_OVERVIEW.md` is the *more conservative* document — it lists projection,
   context-ablation, cross-conditioning, and DFT as **future work (§12)**, so it does not
   inherit these unsupported results.

### In the overview but not verifiable from this download

- **Phase-1 data-pipeline counts** — 53,333 CIFs → 31,979 mononuclear → 9,306 training
  complexes (6,563 O/N-only), 216,509 ligand instances, 54,946 unique SMILES, donor/CN/
  distance distributions. No source CIFs, no `prepare_training_data.py` output, no candidates
  CSV in the download — only the unreadable `train_ln.pt`/`val_ln.pt` tensors. **Unverifiable
  here.** (The derived "~85,000 training samples" *is* corroborated: 335 steps × batch 256.)
- **Architecture internals** — 5 layers / 192+32 features / ~3.8M params / T=500; the 7→11
  zero-pad and discriminative LRs. `finetune.py`'s docstring and flags (`--lr_head`,
  `--lr_backbone`, zero-pad description) confirm the *approach*; exact parameter counts were
  not checked (would require loading a checkpoint).
- **Visual-inspection / geometry claims** — Avogadro confirmation, "TMMA-shaped" fifth
  fragment, Eu–O 2.3–2.6 Å, "0% cross-bonds for the pristine reference." Inherently not
  log-verifiable; the one example xyz read is consistent with a real Eu coordination sphere,
  but distances were not measured. (`metrics/results/control/pristine_reference.json` exists
  but was not opened.)

---

## Confidence

**Solidly evidenced (logs + directory + metrics all agree):**
- Training: val_loss 977.76 → 49.91 @ ep48 (≈95%), early-stop @ ep63 (patience 15),
  best ckpt `epoch=48` present; sampling 0.970/0.938/0.005; batch 256 / ~85k samples.
- Sweep r=1 (29/2500) and r=5 (85/2500); completed r=10 (57/1500) and r=20 (39/750);
  denticity-match 13.8/15.3/10.5%.
- Design test: **maskall 0/6,300 (0.00%)**, mask3 0 valid, mask2 4, mask1 126; rejections
  overwhelmingly N-valence (151/170).
- xTB: baseline 38/41 (92.7%), r=5 81/85; bond metrics 24% / 76% / 60.5%.

**Partial / cut-off (true as far as it goes, but a run was interrupted):**
- `ln_gen_clean` (12194449) outcome inferred from absence of a "Done" line.
- mask3 "≥1,500 attempts": 1,500 *planned*; job cut off before logging — only the empty
  output dir proves 0 valid; exact attempts completed unknown.
- "~10 GPU-h": derived from start/Done timestamps (~9.7 h).
- Checkpoint **file mtimes** (Apr 18 02:28–17:16) do **not** align with the in-log run
  times — they look set at download/sync time, so they were **not** used for timeline
  reasoning (all timing came from timestamps printed inside the logs).

**Could not be checked from this download:**
- All Phase-1 CSD-pipeline counts (no source data or prep logs).
- The `paper/` table numbers (no raw data; `cross_arch_summary.csv` is empty/pending; the
  tables self-identify as regenerable templates).
- Exact model parameter counts / architecture internals; quantitative geometry of generated
  structures.

---

*Audit complete. No files were modified. The single most important numeric correction:
the completed RePaint r=10 run is **57 valid / 1,500 (3.80%)**, not the 19/300/6.33% in the
overview — and the headline "133 valid" should be 171 (or 210 with r=20). The single most
important credibility flag: the `paper/` "Prompts 1–10" artifacts (context-ablation,
cross-architecture, projection-stack, DFT) have no supporting job logs and partly contradict
the real xTB data, though PROJECT_OVERVIEW.md itself does not depend on them.*
