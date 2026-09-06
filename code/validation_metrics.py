"""
validation_metrics.py -- compare a PREDICTION mask to a GROUND-TRUTH mask.

Reproduces the validation numbers in the paper: precision/recall/F1 across
IoU thresholds (greedy one-to-one matching), recall broken out by Wentworth
class, panoptic quality, and the Wasserstein + KS distance between the two
grain-size distributions (with a bootstrap CI on the Wasserstein distance).

Edit the settings, then run:   python validation_metrics.py
"""
import numpy as np
from PIL import Image
from scipy.stats import wasserstein_distance, ks_2samp
from skimage.measure import regionprops

# ---------------- settings ----------------
GT_PATH        = r"path\to\ground_truth_masks.png"     # <-- edit
PRED_PATH      = r"path\to\prediction_cp_masks.png"    # <-- edit
GT_SCALE       = 2.271     # microns/pixel of the GT mask
PRED_SCALE     = 2.271     # microns/pixel of the prediction mask
SOLIDITY_MIN   = 0.80      # applied to the GT (real-grain filter)
# -------------------------------------------

def load(p):
    a = np.array(Image.open(p))
    if a.ndim == 3: a = a[..., 0]
    return a.astype(np.int32)

def solidity_filter(lab, thr):
    keep = [p.label for p in regionprops(lab) if p.solidity >= thr]
    return np.where(np.isin(lab, keep), lab, 0)

def ecd_mm(lab, scale):
    c = np.bincount(lab.ravel()); ids = np.nonzero(c)[0]; ids = ids[ids != 0]
    return 2*np.sqrt(c[ids]*(scale*1e-3)**2/np.pi)

def wentworth(e):
    return "Silt" if e < 0.0625 else "Very fine" if e < 0.125 else "Fine" if e < 0.25 else "Medium+"

def greedy_match(gt, pred, thr):
    """Greedy one-to-one match by descending IoU. Returns TP set (GT labels) and counts."""
    Pmax = pred.max(); m = (gt > 0) & (pred > 0)
    lin = gt[m].astype(np.int64)*(Pmax+1) + pred[m].astype(np.int64)
    inter = np.bincount(lin); ga = np.bincount(gt.ravel()); pa = np.bincount(pred.ravel())
    pairs = []
    for lp in np.nonzero(inter)[0]:
        gi, pi = lp//(Pmax+1), lp%(Pmax+1)
        I = inter[lp]; U = ga[gi] + pa[pi] - I
        pairs.append((I/U, gi, pi))
    pairs.sort(reverse=True)
    ug, up, tp = set(), set(), []
    for iou, gi, pi in pairs:
        if iou < thr: break
        if gi in ug or pi in up: continue
        ug.add(gi); up.add(pi); tp.append((gi, iou))
    nG = int((np.unique(gt) != 0).sum()); nP = int((np.unique(pred) != 0).sum())
    return tp, nG, nP

def prf(tp, nG, nP):
    TP = len(tp); prec = TP/nP if nP else 0; rec = TP/nG if nG else 0
    f1 = 2*prec*rec/(prec+rec) if prec+rec else 0
    return prec, rec, f1, TP

def main():
    gt   = solidity_filter(load(GT_PATH), SOLIDITY_MIN)
    pred = load(PRED_PATH)
    # put prediction on the GT grid if sizes differ (evaluate at one resolution)
    if pred.shape != gt.shape:
        pred = np.array(Image.fromarray(pred.astype(np.uint16)).resize(
            (gt.shape[1], gt.shape[0]), Image.NEAREST)).astype(np.int32)

    print("== detection (greedy 1-to-1 IoU match) ==")
    f1s = []
    for thr in (0.5, 0.6, 0.7, 0.8, 0.9):
        tp, nG, nP = greedy_match(gt, pred, thr)
        prec, rec, f1, TP = prf(tp, nG, nP)
        f1s.append(f1)
        if thr in (0.5, 0.7):
            print(f"  IoU>={thr}:  P={prec:.3f}  R={rec:.3f}  F1={f1:.3f}  (TP={TP}, GT={nG}, pred={nP})")
    print(f"  F1 across IoU 0.5-0.9: {[round(x,3) for x in f1s]}")

    # panoptic quality (IoU>0.5 matches)
    tp, nG, nP = greedy_match(gt, pred, 0.5)
    TP = len(tp); FP = nP-TP; FN = nG-TP
    SQ = np.mean([i for _, i in tp]) if tp else 0
    RQ = TP/(TP + 0.5*FP + 0.5*FN)
    print(f"  panoptic quality PQ={SQ*RQ:.3f}  (SQ={SQ:.3f}, RQ={RQ:.3f})")

    # recall by Wentworth class
    matched = {gi for gi, _ in tp}
    c = np.bincount(gt.ravel()); ids = np.nonzero(c)[0]; ids = ids[ids != 0]
    by = {k: [0, 0] for k in ["Medium+", "Fine", "Very fine", "Silt"]}
    for i in ids:
        k = wentworth(2*np.sqrt(c[i]*(GT_SCALE*1e-3)**2/np.pi))
        by[k][1] += 1
        if i in matched: by[k][0] += 1
    print("== recall by Wentworth class (IoU>=0.5) ==")
    for k in ["Medium+", "Fine", "Very fine", "Silt"]:
        m, t = by[k]
        print(f"  {k:10s} {m}/{t} = {100*m/t:.0f}%" if t else f"  {k}: n/a")

    # distribution distance
    ge = ecd_mm(gt, GT_SCALE); pe = ecd_mm(pred, PRED_SCALE)
    W = wasserstein_distance(pe, ge); ks = ks_2samp(pe, ge)
    rng = np.random.default_rng(0)
    boot = [wasserstein_distance(rng.choice(pe, len(pe), True), rng.choice(ge, len(ge), True))
            for _ in range(2000)]
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print("== grain-size distribution (prediction vs ground truth) ==")
    print(f"  median ECD: GT {np.median(ge):.4f} mm  vs  pred {np.median(pe):.4f} mm")
    print(f"  Wasserstein: {W*1000:.1f} um  (95% bootstrap CI {lo*1000:.1f}-{hi*1000:.1f} um)")
    print(f"  KS: D={ks.statistic:.3f}, p={ks.pvalue:.3g}")

if __name__ == "__main__":
    main()
