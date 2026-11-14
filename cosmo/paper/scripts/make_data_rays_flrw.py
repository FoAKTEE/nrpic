"""Light-ray bundles of the homogeneous-universe test for the working paper."""
import os

import numpy as np

from common import DATA, RUNS
import ray_obs as ar

out = {"dt": 1.0/32.0}
bundles = ar.gr_bundles(os.path.join(RUNS, "flrw_rays_n32_cpu"), base="flrw")
out["nbundle"] = len(bundles)
for i, b in enumerate(bundles):
    for k in ("t", "z", "D_L"):
        out[f"{k}_{i}"] = b[k]
    out[f"t_emit_{i}"] = b["t_emit"]
    out[f"kind_{i}"] = b["kind"]
    out[f"solid_angle_{i}"] = b["solid_angle"]
np.savez(os.path.join(DATA, "rays_flrw.npz"), **out)
print("wrote", os.path.join(DATA, "rays_flrw.npz"))
