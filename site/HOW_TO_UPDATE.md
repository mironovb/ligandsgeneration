# How to update this tracker

This site is a **living tracker**: it is meant to be edited as new runs finish. Almost
every update is one of the three below — each is copy-paste. The golden rule, inherited
from `VERIFICATION_REPORT.md`:

> **Every number gets a source tag** (a job id, a `.out`/`.err` log line, or a metrics
> file). If a number is not log-verified, mark it *unverified* — never present it as a
> settled fact.

To preview any change locally, see [§4 Rebuild & serve](#4-rebuild--serve).

---

## 1. Add a finished run

A new sbatch completed → add **one row** to `_data/experiments.yml`. It appears
automatically in the right table on the **Experiment Log** page (tables are grouped by the
`phase` field; the row's color comes from `status`).

**Steps**

1. Open `_data/experiments.yml`.
2. Copy the block below into the section matching its `phase` (setup / training /
   generation / xtb / sweep / design).
3. Fill **every** field from the job's `.out`/`.err` log. Leave `date` and `gpu_hours`
   **empty (`""`)** unless the log actually prints them — do not guess.
4. Put the headline number in `key_result`, and cite where it came from in `notes`.

```yaml
- job_id: "JOBID"                 # SLURM id(s); space-separate if several share one outcome
  sbatch: "path/to/script.sbatch" # the submission script
  job_name: "ln_xxx"              # SLURM -J name, or "" if not recorded
  partition: "preemptable"    # SLURM -p
  date: ""                        # "YYYY-MM-DD" only if the log prints it, else ""
  gpu_hours: ""                   # number only if a wall window / 4 h cap is logged, else ""
  phase: "generation"             # setup | training | generation | xtb | sweep | design | not-run
  status: "completed"             # completed-clean | completed | timed-out | errored | incomplete | not-run
  outcome: "One-line human-readable result"
  key_result: "the headline number / artifact"
  notes: "Source: <log file:line> or <metrics file>. Caveats here."
```

**Worked example** (an imagined new mask-2 run):

```yaml
- job_id: "14400001"
  sbatch: "run_design_mask2.sbatch"
  job_name: "ln_mask2"
  partition: "preemptable"
  date: "2026-06-01"
  gpu_hours: 4.0
  phase: "design"
  status: "completed"
  outcome: "Dedicated mask-2 run (3 of 5 ligands hidden) to completion"
  key_result: "mask2 = NN valid / MMMM"
  notes: "Source: ln_mask2_14400001.out:<line>. Replaces the partial mask2=4 from job 14292188."
```

Then do [§2](#2-bump-the-status-date--add-a-changelog-entry) and, if the number is quoted
in prose, [§3](#3-add-a-new-result-number-to-a-page).

---

## 2. Bump the status date & add a changelog entry

Do this on **every** meaningful update so "Status as of …" stays current.

**Step A — the status banner (one line).** Edit `_config.yml`:

```yaml
status_date: "2026-06-01"                       # <- the only place the date lives
status_summary: "One-sentence current state."   # <- optional: refresh if the headline changed
```

`_includes/status.html` reads these two fields, so the home page, Conclusions, and
Changelog all re-stamp automatically — **no other file to touch for the date.**

**Step B — a changelog entry (newest first).** Add to the top of the list in
`changelog.md`:

```markdown
- **2026-06-01** — <what changed>. <New verified numbers + their source>. Anything now
  *unverified → verified* (or corrected) noted explicitly.
```

---

## 3. Add a new result number to a page

When a number appears in **prose** (most often `results.md`), it needs a **source tag**.
The site convention is a Markdown footnote citing the job id / log line / metrics file.

**Pattern** (already used throughout `results.md`):

```markdown
The r=5 sampler reached a yield of **3.40%**.[^sweep]

[^sweep]: r=5 ("85 valid / 2500 attempted") from job `12329152`; dir count corroborates.
```

**Where numbers go**

| Kind of number | Put it on | How to tag |
|---|---|---|
| Per-run result (valid counts, yields, val_loss) | `results.md` | footnote → job id + `.out`/`.err` line |
| A whole new run's headline | `_data/experiments.yml` (see §1) | the `notes:` field |
| An at-a-glance status number | `index.md` status cards | no footnote — the cards defer to Results; keep the number identical to the sourced one there |
| A figure value | edit `assets/figures/make_figures.py`, then `make figures` | the script's header comment lists each value's source |

**If the number is NOT log-verified** (e.g. from `PROJECT_OVERVIEW.md` only, or a visual
inspection), do **not** present it as fact. Wrap it in an unverified callout:

```markdown
{: .unverified }
> <claim>. Reproduced from <source>; **not independently verified** here.
```

(Available callouts, defined in `_config.yml`: `.note` `.works` `.caveat` `.unverified`
`.fails`.)

**Never** reintroduce the superseded figures (19/300/6.33%, "5.5×", or "133"). The settled
values are r=10 = **57/1,500 = 3.80%** and total valid = **171** (210 incl. r = 20).

---

## 4. Rebuild & serve

A `Makefile` in this directory wraps the commands (it puts Homebrew Ruby on `PATH` for you,
since system Ruby 2.6.10 is too old):

```bash
cd site
make install     # first time only — installs gems into vendor/bundle
make serve       # build + live-reload at http://localhost:4000/
make build       # one-off static build into _site/
make figures     # regenerate the SVGs after editing make_figures.py
make clean        # wipe _site/ and caches
```

Prefer raw commands? They are:

```bash
export PATH="/usr/local/opt/ruby/bin:$PATH"   # Apple Silicon: /opt/homebrew/opt/ruby/bin
bundle exec jekyll serve --livereload          # or: bundle exec jekyll build
```

A clean build prints `done in …` with no `Warning`/`Error` lines. Deployment to GitHub
Pages is automatic on push to `main` via `.github/workflows/pages.yml` — see `README.md`.
