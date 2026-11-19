#!/usr/bin/env python3
"""Temporal convergence A6 of the SR ladder (package tracks/E-stoch-inf/ladder, JOURNAL
entry 8): runs T25, T12, T06 (Courant factor theta = 0.25, 0.125, 0.0625) at N = 32,
nmax2 = 64, s = +-1, dumping at the same times (inputs/a6proc.list).

    a6_analysis.py --run DIR --out DIR

DIR holds T25p, T12p, T06p, T25m, T12m, T06m.  Quantities at every common dump:
- per-mode R^NR (ladder_lib.curvature) of the s = +1 runs; differences between theta
  values, largest over the modes with W > 1/2 relative to |R^NR| (and the top shells
  |n|^2 >= 49 alone);
- perturbations of phi, chi, K (box mean removed): rms of the difference relative to the
  rms of the perturbation; box means: |difference| relative to |mean|;
- D_n = |R^NR_n / R^lin_n - 1| against the linear reference (ladder_lib) for each theta;
- odd and even parts of H under s -> -s (rms relative to <[H]> of the record), the box
  mean of the even part (H0 + mean of the second-order part);
orders p = log2[Delta(0.25, 0.125) / Delta(0.125, 0.0625)].  Writes a6.json and the
figure fig_a6.png/pdf.
"""
import argparse
import json
import os

import numpy as np

import ladder_lib as LL

THETAS = (("T25", 0.25), ("T12", 0.125), ("T06", 0.0625))
NMESH, NMAX2 = 32, 64
MODEFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "inputs",
                        "modes_n64.txt")
FIELDS = ("phi", "chi", "K")


def load(rundir, modes, metric=True):
    out = []
    for f in LL.dump_list(rundir):
        want = (LL.CURV_VARS if metric else []) + ["H", "Mx", "My", "Mz"]
        h, flds = LL.read_dump(f, want)
        row = dict(time=h["time"], cycle=h["cycle"], H=flds["H"],
                   M=np.stack([flds["Mx"], flds["My"], flds["Mz"]]))
        if metric:
            row["rnr"] = LL.curvature(modes, flds)[0]
            for v in FIELDS:
                row[v] = flds[v]
        out.append(row)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    modes = LL.Modes(NMESH, NMAX2)
    P = {name: load(os.path.join(a.run, name + "p"), modes) for name, _ in THETAS}
    Mrun = {name: load(os.path.join(a.run, name + "m"), modes, metric=False)
            for name, _ in THETAS}
    nd = min(len(v) for v in P.values())
    times = np.array([P["T25"][i]["time"] for i in range(nd)])
    for name, _ in THETAS:
        tt = np.array([P[name][i]["time"] for i in range(nd)])
        tm = np.array([Mrun[name][i]["time"] for i in range(nd)])
        if np.abs(tt - times).max() > 1e-9 or np.abs(tm - times).max() > 1e-9:
            raise SystemExit(f"dump times differ: {name} {tt} {tm} {times}")
    con = {name: LL.read_con(os.path.join(a.run, name + "p")) for name, _ in THETAS}
    conm = {name: LL.read_con(os.path.join(a.run, name + "m")) for name, _ in THETAS}

    ref = LL.reference_for(modes, MODEFILE, times[-1] + 0.05, t_eval=list(times))
    alpha = modes.alpha()
    kshell = np.sqrt(modes.shell_n2.astype(float))
    lin, wmode = [], []
    for t in times:
        rk, _ = ref.modes(t)
        w = ref.window(t, kshell)
        lin.append(LL.L_BOX**-1.5 * (w * rk)[modes.shell_of] * alpha)
        wmode.append(w[modes.shell_of])
    lin, wmode = np.array(lin), np.array(wmode)
    efolds = np.array([float(ref.background(t)["lna"]) for t in times])
    top = modes.n2 >= 49
    low = modes.n2 <= 16

    res = dict(run=a.run, times=times.tolist(), efolds=efolds.tolist(),
               thetas=[th for _, th in THETAS], D={}, diff={}, parts={})
    # D_n against the linear reference, per theta
    for name, th in THETAS:
        rnr = np.array([P[name][i]["rnr"] for i in range(nd)])
        d = np.abs(rnr / lin - 1.0)
        dm = np.where(wmode > 0.5, d, np.nan)
        res["D"][name] = dict(
            max_all=np.nanmax(dm, axis=1).tolist(),
            max_top=np.nanmax(np.where(top, dm, np.nan), axis=1).tolist(),
            max_low=np.nanmax(np.where(low, dm, np.nan), axis=1).tolist(),
            last_per_mode=d[-1].tolist())
    # differences between theta values
    pairs = (("T25", "T12"), ("T12", "T06"), ("T25", "T06"))
    for x, y in pairs:
        key = f"{x}-{y}"
        q = dict(R_all=[], R_top=[], R_low=[])
        for v in FIELDS:
            q[f"{v}_pert"] = []
            q[f"{v}_mean"] = []
        q["H0"] = []
        for i in range(nd):
            rx, ry = P[x][i]["rnr"], P[y][i]["rnr"]
            rel = np.abs(rx - ry) / np.abs(ry)
            rel = np.where(wmode[i] > 0.5, rel, np.nan)
            q["R_all"].append(float(np.nanmax(rel)) if np.isfinite(rel).any() else np.nan)
            q["R_top"].append(float(np.nanmax(rel[top])) if np.isfinite(rel[top]).any()
                              else np.nan)
            q["R_low"].append(float(np.nanmax(rel[low])) if np.isfinite(rel[low]).any()
                              else np.nan)
            for v in FIELDS:
                fx, fy = P[x][i][v], P[y][i][v]
                px, py = fx - fx.mean(), fy - fy.mean()
                q[f"{v}_pert"].append(float(np.sqrt(np.mean((px - py)**2)) /
                                            np.sqrt(np.mean(py**2))))
                q[f"{v}_mean"].append(float(abs(fx.mean() - fy.mean()) / abs(fy.mean())))
        res["diff"][key] = q
    # constraint parts per theta
    for name, th in THETAS:
        rows = []
        for i in range(nd):
            cyc = P[name][i]["cycle"]
            rp = con[name][np.nonzero(con[name][:, 1] == cyc)[0][0]]
            rm = conm[name][np.nonzero(conm[name][:, 1] == cyc)[0][0]]
            hmag, mmag = 0.5 * (rp[9] + rm[9]), 0.5 * (rp[10] + rm[10])
            hp, hm = P[name][i]["H"], Mrun[name][i]["H"]
            mp, mm = P[name][i]["M"], Mrun[name][i]["M"]
            ho, he = 0.5 * (hp - hm), 0.5 * (hp + hm)
            mo, me = 0.5 * (mp - mm), 0.5 * (mp + mm)
            rows.append(dict(
                H_odd=float(np.sqrt(np.mean(ho**2)) / hmag),
                H_even=float(np.sqrt(np.mean((he - he.mean())**2)) / hmag),
                H_even_mean=float(he.mean() / hmag),
                M_odd=float(np.sqrt(np.mean((mo**2).sum(axis=0))) / mmag),
                M_even=float(np.sqrt(np.mean(((me - me.mean(axis=(1, 2, 3),
                                                            keepdims=True))**2).sum(axis=0)))
                             / mmag),
                record_H=float(rp[3]), record_M=float(rp[6])))
        res["parts"][name] = {k: [r[k] for r in rows] for k in rows[0]}
    # orders
    def order(u, v):
        u, v = np.asarray(u, float), np.asarray(v, float)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.log2(u / v)
    o = {}
    for k in res["diff"]["T25-T12"]:
        o[k] = order(res["diff"]["T25-T12"][k], res["diff"]["T12-T06"][k]).tolist()
    pr = res["parts"]
    for k in ("H_odd", "H_even", "H_even_mean", "M_odd", "M_even"):
        # change of each part between theta values (not an error difference)
        o[f"{k}_ratio_25_12"] = (np.asarray(pr["T25"][k]) / np.asarray(pr["T12"][k])).tolist()
        o[f"{k}_ratio_12_06"] = (np.asarray(pr["T12"][k]) / np.asarray(pr["T06"][k])).tolist()
    d25, d12, d06 = (np.asarray(pr[n]["H_even_mean"]) for n in ("T25", "T12", "T06"))
    o["H0_diff_order"] = order(np.abs(d25 - d12), np.abs(d12 - d06)).tolist()
    res["orders"] = o

    # verdict on A6 at the dumps where the difference is above 1e-12 relative
    def band(key, lo=3.5, hi=4.5, floor=1e-12, tmin=0.9):
        ok, vals = True, []
        for i, t in enumerate(times):
            if t < tmin:
                continue
            dd = res["diff"]["T12-T06"][key][i]
            if not np.isfinite(dd) or dd < floor:
                continue
            p = o[key][i]
            vals.append(p)
            ok &= bool(lo <= p <= hi)
        # no dump above the rounding level: not applicable (None), not a failure
        return dict(orders=vals, pass_=(ok if vals else None))
    res["A6"] = {k: band(k) for k in ("R_all", "R_top", "R_low", "phi_pert", "chi_pert",
                                      "K_pert", "phi_mean", "chi_mean", "K_mean")}
    dl = {n: res["D"][n]["max_top"][-1] for n, _ in THETAS}
    res["PA6b"] = dict(D_top_last=dl,
                       change_first=abs(dl["T25"] / dl["T12"] - 1.0),
                       change_second=abs(dl["T12"] / dl["T06"] - 1.0))
    with open(os.path.join(a.out, "a6.json"), "w") as fp:
        json.dump(res, fp, indent=1, default=float)
    np.savez(os.path.join(a.out, "a6_modes.npz"), n2=modes.n2,
             **{f"D_last_{n}": np.array(res["D"][n]["last_per_mode"]) for n, _ in THETAS})
    for i, t in enumerate(times):
        print(f"t={t:6.3f} N={efolds[i]:5.2f} "
              + " ".join(f"{k}={o[k][i]:5.2f}" for k in ("R_all", "R_top", "R_low",
                                                       "phi_pert", "chi_pert", "K_pert",
                                                       "K_mean"))
              + f"  dR(25,12)={res['diff']['T25-T12']['R_all'][i]:.2e}"
              + f" dR(12,06)={res['diff']['T12-T06']['R_all'][i]:.2e}")
    print(json.dumps(dict(A6={k: v["pass_"] for k, v in res["A6"].items()},
                          PA6b=res["PA6b"]), indent=1, default=float))
    figure(res, modes, a.out)


def figure(res, modes, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle as fs
    fs.use_style()
    t = np.array(res["efolds"])
    fig, ax = plt.subplots(2, 2, figsize=(fs.FULL_WIDTH, 6.4))
    cols = {"T25-T12": fs.PAL["blue"], "T12-T06": fs.PAL["red"]}
    tcol = (fs.PAL["yellow"], fs.PAL["green"], fs.PAL["blue"])
    lab = {"T25-T12": r"$\theta=0.25$ vs $0.125$", "T12-T06": r"$\theta=0.125$ vs $0.0625$"}
    a0 = ax[0, 0]
    s0 = slice(1, None)                       # t = 0: identical slices, difference 0
    for key in ("T25-T12", "T12-T06"):
        q = {k: np.asarray(v)[s0] for k, v in res["diff"][key].items()}
        a0.semilogy(t[s0], q["R_all"], "o-", color=cols[key], ms=3,
                    label=lab[key] + r", $R^{\rm NR}_n$")
        a0.semilogy(t[s0], q["chi_pert"], "s--", color=cols[key], ms=3,
                    label=lab[key] + r", $\delta\chi$")
        a0.semilogy(t[s0], q["chi_mean"], "d-.", color=cols[key], ms=3,
                    label=lab[key] + r", $\langle\chi\rangle$")
        a0.semilogy(t[s0], q["K_mean"], "^:", color=cols[key], ms=3,
                    label=lab[key] + r", $\langle K\rangle$")
    a0.axhline(1e-12, **fs.MASK_LINE)
    a0.set_ylim(1e-14, 3e-3)
    a0.set_xlabel(r"e-folds $\mathcal{N}-\mathcal{N}_*$")
    a0.set_ylabel("relative difference")
    a0.legend(fontsize=5.5, ncol=2, loc="center", bbox_to_anchor=(0.5, 0.42))
    a1 = ax[0, 1]
    o = res["orders"]
    for key, mk in (("R_all", "o-"), ("R_top", "v-"), ("phi_pert", "s--"),
                    ("chi_pert", "d--"), ("K_pert", "x--"), ("chi_mean", "D-."),
                    ("K_mean", "^:")):
        lbl = key.replace("_", " ") + (" (at rounding)" if key == "K_mean" else "")
        a1.plot(t, o[key], mk, ms=3, label=lbl)
    a1.axhspan(3.5, 4.5, color="0.9", zorder=0)
    a1.axhline(4.0, **fs.GUIDE)
    a1.set_ylim(0, 8)
    a1.set_xlabel(r"e-folds $\mathcal{N}-\mathcal{N}_*$")
    a1.set_ylabel(r"order $\log_2[\Delta(0.25,0.125)/\Delta(0.125,0.0625)]$")
    a1.legend(fontsize=6, ncol=2, loc="lower right")
    a2 = ax[1, 0]
    k = np.sqrt(modes.n2.astype(float))
    for (name, th), c in zip(THETAS, tcol):
        d = np.array(res["D"][name]["last_per_mode"])
        a2.loglog(k * (1 + 0.02 * (THETAS.index((name, th)) - 1)), d, ".", color=c, ms=2,
                  label=rf"$\theta={th}$")
    a2.axhline(0.02, **fs.GUIDE)
    a2.set_xticks([1, 2, 4, 8])
    a2.set_xticklabels(["1", "2", "4", "8"])
    a2.set_xlabel(r"$|n|$")
    a2.set_ylabel(r"$D_n$ at the last dump")
    a2.legend(fontsize=7, loc="lower right")
    a3 = ax[1, 1]
    pr = res["parts"]
    for (name, th), c in zip(THETAS, tcol):
        a3.semilogy(t, pr[name]["H_odd"], "o-", color=c, ms=3, label=rf"odd, $\theta={th}$")
        a3.semilogy(t, pr[name]["H_even"], "s--", color=c, ms=3, label=rf"even, $\theta={th}$")
        a3.semilogy(t, np.abs(pr[name]["H_even_mean"]), "^:", color=c, ms=3,
                    label=rf"$|$mean even$|$, $\theta={th}$")
    a3.set_xlabel(r"e-folds $\mathcal{N}-\mathcal{N}_*$")
    a3.set_ylabel(r"parts of $\mathcal{H}$ / $\langle[\mathcal{H}]\rangle$")
    a3.legend(fontsize=5.5, ncol=1, loc="lower left")
    fig.tight_layout()
    fs.save(fig, os.path.join(outdir, "fig_a6"))
    plt.close(fig)


if __name__ == "__main__":
    main()
