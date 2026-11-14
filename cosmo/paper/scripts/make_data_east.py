"""Data of the single-wavelength collapse for the working paper: observer density
contrasts, tracks of the fiducial observers, the relativistic delay for the three cloud
shapes, and the constraint violation against the scale factor."""
import os

import numpy as np

from common import DATA, RUNS
import east_c2 as ec
import shape_study as ss

DELTAS = (0.0025, 0.005, 0.01, 0.05)
SHAPES = (("v2", ""), ("tsc", "_tsc"), ("pcs", "_pcs"))


def thin(n, m=700):
    return np.unique(np.linspace(0, n - 1, min(n, m)).astype(int))


out = {"deltas": np.array(DELTAS), "shown": np.array(ec.SHOWN)}
for d in DELTAS:
    key = f"{d:g}"
    for tag, nsuf in SHAPES:
        v = ec.load(RUNS, d, 64, "_" + tag, nsuf)
        if v is None:
            continue
        g, nw, f = v["g"], v["nw"], v["f"]
        dg = ec.distances(f["x"], f["q"], f["axis"])
        apg = ec.a_of_tau(f["tau"])
        dn = ec.distances(np.mod(nw["x"], ec.L), nw["q_fid"], nw["axis_fid"])
        apn = ec.a_of_tau(nw["t_p"])
        # delays: distance below a tenth, mean over the three directions
        dly = []
        for fr in ec.SHOWN:
            gg, nn = [], []
            for j in range(len(f["axis"])):
                s0 = f["q"][j, f["axis"][j]] - ec.XPK
                if abs(s0 - fr*ec.L) < 1e-9:
                    gg.append(ec.below(apg[:, j], dg[:, j], 0.1*dg[0, j]))
                    nn.append(ec.below(apn[:, j], dn[:, j], 0.1*dn[0, j]))
            dly.append((np.mean(gg), np.mean(nn)) if gg and np.isfinite(gg).all()
                       and np.isfinite(nn).all() else (np.nan, np.nan))
        out[f"a10_{tag}_{key}"] = np.array(dly)
        out[f"rise_{tag}_{key}"] = np.array(
            [(ec.rise(g["a_p_0"], g["delta_obs_0"], lev),
              ec.rise(nw["a_p_0"], nw["delta_obs_0"], lev)) for lev in (1.0, 10.0, 100.0)])
        if tag != "v2":
            continue
        ig = thin(len(g["t"]))
        okn = np.isfinite(nw["delta_obs_0"])
        inw = thin(int(okn.sum()))
        for i in (0, 1):
            out[f"gr_ap{i}_{key}"] = g[f"a_p_{i}"][ig]
            out[f"gr_do{i}_{key}"] = g[f"delta_obs_{i}"][ig]
            out[f"nw_ap{i}_{key}"] = nw[f"a_p_{i}"][okn][inw]
            out[f"nw_do{i}_{key}"] = nw[f"delta_obs_{i}"][okn][inw]
        # fiducial observers on the x line at the four starting distances
        js = [j for j in range(len(f["axis"])) if f["axis"][j] == 0 and any(
            abs(f["q"][j, 0] - ec.XPK - fr*ec.L) < 1e-9 for fr in ec.SHOWN)]
        it = thin(len(f["t"]), 1200)
        out[f"fid_gr_ap_{key}"] = apg[it][:, js]
        out[f"fid_gr_d_{key}"] = dg[it][:, js]
        itn = thin(len(nw["tau"]), 1200)
        out[f"fid_nw_ap_{key}"] = apn[itn][:, js]
        out[f"fid_nw_d_{key}"] = dn[itn][:, js]
    for tag, _ in SHAPES:
        c = ss.cstat(os.path.join(RUNS, f"east_d{key}_n64_{tag}"))
        if c is not None:
            i = thin(len(c["a"]), 500)
            out[f"cs_a_{tag}_{key}"] = c["a"][i]
            out[f"cs_Hr_{tag}_{key}"] = c["Hr_mean"][i]
            out[f"cs_Mr_{tag}_{key}"] = c["Mr_mean"][i]
np.savez_compressed(os.path.join(DATA, "east.npz"), **out)
print("wrote", os.path.join(DATA, "east.npz"), os.path.getsize(os.path.join(DATA, "east.npz"))//1024, "kB")
for d in DELTAS:
    key = f"{d:g}"
    print(key, "delay (a10 ratio - 1) by shape:", {t: np.round(out[f"a10_{t}_{key}"][:, 0]/out[f"a10_{t}_{key}"][:, 1] - 1, 4).tolist() for t, _ in SHAPES if f"a10_{t}_{key}" in out})
