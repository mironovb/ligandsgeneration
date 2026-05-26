# Lanthanide Ligand Generation — site

A Jekyll ([just-the-docs](https://just-the-docs.com/)) site that tracks the project to
adapt multi-LigandDiff to lanthanide coordination complexes. This directory is
self-contained so it can be deployed independently of the model code.

## Ruby note (read first)

Build with a **modern Ruby**. The machine's system Ruby (2.6.10) is too old for the
current Jekyll toolchain and its native gems won't compile under the installed clang.
This repo was built with **Homebrew Ruby** — put it on your PATH first:

```bash
export PATH="/usr/local/opt/ruby/bin:$PATH"   # Homebrew (Intel) Ruby; matches GitHub Pages' Ruby 3.x+
ruby --version                                 # should NOT report 2.6.x
```

## Local development

```bash
cd site
bundle config set --local path 'vendor/bundle'   # first time only: keep gems local
bundle install
bundle exec jekyll serve                          # http://localhost:4000/
# or just build:
bundle exec jekyll build                          # output in _site/
```

## Deploying to GitHub Pages (via GitHub Actions)

just-the-docs isn't one of GitHub's built-in "classic Pages" themes, so the site is
built and deployed by `.github/workflows/pages.yml`.

> **In the `ligandsgeneration` repo, `site/` is a subfolder, not the repo root** — so the
> deploy is driven by the **repo-root** `.github/workflows/pages.yml` (configured for the
> `site/` working directory), and the standalone steps below do **not** apply. See the root
> `README.md`. The instructions below are for deploying this `site/` folder as its **own
> standalone repo**.

1. Push the **contents of this `site/` directory** to a GitHub repo (so `_config.yml`
   sits at the repo root). Keeping it as its own repo is the cleanest "deploy
   independently" path; the workflow file then lands at `.github/workflows/pages.yml`.
2. In the repo, go to **Settings → Pages → Build and deployment** and set
   **Source = GitHub Actions**.
3. Push to `main` (or run the workflow manually). The workflow builds with Ruby 3.3 and
   injects the correct `--baseurl` automatically — no need to hardcode `baseurl` in
   `_config.yml` for the deployed site.

> Prefer to keep the site in a `site/` subfolder of a larger repo? The workflow has
> inline notes showing the three lines to switch to a `site/` working directory.

## Updating the status banner

Edit `status_date` and `status_summary` in `_config.yml`; the home page, changelog, and
any page that includes `status.html` update automatically.

## Structured data

- `_data/experiments.yml` — one row per sbatch run (rendered on **Experiment Log**).
- `_data/papers.yml` — reference list incl. the three Kulik papers (rendered on **Background**).
