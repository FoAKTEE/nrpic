"""V6b: tracer trajectories against the exact cycloid. Clock test (code proper time against
the integral of alpha/W dt along the samples) and dynamics test (areal radius from the
tangential metric component against R_LTB(tau)).

python3 v6_tracers.py --scratch <scratch/D-bh-dress> --ref <V1 run dir> --out <dir>
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ltb  # noqa: E402
import vio  # noqa: E402
import figstyle as fs  # noqa: E402

RUNS = {"ES-FL": ("D-20261121-203150-15f2bad", "esfl", "N"),
        "FK": ("D-20261123-022725-a553496", "esflk", "N"),
        "FN4": ("D-20261124-134157-b17938b", "esflk4n", "4N"),
        "FL16": ("D-20261124-172745-72472ed", "esfl16", "N")}
GROUPS = [10.0, 20.0, 28.0, 36.0]


def dedupe(a):
    key = a[:, 1] * 1e7 + a[:, 0]
    rev = key[::-1]
    _, idx = np.unique(rev, return_index=True)
    keep = np.sort(len(key) - 1 - idx)
    a = a[keep]
    return a[np.lexsort((a[:, 0], a[:, 1]))]


def analyse(scr, ref_dir, lab):
    rid, base, lat = RUNS[lab]
    d = os.path.join(scr, rid)
    tr = dedupe(vio.read_records(os.path.join(d, f"{base}.traj.bin"), 8))
    tm = dedupe(vio.read_records(os.path.join(d, f"{base}.trajmet.bin"), 17))
    z = np.load(os.path.join(ref_dir, f"ltbref_{lat.replace('/', 'q')}.npz"))
    R0all, mtab = z["R0"], z["m_tab_p"]
    out = {}
    curves = {}
    tags = np.unique(tr[:, 1]).astype(int)
    for g in GROUPS:
        gt = [t for t in tags if abs(R0all[t] - g) < 1e-3]
        res = []
        for t in gt:
            a = tr[tr[:, 1] == t]
            b = tm[tm[:, 1] == t]
            n = min(len(a), len(b))
            a, b = a[:n], b[:n]
            if not np.allclose(a[:, 0], b[:, 0]):
                # align on common times
                common, ia, ib = np.intersect1d(a[:, 0], b[:, 0], return_indices=True)
                a, b = a[ia], b[ib]
            t_s = a[:, 0]
            x = a[:, 2:5]
            u = a[:, 5:8]
            alpha = b[:, 2]
            gxx, gxy, gxz, gyy, gyz, gzz = (b[:, k] for k in range(6, 12))
            tau_code = b[:, 12]
            G = np.stack([np.stack([gxx, gxy, gxz], -1), np.stack([gxy, gyy, gyz], -1),
                          np.stack([gxz, gyz, gzz], -1)], -2)
            ok = np.isfinite(alpha) & (alpha > 0) & np.all(np.isfinite(G.reshape(len(G), -1)), axis=1) \
                & (np.linalg.det(G) > 0)
            t_s, x, u, alpha, G, tau_code = t_s[ok], x[ok], u[ok], alpha[ok], G[ok], tau_code[ok]
            Gi = np.linalg.inv(G)
            W = np.sqrt(1.0 + np.einsum("ni,nij,nj->n", u, Gi, u))
            rate = alpha / W
            tau_int = tau_code[0] + np.concatenate([[0.0], np.cumsum(0.5 * (rate[1:] + rate[:-1]) * np.diff(t_s))])
            r = np.linalg.norm(x, axis=1)
            nvec = x / r[:, None]
            ez = np.array([0.0, 0.0, 1.0])
            e = np.cross(nvec, ez)
            small = np.linalg.norm(e, axis=1) < 0.3
            e[small] = np.cross(nvec[small], np.array([1.0, 0.0, 0.0]))
            e /= np.linalg.norm(e, axis=1)[:, None]
            B = np.einsum("ni,nij,nj->n", e, G, e)
            Rsim = r * np.sqrt(B)
            m = mtab[t]
            R0 = R0all[t]
            Rltb = ltb.radius_at_tau(tau_code, R0, m)
            Rmax_ex = m * R0 / ltb.MBH
            # clock: relative difference at the last sample with tau_code > 0 and t <= 250
            w = t_s <= 250.0
            k = np.where(w)[0][-1]
            clock_rel = (tau_int[k] - tau_code[k]) / tau_code[k]
            # offset in proper time at fixed areal radius on the infall branch
            i_max = int(np.argmax(Rsim))
            fall = slice(i_max, None)
            dtau_at = {}
            for Rq in [0.75 * Rmax_ex, 0.5 * Rmax_ex, 0.25 * Rmax_ex, 6.0, 4.0]:
                Rf = Rsim[fall]
                if Rf.min() < Rq < Rf.max():
                    j = np.where(Rf < Rq)[0][0]
                    f = (Rf[j - 1] - Rq) / (Rf[j - 1] - Rf[j])
                    tq = tau_code[fall][j - 1] + f * (tau_code[fall][j] - tau_code[fall][j - 1])
                    # exact tau on the infall branch at Rq
                    A = m * R0 / 2.0
                    T = A ** 1.5 / np.sqrt(m)
                    eta0 = np.arccos(1 - 2.0 / m)
                    eta = 2 * np.pi - np.arccos(1 - Rq / A)
                    tex = T * ((eta - np.sin(eta)) - (eta0 - np.sin(eta0)))
                    dtau_at[f"{Rq:.3f}"] = float(tq - tex)
            res.append(dict(tag=int(t), R0=float(R0), m=float(m), R0_measured_t0=float(Rsim[0]),
                            Rmax_sim=float(Rsim.max()), Rmax_exact=float(Rmax_ex),
                            tau_at_Rmax_sim=float(tau_code[i_max]),
                            clock_rel_at_250=float(clock_rel), clock_max_abs=float(np.max(np.abs(tau_int - tau_code))),
                            R_minus_RLTB_max=float(np.max(np.abs(Rsim - Rltb)[tau_code < tau_code[-1]])),
                            dtau_at_R=dtau_at, t_last=float(t_s[-1]), tau_last=float(tau_code[-1]),
                            R_last=float(Rsim[-1])))
            if t == gt[0]:
                curves[g] = (tau_code, Rsim, Rltb, tau_int - tau_code)
        if res:
            out[str(g)] = dict(
                n=len(res),
                R0_meas_minus_R0=float(np.max([abs(x["R0_measured_t0"] - x["R0"]) for x in res])),
                Rmax_sim_minus_exact=[float(np.min([x["Rmax_sim"] - x["Rmax_exact"] for x in res])),
                                      float(np.median([x["Rmax_sim"] - x["Rmax_exact"] for x in res])),
                                      float(np.max([x["Rmax_sim"] - x["Rmax_exact"] for x in res]))],
                clock_rel_at_250=[float(np.min([x["clock_rel_at_250"] for x in res])),
                                  float(np.max([x["clock_rel_at_250"] for x in res]))],
                dtau_at_R={k: float(np.median([x["dtau_at_R"][k] for x in res if k in x["dtau_at_R"]]))
                           for k in res[0]["dtau_at_R"]},
                first=res[0])
    return out, curves


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    allres, allc = {}, {}
    for lab in RUNS:
        r, c = analyse(a.scratch, a.ref, lab)
        allres[lab] = r
        allc[lab] = c
        print(lab, json.dumps({g: {k: v for k, v in x.items() if k != "first"} for g, x in r.items()}, indent=None))
    json.dump(allres, open(os.path.join(a.out, "v6_tracers.json"), "w"), indent=1)
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 3.6))
    ax1 = fig.add_axes([0.08, 0.14, 0.40, 0.8])
    ax2 = fig.add_axes([0.58, 0.14, 0.40, 0.8])
    cols = {"ES-FL": fs.PAL["red"], "FK": fs.PAL["blue"], "FN4": fs.PAL["yellow"], "FL16": fs.PAL["orange"]}
    for lab, c in allc.items():
        for g, ls in [(20.0, ":"), (28.0, "-")]:
            if g in c:
                tau, Rs, Rl, dcl = c[g]
                ax1.plot(tau, Rs - Rl, color=cols[lab], ls=ls, label=f"{lab} $R_0$={g:.0f}")
                ax2.plot(tau, dcl, color=cols[lab], ls=ls)
    ax1.axhline(0, color="k", lw=1)
    ax1.set_xlabel(r"$\tau$ [M]")
    ax1.set_ylabel(r"$R_{\rm sim}(\tau)-R_{\rm LTB}(\tau)$ [M]")
    ax1.set_ylim(-1.0, 0.3)
    ax1.legend(loc="lower left", fontsize=8, ncol=2)
    ax2.axhline(0, color="k", lw=1)
    ax2.set_xlabel(r"$\tau$ [M]")
    ax2.set_ylabel(r"$\int\alpha/W\,dt-\tau_{\rm code}$ [M]")
    fs.save(fig, os.path.join(a.out, "v6_tracers"))


if __name__ == "__main__":
    main()
