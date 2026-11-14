"""Observer density contrast of the small-amplitude run and of its Newtonian reference
for the working paper."""
import os

import numpy as np

from common import DATA, REPO, RUNS
from delta_obs import gr_probes

g, _ = gr_probes(os.path.join(RUNS, "east_d1e-4_n32_cpu"))
nw = np.load(os.path.join(REPO, ".work", "newton_d1e-4_n32.npz"))
out = {"delta": 1e-4, "n": 32}
for i in (0, 1):
    out[f"gr_a_p_{i}"] = g[f"a_p_{i}"]
    out[f"gr_delta_obs_{i}"] = g[f"delta_obs_{i}"]
    out[f"nw_a_p_{i}"] = nw[f"a_p_{i}"]
    out[f"nw_delta_obs_{i}"] = nw[f"delta_obs_{i}"]
np.savez(os.path.join(DATA, "linear.npz"), **out)
print("wrote", os.path.join(DATA, "linear.npz"))
