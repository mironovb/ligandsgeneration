# Project update to Prof. Jiang — data-curation phase

*Internal record of the progress update sent to Prof. De-en Jiang at the start of the
project (the CSD/CIF data-curation phase, before model adaptation and training). The
personal/funding paragraph from the original message is intentionally omitted here. The
analysis report referenced is `site/assets/data/cif_analysis_report.txt`; the per-element
breakdown is `site/assets/data/summary_by_element.csv`.*

---

Dear Prof. Jiang,

I have some progress to share on the lanthanide ligand generation.

I recently received ~53,000 CIF from Shicheng. Since I don't have access to the CSD
Python API (which requires a license), I wrote my own analysis pipeline using pymatgen
and ASE to parse these files. The script identifies donor atoms, decomposes each complex
into individual ligands, and extracts SMILES. I ran the full analysis on my university
cluster.

I checked my results against both of your group's CSD papers, and the overall trends are
consistent:

- Parsed 53,333 of the 53,360 CIF files (the ICC 2025 paper reports 53,370 total Ln
  complexes in CSD v5.46)
- Identified 31,979 mononuclear complexes (vs. 29,891 in the ICC 2025 paper — the
  difference likely comes from using distance-based bond detection rather than CSD API
  coordinate-bond annotations)
- Donor distribution: 65% O, 18% N, 14% C — consistent with the Sci. Rep. 2024 paper
  where O donors dominate across the series
- Average Ln–donor distance decreases from 2.61 Å (La) to 2.43 Å (Lu), matching the
  lanthanide contraction trend reported in both papers (2.62 to 2.41 Å)
- CN distribution peaks at CN=8 (9,658 structures) followed by CN=9 (6,529), consistent
  with the Sci. Rep. finding that CN=8 becomes most popular starting from Sm
- Water (8.0% of ligand instances) and nitrate (3.7%) are the most common inorganic
  ligands, in line with the ICC 2025 analysis

From this dataset, I preliminarily identified 9,306 structures that are suitable for
training a generative model — mononuclear, CN between 7 and 10, with only elements
multi-LigandDiff can handle. Of those, 6,563 have exclusively O/N donors. With ligand
masking augmentation, this gives about 212,000 training samples.

I also extracted a full ligand inventory: 216,509 coordinating ligand instances, with
54,946 unique SMILES. The extractant-relevant chemistries (amides, beta-diketones,
phosphine oxides, phenanthroline derivatives) are all present in the dataset.

I am now working on adapting multi-LigandDiff to generate ligands for Ln centers. The
main changes are adding La–Lu to the element set and expanding the coordination-number
handling from CN=6 to CN=7–10. After going through the codebase, it looks like the
equivariant layers themselves do not consider the coordination number, so only the input
embedding dimensions need to change. I plan to fine-tune from the pretrained
transition-metal checkpoint on the Ln training set.

I attached the analysis report. Let me know if you have any questions or suggestions on
what to prioritize.

Thank you and best regards,
Bogdan
