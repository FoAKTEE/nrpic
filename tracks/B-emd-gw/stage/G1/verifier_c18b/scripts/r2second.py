"""verifier_c18b, ledger line 217: the second reading of the second round of the first source.

    python3 r2second.py OUTDIR

Line 217 says: 30 numbers of the note (lines 201, 202, 204, 205, 209, 211, 212) were compared
with the first-source package's own comparison files (conv_summary.json of runs
B-20261119-163037-6553674 and B-20261119-164017-cd1ba52), largest relative difference 1.96e-12.
Here a third, own reduction of the same per-dump diagnostics (the case files of the analysis
runs, single-precision 'bin' rows, repeated times dropped) computes the 30 numbers from their
definitions and compares them with the comparison files and with the printed ledger values.
Definitions (from the note's ledger rows and the comparison script's docstring):
  c = complex h_+ at K1 (c - i s); a = (1 + tau/2)^2; series of different runs compared at the
  times of the first by cubic-spline interpolation of the other (own CubicSpline call).
  K mod ratio: |c_meas| / |c_pred|, 3 <= a <= 20, c_pred = cross_K * g_cross + nn_K * g_nn
     of null_prediction.json (run B-20261119-142733-932e595), min / median / max.
  amp ratio: |c(jit 0.3) / c(jit 0.1)|, 1.5 <= a <= 20, min / median / max.
  null over signal: |c(jit 0.3)| / |Re c(eps 0.1)|, largest in 2-20, 20-80, 80-140.
  departure: dev = Re c / (s g(tau)) - 1, s = -(5/6) phi_x phi_y, phi_i = -(3/2)(H/k)^2 delta r_i,
     r = (1, eps, 0), g'' + 2 g'/(1 + tau/2) + |K1|^2 (g - 1) = 0 from rest (own ODE solve);
     R_a = mean dev(delta 0.01) / mean dev(delta 0.0025) over a within 5 per cent of a0;
     window = largest a before the first dump with a >= 2 and |dev| > 0.5 per cent.
"""
import json
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline, PchipInterpolator

S = "/data/haiyangw/nrpic/scratch/B-emd-gw"
CASES = {"jit0p3": f"{S}/B-20261119-160530-7bdcb45/jit0p3.json",
         "jit0p1": f"{S}/B-20261119-161519-6e0bc42/jit0p1.json",
         "s01": f"{S}/B-20261115-174722-ba1048d/cw_eps0p1.json",
         "d01_e1": f"{S}/B-20261115-180834-c77a132/cw_eps1.json",
         "d01_e0p3": f"{S}/B-20261115-174722-ba1048d/cw_eps0p3.json",
         "d0025_e1": f"{S}/B-20261119-161519-6e0bc42/d0025_e1.json",
         "d0025_e0p3": f"{S}/B-20261119-163027-f0d304f/d0025_e0p3.json"}
PRED = f"{S}/B-20261119-142733-932e595/null_prediction.json"
NULL_CMP = f"{S}/B-20261119-163037-6553674/conv_summary.json"
DELTA_CMP = f"{S}/B-20261119-164017-cd1ba52/conv_summary.json"
LEDGER = {  # printed values of the ledger lines (note/tables/ledger.tex), for the third column
    "jit0p3_K1": [0.927, 1.04, 1.33], "jit0p1_K1": [0.942, 1.03, 1.27],
    "jit0p3_K2": [0.741, 0.943, 1.0], "jit0p1_K2": [0.728, 0.951, 1.01],
    "amp": [2.12, 2.56, 2.65], "nos": [0.0148, 0.0251, 0.0314],
    "R_e1": [17.9, 16.8, 17.2, 19.1], "R_e0p3": [50.4, 16.8, 19.4, 18.3],
    "win": [10.3, 12.6, 33.7, 41.7]}


def rows(path):
    r = [x for x in json.load(open(path))["rows"] if x.get("kind") == "bin" and "error" not in x]
    r.sort(key=lambda x: x["time"])
    out = []
    for x in r:
        if not out or x["time"] > out[-1]["time"] + 1e-9:
            out.append(x)
    return out


def col(r, key, cplx=True):
    v = np.array([x[key] for x in r], float)
    return v[:, 0] + 1j*v[:, 1] if cplx else v


def a_of(t):
    return (1 + 0.5*np.asarray(t))**2


def at(ts, y, t, kind="cubic"):
    if np.iscomplexobj(y):
        return at(ts, y.real, t, kind) + 1j*at(ts, y.imag, t, kind)
    f = CubicSpline(ts, y) if kind == "cubic" else PchipInterpolator(ts, y)
    v = f(t)
    v[(t < ts[0]) | (t > ts[-1])] = np.nan
    return v


def static(delta, eps):
    k = 2*np.pi/4.0
    phx = -1.5*(1.0/k)**2*delta
    return -(5/6)*phx*(eps*phx)


RTOL = [1e-12]


def g_of(t):
    K = 2*np.pi/4.0*np.sqrt(2.0)
    s = solve_ivp(lambda x, y: [y[1], -2*y[1]/(1 + 0.5*x) - K*K*(y[0] - 1)], (0, float(np.max(t))),
                  [0.0, 0.0], rtol=RTOL[0], atol=RTOL[0]*1e-3, method="DOP853", dense_output=True)
    return s.sol(t)[0]


def reduce(C, P, kind):
    out = {}
    pt = np.array(P["tau"])
    t3 = np.array([x["time"] for x in C["jit0p3"]])
    a3 = a_of(t3)
    for name in ("jit0p3", "jit0p1"):
        r = C[name]
        t = np.array([x["time"] for x in r])
        a = a_of(t)
        m = (a >= 3) & (a <= 20)
        for K in ("K1", "K2"):
            pc = P["cases"][name]
            pr = complex(*pc[f"cross_{K}_plus"])*np.array(P["g_cross"]) + \
                complex(*pc[f"nn_{K}_plus"])*np.array(P["g_nn"])
            ratio = np.abs(col(r, f"h_{K}_plus")[m])/np.abs(at(pt, pr, t, kind)[m])
            out[f"{name}_{K}"] = [float(ratio.min()), float(np.median(ratio)), float(ratio.max())]
    t1 = np.array([x["time"] for x in C["jit0p1"]])
    rr = col(C["jit0p3"], "h_K1_plus")/at(t1, col(C["jit0p1"], "h_K1_plus"), t3, kind)
    m = (a3 >= 1.5) & (a3 <= 20)
    out["amp"] = [float(np.nanmin(np.abs(rr[m]))), float(np.nanmedian(np.abs(rr[m]))),
                  float(np.nanmax(np.abs(rr[m])))]
    ts = np.array([x["time"] for x in C["s01"]])
    sig = at(ts, col(C["s01"], "h_K1_plus").real, t3, kind)
    nz = np.abs(col(C["jit0p3"], "h_K1_plus"))/np.abs(sig)
    out["nos"] = []
    for lo, hi in ((2, 20), (20, 80), (80, 140)):
        mm = (a3 >= lo) & (a3 <= hi) & np.isfinite(nz)
        out["nos"].append(float(np.max(nz[mm])))
    dev = {}
    for n, d, e in (("d01_e1", 0.01, 1.0), ("d01_e0p3", 0.01, 0.3), ("d0025_e1", 0.0025, 1.0),
                    ("d0025_e0p3", 0.0025, 0.3)):
        t = np.array([x["time"] for x in C[n]])
        a = a_of(t)
        dv = col(C[n], "h_K1_plus").real/(static(d, e)*g_of(t)) - 1
        dev[n] = (a, dv)
    out["win"] = []
    for n in ("d01_e1", "d01_e0p3", "d0025_e1", "d0025_e0p3"):
        a, dv = dev[n]
        bad = np.flatnonzero((a >= 2) & (np.abs(dv) > 5e-3))
        out["win"].append(float(a[bad[0] - 1]) if bad.size else float(a[-1]))
    for e in ("e1", "e0p3"):
        a1, v1 = dev[f"d01_{e}"]
        a2, v2 = dev[f"d0025_{e}"]
        out[f"R_{e}"] = []
        for a0 in (20, 30, 40, 60):
            m1 = (a1 >= 0.95*a0) & (a1 <= 1.05*a0)
            m2 = (a2 >= 0.95*a0) & (a2 <= 1.05*a0)
            out[f"R_{e}"].append(float(np.mean(v1[m1])/np.mean(v2[m2])))
    return out


def helper(nc, dc):
    P11, P14 = nc["P11"], dc["P14"]
    return {"jit0p3_K1": P11["jit0p3"]["K1_mod_ratio_3_20"], "jit0p1_K1": P11["jit0p1"]["K1_mod_ratio_3_20"],
            "jit0p3_K2": P11["jit0p3"]["K2_mod_ratio_3_20"], "jit0p1_K2": P11["jit0p1"]["K2_mod_ratio_3_20"],
            "amp": P11["ratio_K1_A03_A01_a1.5_20"],
            "nos": [P11[f"null03_over_signal01_K1_a{lo}_{hi}_max"] for lo, hi in
                    (("2.0", "20.0"), ("20.0", "80.0"), ("80.0", "140.0"))],
            "R_e1": [P14["R_e1"][f"R_a{a}"] for a in (20, 30, 40, 60)],
            "R_e0p3": [P14["R_e0p3"][f"R_a{a}"] for a in (20, 30, 40, 60)],
            "win": [P14[n]["window_a_dev_le_0p5pct"] for n in ("d01_e1", "d01_e0p3", "d0025_e1", "d0025_e0p3")]}


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    C = {k: rows(v) for k, v in CASES.items()}
    P = json.load(open(PRED))
    mine = reduce(C, P, "cubic")
    pch = reduce(C, P, "pchip")
    RTOL[0] = 1e-11
    loose = reduce(C, P, "cubic")
    RTOL[0] = 1e-12
    H = helper(json.load(open(NULL_CMP)), json.load(open(DELTA_CMP)))
    table, n = [], 0
    for k in H:
        for i, (x, y, z, w) in enumerate(zip(mine[k], H[k], LEDGER[k], pch[k])):
            n += 1
            table.append({"quantity": f"{k}[{i}]", "mine": x, "helper": y, "printed": z,
                          "rel_mine_helper": abs(x/y - 1), "rel_printed_helper": abs(z/y - 1),
                          "printed_digits_ok": f"{y:.3g}" == f"{z:.3g}" or abs(z/y - 1) < 5e-3,
                          "rel_pchip_helper": abs(w/y - 1),
                          "rel_mine_rtol1e-11_helper": abs(loose[k][i]/y - 1)})
    res = {"n_compared": n, "max_rel_mine_helper": max(r["rel_mine_helper"] for r in table),
           "max_rel_printed_helper": max(r["rel_printed_helper"] for r in table),
           "all_printed_digits_ok": all(r["printed_digits_ok"] for r in table),
           "max_rel_pchip_helper": max(r["rel_pchip_helper"] for r in table),
           "max_rel_mine_rtol1e-11_helper": max(r["rel_mine_rtol1e-11_helper"] for r in table),
           "rows": table}
    with open(os.path.join(out, "r2second_c18b.json"), "w") as f:
        json.dump(res, f, indent=1)
    for r in table:
        print(f"{r['quantity']:14s} mine {r['mine']:.12g} helper {r['helper']:.12g} printed {r['printed']} "
              f"rel {r['rel_mine_helper']:.2e} pchip {r['rel_pchip_helper']:.1e}")
    print({k: v for k, v in res.items() if k != "rows"})
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(fs.COLUMN_WIDTH*1.3, 2.8))
    x = np.arange(n)
    ax.semilogy(x, [max(r["rel_mine_helper"], 1e-17) for r in table], "o", ms=3,
                color=fs.PAL["blue"], label="own reduction vs comparison files")
    ax.semilogy(x, [max(r["rel_pchip_helper"], 1e-17) for r in table], "x", ms=3,
                color=fs.PAL["orange"], label="own, PCHIP interpolation")
    ax.semilogy(x, [max(r["rel_printed_helper"], 1e-17) for r in table], "s", ms=3, mfc="none",
                color=fs.PAL["red"], label="printed (3 digits) vs comparison files")
    ax.axhline(1.96e-12, **fs.THIN)
    ax.set_xlabel("compared number (lines 201-212)")
    ax.set_ylabel("relative difference")
    ax.legend(fontsize=6)
    ax.set_title("line 217 (black: 1.96e-12)", fontsize=8)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "r2second_c18b"))


if __name__ == "__main__":
    main()
