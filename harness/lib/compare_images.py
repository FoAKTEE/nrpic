"""Compare two PNG files pixel by pixel (used by nrpic-stage verify; needs numpy and matplotlib,
so it runs through `nrpic-env exec -- python`).

    python compare_images.py <committed.png> <regenerated.png>

Prints one JSON line: {"same_shape": bool, "shape_a": [...], "shape_b": [...], "rms": float,
"max": float, "frac_diff": float}; values in [0, 1] units of the colour channels.
"""
import json
import sys

import numpy as np
import matplotlib.image as mpimg


def load(p):
    a = mpimg.imread(p).astype(float)
    if a.ndim == 2:
        a = a[:, :, None]
    if a.shape[2] == 4:                      # composite onto white, ignore alpha
        a = a[:, :, :3] * a[:, :, 3:4] + (1 - a[:, :, 3:4])
    return a


def main(pa, pb):
    a, b = load(pa), load(pb)
    out = {"same_shape": a.shape == b.shape, "shape_a": list(a.shape), "shape_b": list(b.shape)}
    if a.shape == b.shape:
        d = np.abs(a - b)
        out.update(rms=float(np.sqrt(np.mean(d ** 2))), max=float(d.max()),
                   frac_diff=float(np.mean(d.max(axis=2) > 1.0 / 255)))
    else:
        out.update(rms=None, max=None, frac_diff=None)
    print(json.dumps(out))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
