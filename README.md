Accessible automated grain-size analysis of sandstone thin sections
Code, fine-tuned model, and data supporting the manuscript submitted to Computers &
Geosciences. C&G requires a public repository at submission and a DOI-archived version for
acceptance; this repository is built to satisfy that.
We lightly fine-tune a free, off-the-shelf instance-segmentation model (Cellpose, cpsam / a
Segment-Anything backbone) on one or two hand-labeled slides, run it on ordinary single
thin-section images, and validate the result at the level of the grain-size distribution.
Authors
Dr. J. Matthew Sernell and Dr. Chris Coughenour
Department of Geoscience and the Environment, University of Pittsburgh at Johnstown
What's here (and why it's enough)
Every accuracy claim in the paper rests on three fully delineated slides, so those three —
image, ground truth, and prediction — are included in full. The other 161 production slides
appear only as the aggregate quarry-scale result, which is captured completely by the two
summary tables in `results/`. So this repository reproduces every validated number without
shipping 164 raw images.
```
code/        pipeline scripts
model/       pointer to the weights (hosted on Zenodo, >1 GB — see model/README.txt)
data/
  images/                 clean RGB thin-section images (+ representative/ : one per unit)
  masks_ground_truth/     hand-traced label masks (BVLX, LLCR) + seg files; RGLL note
  masks_predicted/        Cellpose predictions for the three validation slides
  delineations/           cyan-outline overlays used to build/recover ground truth
  cross_check/            Fiji/MorphoLibJ export (independent measurement check)
results/     batch_log.csv and per_slide_grainsize.csv  (the full 164-slide result)
figures/     production grain-size figure
```
The three validation slides
Slide	Role	Scale (um/px)	Ground truth
BVLX-01-1	training	2.271	retained hand mask (574 raw, 520 after solidity filter)
LLCR03-01-4	training	2.271	retained hand mask (667 raw, 614 after filter)
RGLL03-01-1	held-out	1.534 native / 2.271 inference	reconstructed from the retained delineation (473; recorded 470) — see the note in masks_ground_truth/
Reproducing the results
`code/batch_infer.py` — run the model over `data/images/` to produce `*_cp_masks.png`.
`code/grainsize.py` — measure a mask: ECD, Wentworth by count and by area (solidity >= 0.80).
`code/batch_grainsize.py` — per-slide summary across a folder (produces per_slide_grainsize.csv).
`code/recon_masks.py` — rebuild the RGLL ground truth from its delineation overlay.
`code/validate.py` — determinism check (SHA-256 of mask arrays across repeated runs).
`figures/Fig_production_grainsize.png` is generated from `results/per_slide_grainsize.csv`.
Model weights (on Zenodo)
The fine-tuned model (Training2Samples, ~1 GB) is too large for GitHub and is archived on
Zenodo (https://doi.org/10.5281/zenodo.22544499); download it and place it in `model/` (see `model/README.txt`). The Zenodo DOI is the
citable, archival reference and is what Computers & Geosciences requires. Cite both the
GitHub URL and the Zenodo DOI in the paper's Computer Code Availability section.
Full image set
The complete 164-image set is not required to reproduce the paper and is not stored on GitHub.
Include it in the Zenodo record if you want it public, or provide it from the corresponding
author on request. The two CSVs in `results/` already capture the full 164-slide result.
Environment
See `requirements.txt`. Built and run on Python 3.10.20, Cellpose 4.1.1, PyTorch 2.7.1
(CUDA 11.8), on a consumer GPU (NVIDIA GTX 1650, 4 GB); a CPU-only setup also works, slower.
Citation and license
Add the paper citation and the Zenodo DOI in `CITATION.cff`. Licensed under MIT (`LICENSE`).
