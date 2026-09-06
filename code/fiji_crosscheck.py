"""
fiji_crosscheck.py -- confirm Fiji/MorphoLibJ and Python measure the same mask identically.

Reads a MorphoLibJ "Analyze Regions" CSV (needs 'Label' and 'Area' columns, in pixels,
image uncalibrated) and the SAME label mask measured in Python, and checks that the two
tools return the identical object set and per-grain areas.

Edit the settings, then run:   python fiji_crosscheck.py
"""
import csv
import numpy as np
from PIL import Image
from skimage.measure import regionprops

# ---------------- settings ----------------
FIJI_CSV   = r"path\to\BVLX_fiji_regions.csv"          # <-- edit
MASK_PATH  = r"path\to\BVLX-01-1_2271_cp_masks.png"    # <-- edit (same mask Fiji measured)
# -------------------------------------------

def main():
    fiji = {}
    with open(FIJI_CSV, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        # tolerate different label/area header names
        lab_key  = next(k for k in r.fieldnames if k.strip().lower() in ("label", ""))
        area_key = next(k for k in r.fieldnames if k.strip().lower() == "area")
        for d in r:
            try: fiji[int(float(d[lab_key]))] = float(d[area_key])
            except Exception: pass
    a = np.array(Image.open(MASK_PATH)); a = a[..., 0] if a.ndim == 3 else a
    py = {p.label: float(p.area) for p in regionprops(a.astype(np.int32))}

    common = set(fiji) & set(py)
    diffs = np.array([abs(fiji[l] - py[l]) for l in common])
    print(f"objects: Fiji {len(fiji)}, Python {len(py)}, shared {len(common)}")
    print(f"per-grain area |Fiji-Python|: max={diffs.max():.1f}, "
          f"exact matches={int((diffs==0).sum())}/{len(diffs)}")

if __name__ == "__main__":
    main()
