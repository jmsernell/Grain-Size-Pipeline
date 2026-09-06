"""
batch_grainsize.py  --  measures every mask and writes one summary CSV.
Nothing to edit. Just run it. It reads the masks in
C:\\Cellpose All Slides\\slides_masks and writes per_slide_grainsize.csv
onto your Desktop.
"""

import os, glob, csv, sys
import numpy as np
from PIL import Image

try:
    from skimage.measure import regionprops
except Exception:
    print("Could not import scikit-image. Run this in the (cellpose) prompt.")
    sys.exit(1)

FOLDER = r"C:\Cellpose All Slides\slides_masks"
SCALE = 2.271e-3          # mm per pixel (all masks output at 2.271 um/px)
SOLIDITY_MIN = 0.80
OUT = os.path.join(os.path.expanduser("~"), "Desktop", "per_slide_grainsize.csv")


def wclass(ecd_mm):
    if ecd_mm < 0.0625: return "Silt"
    if ecd_mm < 0.125:  return "VFine"
    if ecd_mm < 0.25:   return "Fine"
    return "Medplus"


def find_masks(folder):
    for pat in ("*_cp_masks.png", "*_masks.png", "*.png"):
        hits = sorted(glob.glob(os.path.join(folder, pat)))
        if hits:
            return hits
    return []


def main():
    if not os.path.isdir(FOLDER):
        print("FOLDER NOT FOUND:", FOLDER)
        print("Tell Claude the exact folder path and he'll fix this line.")
        return
    files = find_masks(FOLDER)
    print(f"Found {len(files)} mask files in {FOLDER}")
    if not files:
        print("No .png masks found. Tell Claude.")
        return

    rows, skipped = [], 0
    for i, fp in enumerate(files, 1):
        name = os.path.basename(fp)
        try:
            a = np.array(Image.open(fp))
            if a.ndim == 3:
                a = a[..., 0]
            a = a.astype(np.int32)
            if int(a.max()) == 0:
                skipped += 1
                continue
            areas = np.array([p.area for p in regionprops(a) if p.solidity >= SOLIDITY_MIN],
                             dtype=float)
            if len(areas) == 0:
                skipped += 1
                continue
            ecd = 2 * np.sqrt(areas * SCALE**2 / np.pi)   # mm
            cls = np.array([wclass(e) for e in ecd])
            n = len(ecd)
            tot = areas.sum()
            cnt = lambda c: round(100 * float(np.sum(cls == c)) / n, 1)
            ar  = lambda c: round(100 * float(areas[cls == c].sum()) / tot, 1)
            meanw_ecd = 2 * np.sqrt(np.average(areas, weights=areas) * SCALE**2 / np.pi)
            rows.append([name, n, round(float(np.median(ecd)), 4), round(float(meanw_ecd), 4),
                         cnt("Medplus"), cnt("Fine"), cnt("VFine"), cnt("Silt"),
                         ar("Medplus"),  ar("Fine"),  ar("VFine"),  ar("Silt")])
        except Exception as e:
            print(f"  ! skipped {name}: {e}")
            skipped += 1
        if i % 10 == 0:
            print(f"  processed {i}/{len(files)}")

    hdr = ["filename", "n_grains", "median_ecd_count_mm", "meanw_ecd_area_mm",
           "count_Medplus_pct", "count_Fine_pct", "count_VFine_pct", "count_Silt_pct",
           "area_Medplus_pct", "area_Fine_pct", "area_VFine_pct", "area_Silt_pct"]
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(hdr)
        w.writerows(rows)

    print("\nDONE.")
    print(f"  measured {len(rows)} slides, skipped {skipped}")
    print(f"  wrote: {OUT}")
    print("  Upload that file (per_slide_grainsize.csv from your Desktop) to Claude.")


if __name__ == "__main__":
    main()
