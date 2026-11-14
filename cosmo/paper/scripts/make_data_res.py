"""Resolution study of the collapse at amplitude 0.01 (quadratic cloud, one particle per
cell) for the working paper: observer density contrast at the overdensity, infall of the
fiducial observers, and the mean relative Hamiltonian constraint, at 64, 96, 128 cells."""
import os

import numpy as np

from common import DATA, RUNS
import east_c2 as ec
import shape_study as ss
from delta_obs import gr_probes


def thin(n, m=600):
    return np.unique(np.linspace(0, n - 1, min(n, m)).astype(int))


out = {"ns": []}
for n in (64, 96, 128):
    gdir = os.path.join(RUNS, f"east_d0.01_n{n}_tsc")
    if not os.path.exists(os.path.join(gdir, "east.nrpic.hst")):
        continue
    out["ns"].append(n)
    g, _ = gr_probes(gdir)
    i = thin(len(g["t"]))
    out[f"gr_ap_{n}"] = g["a_p_0"][i]
    out[f"gr_do_{n}"] = g["delta_obs_0"][i]
    f = ec.gr_fiducial(gdir)
    dg = ec.distances(f["x"], f["q"], f["axis"])
    apg = ec.a_of_tau(f["tau"])
    nfile = os.path.join(RUNS, f"newton_d0.01_n{n}_tsc", "newton.npz")
    nw = dict(np.load(nfile)) if os.path.exists(nfile) else None
    if nw is not None:
        ok = np.isfinite(nw["delta_obs_0"])
        j = thin(int(ok.sum()))
        out[f"nw_ap_{n}"] = nw["a_p_0"][ok][j]
        out[f"nw_do_{n}"] = nw["delta_obs_0"][ok][j]
        dn = ec.distances(np.mod(nw["x"], ec.L), nw["q_fid"], nw["axis_fid"])
        apn = ec.a_of_tau(nw["t_p"])
    a10 = []
    for fr in ec.SHOWN:
        gg, nn = [], []
        for k in range(len(f["axis"])):
            s0 = f["q"][k, f["axis"][k]] - ec.XPK
            if abs(s0 - fr*ec.L) < 1e-9:
                gg.append(ec.below(apg[:, k], dg[:, k], 0.1*dg[0, k]))
                if nw is not None:
                    nn.append(ec.below(apn[:, k], dn[:, k], 0.1*dn[0, k]))
        a10.append((np.mean(gg), np.mean(nn) if nn else np.nan))
    out[f"a10_{n}"] = np.array(a10)
    cs = ss.cstat(gdir)
    j = thin(len(cs["a"]), 500)
    out[f"cs_a_{n}"] = cs["a"][j]
    out[f"cs_Hr_{n}"] = cs["Hr_mean"][j]
out["ns"] = np.array(out["ns"])
np.savez_compressed(os.path.join(DATA, "resolution.npz"), **out)
for n in out["ns"]:
    a = out[f"a10_{n}"]
    print(n, "infall (GR):", np.round(a[:, 0], 2), "delay (percent):", np.round(100*(a[:, 0]/a[:, 1] - 1), 2))
