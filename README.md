# Lanthanide Ligand Generation

Adapting **multi-LigandDiff** — a 3D equivariant diffusion model built for transition-metal
complexes — to **lanthanide coordination chemistry**, as a tool for rare-earth separations.
This repository hosts the project's living-documentation **site** and the analysis **reports**.

**Live site:** <https://mironovb.github.io/ligandsgeneration/>
_(published by GitHub Actions once Pages is enabled — see [Deployment](#deployment))_

## What's in here

| Path | Contents |
|---|---|
| `site/` | The Jekyll ([just-the-docs](https://just-the-docs.com/)) documentation site — background, methods, results, experiment log, strategy, conclusions. **This is what gets published to Pages.** |
| `PROJECT_OVERVIEW.md` | High-level overview of the project. |
| `LITERATURE_AND_STRATEGY.md` | Literature review and research strategy. |
| `SITE_AUDIT.md` | Audit of the site's claims for accuracy and provenance. |
| `VERIFICATION_REPORT.md` | Verification of reported metrics against on-cluster job logs. |
| `.github/workflows/pages.yml` | CI that builds `site/` and deploys it to GitHub Pages. |

Kept **out** of the repo on purpose (see [`.gitignore`](.gitignore)): `prompts/` (local
workflow prompts), `papers/` (reference PDFs), and `multi_LigandDiff/` (the ~1.1 GB model
code, which is its own repository).

## Develop the site locally

The toolchain needs a modern Ruby — the macOS system Ruby (2.6) is too old. The Makefiles
put Homebrew Ruby on `PATH` for you. From the repo root:

```bash
make install    # first time only: install gems into site/vendor/bundle
make serve      # build + serve with live reload at http://localhost:4000/
make build      # one-off build into site/_site/
make help       # list all targets
```

These proxy to [`site/Makefile`](site/Makefile); you can equivalently `cd site && make serve`.
See [`site/README.md`](site/README.md) for the full site-specific notes (status banner,
structured data files, figure regeneration).

## Deployment

Every push to `main` triggers [`.github/workflows/pages.yml`](.github/workflows/pages.yml),
which builds the `site/` subfolder with Jekyll and publishes it to GitHub Pages. The workflow
injects the correct `--baseurl` automatically, so no URL is hardcoded in `_config.yml`.

**One-time setup** (required before the first deploy): on GitHub, go to
**Settings → Pages → Build and deployment** and set **Source = "GitHub Actions"**. After
that, pushing to `main` (or running the workflow manually from the Actions tab) redeploys
the site.
