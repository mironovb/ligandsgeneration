---
layout: default
title: Conclusions
nav_order: 7
---

# Conclusions & next steps
{: .no_toc }

{% include status.html %}

## Current conclusion

**In its current form the model is a completion tool, not a designer.** It reliably
regenerates a single missing ligand when the rest of the complex is present — mask 1
completion gives **126 valid** Eu(TMMA)₂(NO₃)₃ structures, xTB-stable at **38/41
(92.7%)** — but it **cannot compose a valence-correct coordination sphere from the metal
alone** (de-novo: **0 valid / 6,300**).

The failure is **chemical, not merely geometric**: the rejections are overwhelmingly
nitrogen placed in impossible 4-bond environments (~100% of logged rejections), and
validity sets in to zero as soon as the scaffold is reduced to two context ligands
(126 → 4 → 0 → 0 for mask 1/2/3/all). The inpainting objective, as trained, teaches
**local consistency** but not **global composition**.

This is a clean, defensible **negative result with a mechanistic explanation**, and it
directly motivates the architectural question at the center of the
[Strategy](strategy.html): whether multi-LigandDiff can be pushed to true design, or
whether a coordination-aware architecture is needed.

A secondary, methodological conclusion: **automated graph metrics over-flagged
"failures."** The fragment-count and xTB cross-bond rates (76% / 60.5%) were artifacts of
a bond-detection cutoff; visual inspection was necessary to get the story right (see the
[metric caveat](results.html#the-metric-caveat)). Always corroborate automated metrics
with direct inspection.

## Next steps (prioritized)

1. **Complete the degradation curve.** Run a dedicated **mask 2** experiment (3 of 5
   hidden) to locate exactly where between mask 1 (works) and mask 3 (0%) the cliff falls.
   Cheap, and it sharpens the result for the paper. *(The current mask 2 = 4 is only the
   handful that survived before a time-limit cutoff.)*
2. **Training-data augmentation toward harder masks.** Few of the up-to-20 mask configs per
   complex hide *most* ligands; increasing the fraction of high-mask-count examples directly
   targets the deficiency.
3. **Cross-class conditioning.** Test whether the model follows context toward a different
   donor class (phosphine oxide, Schiff base) or reverts to the dominant amide/nitrate
   training prior.
4. **Hard geometric projection during sampling** (Christopher 2024, *already implemented in
   the repo*). Projects generated atoms out of an exclusion shell around context atoms;
   targets the "placed slightly too close" tendency behind the cross-bond artifact.
5. **Architecture decision.** If (2)–(4) do not enable de-novo generation, consider
   alternatives — flow-matching, or autoregressive composition — better suited to building
   structure without a scaffold. This is the fork into [Track B](strategy.html#track-b-next--a-coordination-aware-rare-earth-native-platform).
6. **Validation-pipeline upgrade.** Once a candidate set is trusted, tighten the xTB
   protocol (frozen context, `--alpb dodecane`, `--opt tight`) and run **DFT validation**
   (PBE0-D3/def2-TZVP, Stuttgart ECP28MWB on Eu, SMD dodecane; ORCA templates prepared) on
   the top candidates.

{: .unverified }
> **No DFT has been run.** Only `orca_templates/pbe0_eu.inp` exists in the repo — no ORCA
> outputs, no `dft_work/`, no submission log. DFT validation is a *next step*, not a
> completed result.

See the [Strategy](strategy.html) page for how these steps split into the publish-now
(Track A) and build-next (Track B) roadmap.
