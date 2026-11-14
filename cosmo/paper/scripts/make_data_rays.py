"""Light-ray bundles of the collapse runs for the working paper: deviation of the
luminosity distance from the homogeneous relation along each ray, for the relativistic
run and the Newtonian reference, and their ratio at equal redshift. Emission times: the
set of the source paper."""
import os

import numpy as np

from common import DATA, L, RUNS
import east_rays as er
import ray_obs as ar

WANT = {0.01: (1, 28, 43, 52), 0.005: (1, 28, 58, 112), 0.0025: (1, 28, 59, 163),
        0.05: (1, 4, 8, 9)}
out = {}
for d, want in WANT.items():
    gdir = os.path.join(RUNS, f"east_d{d:g}_n64_v2")
    nfile = os.path.join(RUNS, f"newton_d{d:g}_n64_v2", "newton_rays.npz")
    if not (os.path.exists(os.path.join(gdir, "rays.npz")) and os.path.exists(nfile)):
        continue
    gb = {b["bundle"]: b for b in ar.gr_bundles(gdir)}
    nb = {b["bundle"]: b for b in er.load_newton(nfile)}
    k = 0
    for b in sorted(set(gb) & set(nb)):
        g, w = gb[b], nb[b]
        ae = g["a_emit"]
        near = min(want, key=lambda v: abs(v - ae))
        if abs(near - ae) > max(2.5, 0.06*near):
            continue
        kind = g["kind"]
        x0 = np.full(3, 0.25*L if kind == 0 else 0.75*L)
        g, w = er.cut(g, x0), er.cut(w, x0)
        if len(g["z"]) < 4 or len(w["z"]) < 4:
            continue
        zc, diff = er.compare(g, w)
        key = f"{d:g}_{k}"
        out[f"z_{key}"] = g["z"]
        out[f"y_{key}"] = g["D_L"]/g["D_FRW"] - 1.0
        out[f"zn_{key}"] = w["z"]
        out[f"yn_{key}"] = w["D_L"]/w["D_FRW"] - 1.0
        out[f"zc_{key}"] = zc
        out[f"diff_{key}"] = diff
        out[f"meta_{key}"] = np.array([kind, ae, near])
        k += 1
    out[f"n_{d:g}"] = k
np.savez_compressed(os.path.join(DATA, "rays.npz"), **out)
print("wrote", os.path.join(DATA, "rays.npz"), {k: int(v) for k, v in out.items() if k.startswith("n_")})
