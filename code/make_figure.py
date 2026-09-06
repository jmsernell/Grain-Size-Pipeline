"""
make_figure.py -- build the quarry-scale grain-size figure from the batch summaries.

Reads results/per_slide_grainsize.csv (per-slide medians and Wentworth fractions) and
results/batch_log.csv (for the capture-resolution group of each slide), and writes the
two-panel figure: (a) per-slide median grain size by sample unit, (b) mean Wentworth
composition by unit.

Run from the repository root:   python code/make_figure.py
"""
import csv, re
import numpy as np
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

PER_SLIDE = "results/per_slide_grainsize.csv"
BATCH_LOG = "results/batch_log.csv"
OUT       = "figures/Fig_production_grainsize.png"

def stem(fn):
    s = fn.split(".")[0]
    for suf in ("_cp_masks", "_masks", "_2271", "_seg"): s = s.replace(suf, "")
    return s
def unit(fn): return re.sub(r"\d+$", "", stem(fn).split("-")[0])

def main():
    G = list(csv.DictReader(open(PER_SLIDE, newline="", encoding="utf-8-sig")))
    res = {stem(d["filename"]): float(d["native_um_px"])
           for d in csv.DictReader(open(BATCH_LOG, newline="", encoding="utf-8-sig"))}
    isA = lambda fn: abs(res.get(stem(fn), 2.271) - 2.271) < 0.01

    U = defaultdict(list)
    for d in G: U[unit(d["filename"])].append(d)
    A = [u for u in sorted(U) if isA(U[u][0]["filename"])]
    B = [u for u in sorted(U) if not isA(U[u][0]["filename"])]
    order = A + B

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    data = [[float(x["median_ecd_count_mm"]) for x in U[u]] for u in order]
    bp = ax1.boxplot(data, patch_artist=True, widths=0.6, medianprops=dict(color="black"))
    for i, box in enumerate(bp["boxes"]):
        box.set_facecolor("#3b5b8c" if order[i] in A else "#a83e3e"); box.set_alpha(0.75)
    ax1.axhline(0.0625, ls="--", c="gray", lw=0.8); ax1.axhline(0.125, ls="--", c="gray", lw=0.8)
    ax1.set_xticks(range(1, len(order)+1)); ax1.set_xticklabels(order, rotation=45, ha="right", fontsize=8)
    ax1.set_ylabel("Per-slide median grain size, ECD (mm)"); ax1.set_title("(a) Grain size by sample unit", fontsize=10)
    ax1.legend(handles=[Patch(fc="#3b5b8c", alpha=.75, label="Group A (2.271 um/px)"),
                        Patch(fc="#a83e3e", alpha=.75, label="Group B (2.73 um/px)")], fontsize=7, loc="upper right")

    classes = ["count_Medplus_pct", "count_Fine_pct", "count_VFine_pct", "count_Silt_pct"]
    labels  = ["Medium+", "Fine", "Very fine", "Silt"]
    cols    = ["#4a4a4a", "#8a8a8a", "#c2a35a", "#c47b3a"]
    comp = np.array([[np.mean([float(x[c]) for x in U[u]]) for c in classes] for u in order])
    bottom = np.zeros(len(order))
    for j, lab in enumerate(labels):
        ax2.bar(range(len(order)), comp[:, j], bottom=bottom, label=lab, color=cols[j], width=0.7)
        bottom += comp[:, j]
    ax2.set_xticks(range(len(order))); ax2.set_xticklabels(order, rotation=45, ha="right", fontsize=8)
    ax2.set_ylabel("Mean Wentworth composition by count (%)"); ax2.set_ylim(0, 100)
    ax2.set_title("(b) Textural composition by sample unit", fontsize=10)
    ax2.legend(fontsize=7, loc="upper right", ncol=2)
    plt.tight_layout(); plt.savefig(OUT, dpi=200, bbox_inches="tight")
    print("wrote", OUT)

if __name__ == "__main__":
    main()
