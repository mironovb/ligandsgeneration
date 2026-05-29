---
layout: default
title: Home
nav_order: 1
description: "A conditional 3D generative model for lanthanide ligand design — objective, vision, and status at a glance."
permalink: /
---

# Lanthanide Ligand Generation
{: .no_toc }

{% include status.html %}

## The objective

Separating individual rare-earth elements from one another is a major industrial and
strategic challenge, and the chemistry that drives the selectivity lives in the
**ligand** — the organic molecule that wraps around the metal ion. This project builds a
**conditional 3D generative model** that proposes new ligand structures for a specified
**lanthanide (Ln) coordination environment**, as a tool for rare-earth separations.

Concretely, we adapt **multi-LigandDiff** — a 3D equivariant diffusion model originally
built for d-block transition-metal complexes — to the f-block, and to the high
coordination numbers (CN 7–10) that lanthanides prefer.

## The vision

> Train a model on the tens of thousands of known Ln complexes in the Cambridge
> Structural Database (CSD), then ask it to generate ligands meeting a target
> specification — for example *"generate ligands with 2 N donors and 3 O donors, neutral
> charge"* — producing a pool of candidates that can be screened computationally and
> ultimately synthesized.
>
> — Prof. De-en Jiang (Vanderbilt), project framing

The arc is **generate → screen → synthesize**. This site tracks how far along that arc
the current model reaches, and exactly where it stops.

## Status at a glance

<div style="display:flex; flex-wrap:wrap; gap:0.75rem; margin:1rem 0 1.5rem;">
  <div style="flex:1 1 220px; border:1px solid #e2e8f0; border-left:4px solid #16a34a; border-radius:6px; padding:0.7em 0.9em; background:#f8fafc;">
    <div style="font-size:0.8em; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">Dataset</div>
    <div style="font-weight:700; color:#16a34a; font-size:1.05em;">✓ curated</div>
    <div style="margin-top:0.35em; font-size:0.92em;"><strong>9,306</strong> training complexes from 53,333 CIFs; trends match the Jiang CSD papers.</div>
  </div>
  <div style="flex:1 1 220px; border:1px solid #e2e8f0; border-left:4px solid #16a34a; border-radius:6px; padding:0.7em 0.9em; background:#f8fafc;">
    <div style="font-size:0.8em; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">Trained model</div>
    <div style="font-weight:700; color:#16a34a; font-size:1.05em;">✓ converged</div>
    <div style="margin-top:0.35em; font-size:0.92em;">Validation loss <strong>977.8 → 49.9</strong> (~95% ↓), best at epoch 48, clean early-stop.</div>
  </div>
  <div style="flex:1 1 220px; border:1px solid #e2e8f0; border-left:4px solid #16a34a; border-radius:6px; padding:0.7em 0.9em; background:#f8fafc;">
    <div style="font-size:0.8em; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">RePaint sweep</div>
    <div style="font-weight:700; color:#16a34a; font-size:1.05em;">✓ done</div>
    <div style="margin-top:0.35em; font-size:0.92em;">Yield <strong>1.16% → 5.20%</strong> across r = 1 → 20; <strong>r = 5</strong> is the working point.</div>
  </div>
  <div style="flex:1 1 220px; border:1px solid #e2e8f0; border-left:4px solid #16a34a; border-radius:6px; padding:0.7em 0.9em; background:#f8fafc;">
    <div style="font-size:0.8em; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">Completion (mask 1)</div>
    <div style="font-weight:700; color:#16a34a; font-size:1.05em;">✓ works</div>
    <div style="margin-top:0.35em; font-size:0.92em;"><strong>126 valid</strong> structures; xTB-stable <strong>38/41 (92.7%)</strong>.</div>
  </div>
  <div style="flex:1 1 220px; border:1px solid #e2e8f0; border-left:4px solid #dc2626; border-radius:6px; padding:0.7em 0.9em; background:#fef2f2;">
    <div style="font-size:0.8em; text-transform:uppercase; letter-spacing:0.04em; color:#64748b;">De-novo design</div>
    <div style="font-weight:700; color:#dc2626; font-size:1.05em;">diagnostic</div>
    <div style="margin-top:0.35em; font-size:0.92em;"><strong>0 valid / 6,300</strong> attempts from a bare Eu center.</div>
  </div>
</div>

**The one-sentence story:** from a curated, CSD-validated lanthanide dataset (9,306
complexes), a transition-metal diffusion model fine-tunes cleanly to the f-block and
**reliably completes** lanthanide coordination spheres (xTB-stable) while RePaint tunes
yield — and a **sharp diagnostic** shows it cannot *yet* design a sphere from the bare metal
(0 / 6,300), a specific, fixable valence-composition gap that points to a coordination-aware
platform.

All numbers above are traceable to on-cluster job logs and metrics files; see
[Results](results.html) for the per-experiment provenance and [Experiment
Log](experiment-log.html) for the full run table.

## Navigating this tracker

| Page | What's there |
|---|---|
| [Background](background.html) | Why Ln separations matter, the objective, and the key papers (incl. the three Kulik papers). |
| [Dataset](dataset.html) | The lanthanide CSD curation: 53k CIFs → 9,306 training complexes, validated against the Jiang group's CSD papers; per-element table + downloads. |
| [Methods](methods.html) | The multi-LigandDiff architecture, the lanthanide adaptation, the data pipeline, and the training setup. |
| [Results](results.html) | Training curve, RePaint sweep, the metric caveat, and the de-novo design test. |
| [Code Review](code-review.html) | Code-level reading of the repo: where the validity/sampling pipeline can be wrong (the nitrate-rejecting checker, the inflated 6,300 denominator) and the cheapest fixes toward a positive de-novo result. |
| [Experiment Log](experiment-log.html) | Every sbatch run: job id, partition, outcome, key result — the living tracker. |
| [Strategy](strategy.html) | The two-track roadmap (publish the finding now; build a coordination-aware platform next). |
| [Conclusions](conclusions.html) | The current conclusion and prioritized next steps. |
| [Changelog](changelog.html) | Dated log of changes to this tracker. |
