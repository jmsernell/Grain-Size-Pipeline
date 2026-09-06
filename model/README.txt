Model weights are hosted on Zenodo, not in this GitHub repository.

The fine-tuned model, "Training2Samples" (the two-slide cpsam model behind every
production and validation result in the paper), is about 1 GB — over GitHub's 100 MB
per-file limit. It lives in the Zenodo archive for this project instead:

    Zenodo DOI: 10.5281/zenodo.22544499

To run the pipeline:
  1. Download "Training2Samples" from the Zenodo record above.
  2. Put it here (model/Training2Samples) or in your Cellpose models directory
     (e.g. ~/.cellpose/models/), and point code/batch_infer.py at it.

Why Zenodo: it hosts large research artifacts and mints the citable DOI that
Computers & Geosciences requires. GitHub holds the code and validation data; Zenodo
holds the model weights (and, optionally, the full 164-image set). The paper's
Computer Code Availability section cites both the GitHub URL and the Zenodo DOI.
