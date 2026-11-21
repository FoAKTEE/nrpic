"""Lead's batch-4a recheck of C-sidm (predictions L23, L26-L28 in tracks/C-sidm/JOURNAL.md,
2026-11-21T15:50Z).

Own code, independent of drift/scripts/*.py and verify_g1/*.py: reads `box.coll.hst`,
`cc.nrpic.hst`, `cc.z4c.user.hst` by their header names (reader of rv_clusters.py, the lead's
own) and `cc.traj.bin` / `cc.trajmet.bin` directly from their record layout in docs/FORMATS.md
(8 and 17 float64: time, tag, x^i, u_i; time, tag, alpha, beta^i, gamma_ij (xx xy xz yy yz zz),
tau, E, S_i).

    python3 rv_batch4a.py --part base --out DIR     # L23, L26, L27
    python3 rv_batch4a.py --part vi --out DIR       # L28: run (i) joined with its continuation (vi)

L27 uses a coherent part different from the package's: within each of 20 equal-count bins of
the Killing energy E_K(0), 20 equal-count bins of the conserved angular momentum |x x u|(0)
(covariant u, so x x u is the Killing quantity of the rotations), times the sign of x.u at
t = 0: 800 cells of about 125 particles each.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)
from rv_clusters import read_hst  # noqa: E402

SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
CTRL = {
    "cc1_M4": [f"{SCR}/C-20261115-171058-c26cfad/cc1_kninf"],
    "cc1_M8": [f"{SCR}/C-20261121-125459-f03c4ba/cc1_kninf_M8"],
    "cc2_M4": [f"{SCR}/C-20261115-171059-4b70228/cc2_kninf"],
    "cc2_M8": [f"{SCR}/C-20261120-222533-ce50a86/cc2_kninf_M8"],
}
VI = [f"{SCR}/C-20261120-222533-ce50a86/cc2_kninf_M8", f"{SCR}/C-20261121-140023-b0f113e/cc2_kninf_M8_A"]
T10 = f"{SCR}/C-20261115-165902-f9b1c8f"
PKG_D2 = f"{SCR}/C-20261121-140356-f933a0e/diffusion.json"
PKG_M8 = f"{SCR}/C-20261121-140057-92742cf/compare_cc_M8.json"


def join(dirs, fname):
    """Histories of a run and its continuations; a later file keeps only records after the
    last time of the earlier ones."""
    out = None
    for d in dirs:
        p = os.path.join(d, fname)
        if not os.path.exists(p):
            continue
        h = read_hst(p)
        if out is None:
            out = h
            continue
        k = h["time"] > out["time"][-1] + 1e-9
        out = {n: np.concatenate([out[n], h[n][k]]) for n in out}
    return out


def centred_mean(t, y, width):
    return np.array([y[np.abs(t - ti) <= width / 2.0].mean() for ti in t])


def window_mean(t, y, t0, t1):
    k = (t >= t0 - 1e-9) & (t <= t1 + 1e-9)
    return float(y[k].mean()) if k.any() else None


def t10_counts():
    res = {}
    for c in ["mb1", "mb8", "mb64", "seed8"]:
        h = read_hst(f"{T10}/{c}/box.coll.hst")
        res[c] = int(round(h["n_coll"].sum()))
    return res


def control_numbers(dirs):
    h = join(dirs, "cc.nrpic.hst")
    z = join(dirs, "cc.z4c.user.hst")
    t, a = h["time"], h["alpha_probe"]
    y = a - a[0]
    m20 = centred_mean(t, y, 20.0)
    inner = (t >= 10.0) & (t <= t[-1] - 10.0)      # full 20 M windows only
    i = np.flatnonzero(inner)[np.argmax(m20[inner])]
    r = dict(t_end=float(t[-1]), np_min=int(h["np"].min()), np_max=int(h["np"].max()),
             sum_m_spread=float(h["sum_m"].max() - h["sum_m"].min()),
             max20=float(m20[i]), t_max20=float(t[i]),
             pm5={str(tc): window_mean(t, y, tc - 5.0, tc + 5.0) for tc in (100.0, 200.0, 250.0, 300.0)},
             H_mean_100_300=window_mean(z["time"], z["H-norm2"], 100.0, 300.0),
             H0=float(z["H-norm2"][0]), alpha_min_low=float(np.min(h["alpha_min"])))
    return r, (t, y, m20, z["time"], z["H-norm2"])


def traj(dirs):
    """Records grouped by time: dict time -> (tag, x, u, alpha, beta, gamma)."""
    recs = []
    for d in dirs:
        a = np.fromfile(os.path.join(d, "cc.traj.bin"), dtype=np.float64).reshape(-1, 8)
        m = np.fromfile(os.path.join(d, "cc.trajmet.bin"), dtype=np.float64).reshape(-1, 17)
        if a.shape[0] != m.shape[0] or not (np.array_equal(a[:, 0], m[:, 0]) and np.array_equal(a[:, 1], m[:, 1])):
            raise SystemExit(f"traj and trajmet records do not match in {d}")
        for tt in np.unique(a[:, 0]):
            if recs and tt <= recs[-1][0] + 1e-9:
                continue
            k = a[:, 0] == tt
            recs.append((float(tt), a[k], m[k]))
    return recs


def killing(a, m):
    u = a[:, 5:8]
    alpha, beta = m[:, 2], m[:, 3:6]
    g = np.empty((len(a), 3, 3))
    for (i, j), c in zip([(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)], range(6, 12)):
        g[:, i, j] = m[:, c]
        g[:, j, i] = m[:, c]
    gi = np.linalg.inv(g)
    W = np.sqrt(1.0 + np.einsum("ni,nij,nj->n", u, gi, u))
    return alpha * W - np.sum(beta * u, axis=1)


def equal_count_bins(v, nb):
    r = np.empty(len(v), dtype=np.int64)
    r[np.argsort(v, kind="stable")] = (np.arange(len(v)) * nb) // len(v)
    return r


def diffusion(dirs, nb=20):
    recs = traj(dirs)
    t0, a0, m0 = recs[0]
    o0 = np.argsort(a0[:, 1])
    tag0 = a0[o0, 1]
    E0 = killing(a0, m0)[o0]
    x0, u0 = a0[o0, 2:5], a0[o0, 5:8]
    L0 = np.linalg.norm(np.cross(x0, u0), axis=1)
    be = equal_count_bins(E0, nb)
    cell = np.empty(len(E0), dtype=np.int64)
    for b in range(nb):
        k = np.flatnonzero(be == b)
        cell[k] = b * nb + equal_count_bins(L0[k], nb)
    cell = cell * 2 + (np.sum(x0 * u0, axis=1) > 0)
    ncell = np.bincount(cell, minlength=2 * nb * nb)
    t, s2, mde = [], [], []
    for tt, a, m in recs:
        o = np.argsort(a[:, 1])
        if not np.array_equal(a[o, 1], tag0):
            raise SystemExit(f"tags change at t = {tt}")
        dE = killing(a, m)[o] - E0
        cm = np.bincount(cell, weights=dE, minlength=len(ncell)) / np.maximum(ncell, 1)
        t.append(tt)
        s2.append(float(np.mean((dE - cm[cell]) ** 2)))
        mde.append(float(dE.mean()))
    t, s2 = np.array(t), np.array(s2)
    out = dict(t=t.tolist(), s2=s2.tolist(), mean_dE=mde, var_E0=float(np.var(E0)),
               cells_min_max=[int(ncell.min()), int(ncell.max())])
    for name, (ta, tb) in {"full": (25.0, 300.0), "early": (25.0, 75.0), "late": (300.0 + 1e-6, 1e9)}.items():
        k = (t >= ta - 1e-6) & (t <= tb + 1e-6)
        if k.sum() >= 2:
            D, a = np.polyfit(t[k], s2[k], 1)
            out[f"D_{name}"] = float(D)
    return out


def figure_base(ser, d2, pkg, out):
    sys.path.insert(0, os.path.join(WT, "python"))
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.5, 3.6))
    cols = {"cc1_M4": fs.SERIES[0], "cc1_M8": fs.SERIES[1], "cc2_M4": fs.SERIES[2], "cc2_M8": fs.SERIES[3]}
    for lab, (t, y, m20, tz, Hn) in ser.items():
        axs[0].plot(t, y, color=cols[lab], lw=0.5, alpha=0.5)
        axs[0].plot(t, m20, color=cols[lab], lw=1.5, label=lab.replace("_", " "))
        axs[1].semilogy(tz, Hn, color=cols[lab], lw=1.0, label=lab.replace("_", " "))
    axs[0].axhline(0.0, **fs.GUIDE)
    axs[0].set_xlabel(r"$t/M$")
    axs[0].set_ylabel(r"$\alpha_c - \alpha_c(0)$ (thick: centred 20 M mean)")
    axs[0].set_title("collisionless King controls, M/4 and M/8")
    axs[0].legend(frameon=False, fontsize=8)
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_ylabel("H-norm2")
    axs[1].set_title("Hamiltonian constraint")
    ax = axs[2]
    for lab, r in d2.items():
        t, s2 = np.array(r["t"]), np.array(r["s2"])
        ax.plot(t, s2 * 1e6, "o", color=cols[lab], ms=4, label=f"{lab.replace('_', ' ')} (lead cells)")
        ps = np.array(pkg[lab]["s2"])
        ax.plot(np.array(pkg[lab]["t"]), ps * 1e6, "--", color=cols[lab], lw=1.0)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"incoherent var$(\Delta E_K)$ / $10^{-6}$")
    ax.set_title("energy diffusion: lead (dots), package (dashed)")
    ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "rv_drift_b4a"))


def figure_vi(t, y, m40, tz, Hn, d2, out):
    sys.path.insert(0, os.path.join(WT, "python"))
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.5, 3.6))
    ax = axs[0]
    ax.plot(t, y, color=fs.SERIES[3], lw=0.5, alpha=0.5)
    ax.plot(t, m40, color=fs.SERIES[3], lw=1.8, label="centred 40 M mean")
    ax.axvline(300.0, **fs.GUIDE)
    ax.axhline(0.0, **fs.GUIDE)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\alpha_c - \alpha_c(0)$")
    ax.set_title("CC2 on M/8: run (i) and continuation (vi)")
    ax.legend(frameon=False, fontsize=8)
    axs[1].semilogy(tz, Hn, color=fs.SERIES[3], lw=1.0)
    axs[1].axvline(300.0, **fs.GUIDE)
    axs[1].set_xlabel(r"$t/M$")
    axs[1].set_ylabel("H-norm2")
    axs[1].set_title("Hamiltonian constraint")
    ax = axs[2]
    tt, s2 = np.array(d2["t"]), np.array(d2["s2"])
    ax.plot(tt, s2 * 1e6, "o", color=fs.SERIES[3], ms=4)
    ax.axvline(300.0, **fs.GUIDE)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"incoherent var$(\Delta E_K)$ / $10^{-6}$")
    ax.set_title("energy diffusion (lead cells)")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "rv_drift_vi"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["base", "vi"], required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}
    if a.part == "base":
        res["L23_T10_ncoll"] = t10_counts()
        ser = {}
        for lab, dirs in CTRL.items():
            res.setdefault("L26", {})[lab], ser[lab] = control_numbers(dirs)
        L = res["L26"]
        res["L26_ratio_max20_cc1"] = L["cc1_M8"]["max20"] / L["cc1_M4"]["max20"]
        res["L26_ratio_max20_cc2"] = L["cc2_M8"]["max20"] / L["cc2_M4"]["max20"]
        pkg = json.load(open(PKG_D2))
        d2 = {lab: diffusion(dirs) for lab, dirs in CTRL.items()}
        res["L27"] = {lab: {k: v for k, v in r.items() if k not in ("t", "s2", "mean_dE")} for lab, r in d2.items()}
        for lab in d2:
            res["L27"][lab]["pkg_D_full"] = pkg[lab]["fit_full"]["D"]
            res["L27"][lab]["lead_over_pkg_full"] = d2[lab]["D_full"] / pkg[lab]["fit_full"]["D"]
            res["L27"][lab]["lead_over_pkg_early"] = d2[lab]["D_early"] / pkg[lab]["fit_early"]["D"]
        res["L27_ratio_M8_M4"] = {m: d2[f"{m}_M8"]["D_full"] / d2[f"{m}_M4"]["D_full"] for m in ("cc1", "cc2")}
        with open(os.path.join(a.out, "rv_b4a_series.json"), "w") as f:
            json.dump({lab: dict(t=r["t"], s2=r["s2"], mean_dE=r["mean_dE"]) for lab, r in d2.items()}, f)
        figure_base(ser, d2, pkg, a.out)
    else:
        h = join(VI, "cc.nrpic.hst")
        z = join(VI, "cc.z4c.user.hst")
        h1 = read_hst(os.path.join(VI[0], "cc.nrpic.hst"))
        h2 = read_hst(os.path.join(VI[1], "cc.nrpic.hst"))
        t, al = h["time"], h["alpha_probe"]
        y = al - al[0]
        m40 = centred_mean(t, y, 40.0)
        inner = (t >= 320.0) & (t <= t[-1] - 20.0)
        j = np.flatnonzero(inner)
        imin = j[np.argmin(m40[j])] if j.size else None
        k2 = h2["time"] > 300.0 + 1e-9
        res["L28"] = dict(
            t_end=float(t[-1]), np_min=int(h["np"].min()), np_max=int(h["np"].max()),
            sum_m_identical=bool(np.all(h2["sum_m"] == h1["sum_m"][0])),
            join_step=float(h2["alpha_probe"][k2][0] - h1["alpha_probe"][-1]),
            first_after_300=[float(h2["time"][k2][0]), float(h2["alpha_probe"][k2][0])],
            last_of_i=[float(h1["time"][-1]), float(h1["alpha_probe"][-1])],
            min40_after_320=None if imin is None else [float(t[imin]), float(m40[imin])],
            trailing40_end=window_mean(t, y, t[-1] - 40.0, t[-1]),
            pm5={str(tc): window_mean(t, y, tc - 5.0, tc + 5.0) for tc in (300.0, 400.0, 500.0, 600.0)},
            alpha_c_low=float(al.min()), alpha_min_low=float(h["alpha_min"].min()),
            H_mean_100_300=window_mean(z["time"], z["H-norm2"], 100.0, 300.0),
            H_mean_after_300=window_mean(z["time"], z["H-norm2"], 300.0 + 1e-6, 1e9),
            push_unconverged_max=float(h["push_unconverged"].max()))
        d2 = diffusion(VI)
        res["L28_D2"] = {k: v for k, v in d2.items() if k not in ("t", "s2", "mean_dE")}
        res["L28_D2"]["mean_dE_end"] = d2["mean_dE"][-1]
        res["L28_D2"]["t_last"] = d2["t"][-1]
        figure_vi(t, y, m40, z["time"], z["H-norm2"], d2, a.out)
    with open(os.path.join(a.out, f"rv_b4a_{a.part}.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
