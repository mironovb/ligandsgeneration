---
layout: default
title: Background
nav_order: 2
---

# Background, objective & key papers
{: .no_toc }

<details open markdown="block">
  <summary>On this page</summary>
{: .text-delta }
- TOC
{:toc}
</details>

## Why lanthanide separations matter

The lanthanides (La–Lu) are the bulk of the "rare earths," and they are essential to
magnets, phosphors, catalysts, and batteries. The hard problem is **separating the
individual elements from one another**: chemically they are extremely similar — all
favor the +3 oxidation state, and their ionic radii change only smoothly across the
series (the *lanthanide contraction*). Industrial separation relies on solvent
extraction with organic **ligands** that bind one lanthanide slightly more tightly than
its neighbors. Designing those ligands is slow, expensive, and largely driven by chemical
intuition.

The chemistry that produces selectivity lives in the ligand — its donor atoms, its
denticity, and how it fits the contracting Ln³⁺ ion. If we could *generate* candidate
ligands to a target coordination specification, we could enlarge the design space well
beyond what intuition reaches.

## The objective

Build a **conditional 3D generative model** that proposes ligand structures for a
specified lanthanide coordination environment, as a tool for rare-earth separations. The
long-term workflow is **generate → screen → synthesize**: generate to a donor/charge
specification, screen the candidates computationally (xTB, then DFT), and synthesize the
best.

This project takes a concrete first step: adapt the **multi-LigandDiff** diffusion model
(built for d-block transition metals, coordination number ≤ 6) to the **f-block** and to
the **high coordination numbers (CN 7–10)** lanthanides prefer — a regime no prior model,
including the Kulik coordination-prediction tools, has covered.

A first deliverable already exists independently of the model: a curated
**[lanthanide CSD dataset](dataset.html)** of 9,306 training-ready complexes, built with a
license-free pymatgen/ASE pipeline and **validated against the Jiang group's own published
CSD analyses** (donor distributions, the lanthanide contraction, the CN = 8 peak all
reproduce). It is the foundation everything below is trained on.

## The reference complex

Every generation experiment in this project uses one well-characterized complex as its
test bed: **Eu(TMMA)₂(NO₃)₃** (Kravchuk et al., EurJIC 2024; CCDC VEDTAA01). TMMA
(*N,N,N′,N′-tetramethylmalonamide*) is a diamide chemically adjacent to the
diglycolamide-type extractants used in real separations. The complex is a europium center
with 2 TMMA ligands (each bidentate through two carbonyl O) and 3 nitrate ligands (each
bidentate) — **5 ligands, coordination number 10, 35 heavy atoms**, in a *cis*
configuration.

## Key papers

The list below renders from `_data/papers.yml`, grouped by role. DOIs/links are shown
where the source documents provide them.

{% assign groups = "background,reference,method,kulik" | split: "," %}
{% assign group_titles = "Application domain — rare-earth separations,The reference complex,Generative-modeling methods,Prof. Jiang's reading list — the three Kulik-group papers" | split: "," %}
{% for g in groups %}
### {{ group_titles[forloop.index0] }}
{: .no_toc }

{% for p in site.data.papers %}{% if p.group == g %}- **{{ p.title }}** — {{ p.authors }}{% if p.venue != "" %}. *{{ p.venue }}*{% endif %}{% if p.doi != "" %}. DOI: [{{ p.doi }}]({{ p.url }}){% elsif p.url != "" %}. [link]({{ p.url }}){% endif %}.{% if p.software != "" %} <br>↳ *Software / data:* {{ p.software }}{% endif %}{% if p.note != "" %} <br>↳ *Relevance:* {{ p.note }}{% endif %}
{% endif %}{% endfor %}
{% endfor %}

{: .note }
> The three Kulik-group papers are the heart of the forward strategy: all three
> *characterize, predict, or classify* metal–ligand coordination, but **none of them
> generate**. They locate the exact capability our generative model lacks — a learned
> model of what a *valid* coordination environment is. See [Strategy](strategy.html) for
> how they seed the next platform.
