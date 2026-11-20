#!/usr/bin/env python3
"""C4 (and a line check of C3): finder results, non-finite times, and trapped points on the
x-axis lines of BH-1 (dx = M/4, M/6, M/8) and BH-1R.

On the line y = z = dx/2 (cells containing the plane 0.01; dx of the local level), with
n = (x, dx/2, dx/2)/r and the spherical decomposition gamma = A n n + B (delta - n n),
K_ij = a n n + b (delta - n n):
  R = r sqrt(B),  KT = K^theta_theta = b/B,  |DR|^2 = (dR/dr)^2 / A,
  2m/R = 1 + (R KT)^2 - |DR|^2;  a round sphere is (future) trapped where 2m/R > 1 and KT > 0.
dR/dr by second-order differences along each half line (x > 0 and x < 0 separately).

Writes c4_lines.json and fig_c4_lines.{png,pdf} into $NRPIC_RUN_DIR.
"""
import json
import os
import sys
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs          # noqa: E402
import vbpaths as P            # noqa: E402
import vbio as V               # noqa: E402

RUNS = ["bh_n128", "bh_n192", "bh_n256", "bh_smr"]


def local_dx(x, run):
    if run != "bh_smr":
        return np.full_like(x, P.RUN_DX[run])
    x16 = x * 16.0
    coarse = np.abs(x16 - np.round(x16)) < 1e-9
    return np.where(coarse, 0.125, 0.0625)


def line_ms(adm, run):
    x = adm["x1v"]
    dx = local_dx(x, run)
    y = z = 0.5 * dx
    r = np.sqrt(x * x + y * y + z * z)
    n = np.stack([x, y, z]) / r
    g = {k: adm["adm_g" + k] for k in ("xx", "xy", "xz", "yy", "yz", "zz")}
    K = {k: adm["adm_K" + k] for k in ("xx", "xy", "xz", "yy", "yz", "zz")}

    def nn(T):
        return (n[0] ** 2 * T["xx"] + n[1] ** 2 * T["yy"] + n[2] ** 2 * T["zz"]
                + 2 * (n[0] * n[1] * T["xy"] + n[0] * n[2] * T["xz"] + n[1] * n[2] * T["yz"]))

    A = nn(g)
    B = 0.5 * (g["xx"] + g["yy"] + g["zz"] - A)
    a = nn(K)
    b = 0.5 * (K["xx"] + K["yy"] + K["zz"] - a)
    R = r * np.sqrt(B)
    KT = b / B
    KL = a / A
    out = dict(x=x, r=r, R=R, KT=KT, KL=KL, A=A, B=B)
    two_m = np.full_like(x, np.nan)
    for side in (x > 0, x < 0):
        idx = np.nonzero(side)[0]
        o = idx[np.argsort(r[idx])]
        dRdr = np.gradient(R[o], r[o])
        DR2 = dRdr ** 2 / A[o]
        two_m[o] = 1.0 + (R[o] * KT[o]) ** 2 - DR2
    out["two_m_over_R"] = two_m
    out["trapped"] = (two_m > 1.0) & (KT > 0)
    return out


def first_nonfinite(path, skip_cols=0):
    try:
        names, d = V.read_hst(path)
    except Exception as e:                         # noqa: BLE001
        return dict(error=str(e))
    bad = ~np.all(np.isfinite(d[:, skip_cols:]), axis=1)
    return dict(t_last=float(d[-1, 0]), n=int(len(d)),
                t_first_nonfinite=float(d[np.argmax(bad), 0]) if bad.any() else None)


def main():
    warnings.simplefilter("ignore", RuntimeWarning)
    out = P.outdir()
    res = {}
    series = {}
    for run in RUNS:
        d = P.RUN_DIR[run]
        rr = {}
        names, hs = V.read_horizon_summary(os.path.join(d, "ball.horizon_summary_0.txt"))
        col = {nm: k for k, nm in enumerate(names)}
        finite = np.isfinite(hs[:, col["mass"]]) if len(hs) else np.zeros(0, bool)
        rr["finder"] = dict(n_searches=int(len(hs)), n_finite=int(finite.sum()),
                            t_first_search=float(hs[0, col["time"]]) if len(hs) else None,
                            t_last_search=float(hs[-1, col["time"]]) if len(hs) else None,
                            t_first_finite=float(hs[finite, col["time"]][0]) if finite.any() else None,
                            all_columns_nan_when_not_found=bool(np.all(~np.isfinite(hs[~finite][:, 2:]))) if (~finite).any() else None)
        rr["nrpic_hst"] = first_nonfinite(os.path.join(d, "ball.nrpic.hst"))
        rr["cstat_hst"] = first_nonfinite(os.path.join(d, "ball.cstat.hst"))
        # z4c.user.hst (AthenaK history): plain columns
        zz = np.loadtxt(os.path.join(d, "ball.z4c.user.hst"), comments="#", ndmin=2)
        badz = ~np.all(np.isfinite(zz), axis=1)
        rr["z4c_user_hst"] = dict(t_last=float(zz[-1, 0]),
                                  t_first_nonfinite=float(zz[np.argmax(badz), 0]) if badz.any() else None)
        log = open(os.path.join(d, "athena.log")).read()
        rr["log_tail_has_time_limit"] = "Terminating on time limit" in log
        rr["log_mentions_nan"] = ("nan" in log.lower())
        files = V.tabout_series(os.path.join(d, "tab"), "adm")
        ts, maxtm, trapped_r, nonfin = [], [], [], []
        first = None
        rows = []
        for f in files:
            adm = V.read_tabout(f)
            L = line_ms(adm, run)
            t = adm["time"]
            fin = np.isfinite(L["two_m_over_R"])
            nonfin.append(int((~np.isfinite(adm["adm_gxx"])).sum()))
            ts.append(t)
            maxtm.append(float(np.nanmax(L["two_m_over_R"][fin])) if fin.any() else np.nan)
            tr = L["trapped"] & fin
            if tr.any():
                rt = L["r"][tr]
                rows.append(dict(t=t, r_trapped=sorted(set(np.round(rt, 4).tolist())),
                                 R_trapped=sorted(set(np.round(L["R"][tr], 4).tolist())),
                                 max_two_m_over_R=float(np.nanmax(L["two_m_over_R"][tr]))))
                if first is None:
                    first = rows[-1]
            series.setdefault(run, []).append((t, L))
        rr["line"] = dict(n_outputs=len(files), t_last=float(ts[-1]) if ts else None,
                          first_output_with_nonfinite_gxx=float(ts[int(np.argmax(np.array(nonfin) > 0))]) if any(nonfin) else None,
                          first_trapped=first, trapped_rows=rows, max_two_m_over_R=list(zip(ts, maxtm)))
        res[run] = rr
    with open(os.path.join(out, "c4_lines.json"), "w") as fh:
        json.dump(res, fh, indent=1, default=float)

    # ------------------------------------------------ figure
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8.0, 6.6))
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.08, top=0.95, wspace=0.32, hspace=0.42)
    lab = {"bh_smr": "BH-1R", "bh_n256": "BH-1 M/8", "bh_n192": "BH-1 M/6", "bh_n128": "BH-1 M/4"}
    cols = {"bh_smr": fs.PAL["red"], "bh_n256": fs.PAL["blue"], "bh_n192": fs.PAL["green"], "bh_n128": fs.PAL["orange"]}
    ax = fig.add_subplot(2, 2, 1)
    for run in RUNS:
        t, mx = zip(*res[run]["line"]["max_two_m_over_R"])
        ax.plot(t, mx, color=cols[run], label=lab[run])
    ax.axhline(1.0, **fs.GUIDE)
    ax.set_xlabel(r"code time $t\,/M$")
    ax.set_ylabel(r"largest $2m/R$ on the $x$ line")
    ax.set_ylim(0, 1.6)
    ax.legend(fontsize=7, frameon=False)
    ax.set_title("Misner-Sharp compactness on the line", fontsize=10)
    ax = fig.add_subplot(2, 2, 2)
    for run in RUNS:
        for rw in res[run]["line"]["trapped_rows"]:
            ax.plot([rw["t"]] * len(rw["r_trapped"]), rw["r_trapped"], ".", ms=3, color=cols[run])
    names, hs = V.read_horizon_summary(os.path.join(P.BH1R, "ball.horizon_summary_0.txt"))
    fin = np.isfinite(hs[:, 2])
    ax.plot(hs[fin, 1], hs[fin, 10], color=fs.PAL["red"], lw=1.0, label="BH-1R finder mean radius")
    ax.set_xlabel(r"code time $t\,/M$")
    ax.set_ylabel(r"coordinate $r$ of trapped line points $/M$")
    ax.set_xlim(9, 16.2)
    ax.set_ylim(0, 0.8)
    ax.legend(fontsize=7, frameon=False)
    ax.set_title(r"trapped points ($2m/R>1$, $K_T>0$)", fontsize=10)
    for j, run in enumerate(["bh_n256", "bh_smr"]):
        ax = fig.add_subplot(2, 2, 3 + j)
        sel = [(t, L) for t, L in series[run] if t in (10.0, 10.5, 11.0, 11.5, 12.0, 13.0, 14.0, 15.0)]
        cc = fs.series_colors(len(sel), "viridis")
        for c_, (t, L) in zip(cc, sel):
            pos = L["x"] > 0
            o = np.argsort(L["r"][pos])
            ax.plot(L["r"][pos][o], L["two_m_over_R"][pos][o], color=c_, lw=1.2, label=f"$t$ = {t:g}")
        ax.axhline(1.0, **fs.GUIDE)
        ax.set_xlim(0, 2.0)
        ax.set_ylim(0, 1.5)
        ax.set_xlabel(r"coordinate radius $r\,/M$ ($x>0$)")
        ax.set_ylabel(r"$2m/R$")
        ax.legend(fontsize=6.5, frameon=False, ncol=2)
        ax.set_title(f"{lab[run]}: $2m/R$ on the line", fontsize=10)
    fs.save(fig, os.path.join(out, "fig_c4_lines"))
    short = {k: {kk: (vv if kk != "line" else {k3: v3 for k3, v3 in vv.items() if k3 not in ("max_two_m_over_R",)})
                 for kk, vv in v.items()} for k, v in res.items()}
    print(json.dumps(short, indent=1, default=float)[:20000])


if __name__ == "__main__":
    main()
