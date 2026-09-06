"""
recon_masks.py  --  read-only reconnaissance, changes nothing on disk.

It scans a folder (and its subfolders) for Cellpose mask files that belong to
the three evaluation slides, and prints the format, image dimensions, and the
number of grains in each. This tells us how your ground-truth and predicted
masks are stored so the evaluation script can be built to match.

HOW TO RUN (in the Anaconda Prompt with (cellpose) active):
    cd "C:\\Users\\Matt\\Desktop\\Geology Paper Desktop Stuff"
    python recon_masks.py

or point it at any folder explicitly:
    python recon_masks.py "C:\\Users\\Matt\\Desktop\\Geology Paper Desktop Stuff"
"""

import os
import sys
import glob
import numpy as np

# Slides we need for the evaluation. Add/adjust if your filenames differ.
KEYS = ["BVLX-01-1", "LLCR03-01-4", "RGLL03-01-1"]

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."


def load_label_array(path):
    """Return a 2D integer label array from a .npy (_seg.npy) or a mask .png."""
    lower = path.lower()
    if lower.endswith(".npy"):
        obj = np.load(path, allow_pickle=True)
        try:
            d = obj.item()
            if isinstance(d, dict) and "masks" in d:
                return np.asarray(d["masks"]), "npy(dict['masks'])"
            return np.asarray(d), "npy(array)"
        except Exception:
            return np.asarray(obj), "npy(array)"
    else:
        # PNG / TIF label image. Try OpenCV first (16-bit safe), then tifffile.
        try:
            import cv2
            im = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if im is not None:
                return np.asarray(im), "image(cv2)"
        except Exception:
            pass
        try:
            import tifffile
            return np.asarray(tifffile.imread(path)), "image(tifffile)"
        except Exception as e:
            raise RuntimeError(f"could not read image: {e}")


def describe(path):
    try:
        arr, how = load_label_array(path)
    except Exception as e:
        return f"  !! COULD NOT READ ({e})"
    shape = "x".join(str(s) for s in arr.shape)
    dtype = str(arr.dtype)
    note = ""
    if arr.ndim == 2 and np.issubdtype(arr.dtype, np.integer):
        uniq = np.unique(arr)
        n = int((uniq != 0).sum())
        note = f"grains={n}, max_label={int(arr.max())}"
    elif arr.ndim == 2:
        note = "2D but not integer labels (may be an overlay, not a label mask)"
    else:
        note = "not 2D (likely an RGB overlay, not a label mask)"
    return f"  read_as={how} | dims={shape} | dtype={dtype} | {note}"


def main():
    root = os.path.abspath(ROOT)
    print(f"Scanning: {root}\n")
    hits = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            lf = f.lower()
            is_maskish = lf.endswith(".npy") or ("mask" in lf and (lf.endswith(".png") or lf.endswith(".tif") or lf.endswith(".tiff")))
            if not is_maskish:
                continue
            if not any(k.lower() in lf for k in KEYS):
                continue
            hits.append(os.path.join(dirpath, f))

    if not hits:
        print("No matching mask files found for:", ", ".join(KEYS))
        print("If your ground-truth/predicted files use different names, tell me the")
        print("actual filenames for these three slides and I'll adjust the script.")
        return

    for p in sorted(hits):
        print(os.path.relpath(p, root))
        print(describe(p))
        print()

    print(f"Total matching files: {len(hits)}")
    print("\nPaste this entire printout back. In particular I need, per slide, which file")
    print("is the hand-traced ground truth and which is the model prediction, plus whether")
    print("their dims match (they must be on the same pixel grid to compare).")


if __name__ == "__main__":
    main()
