#!/usr/bin/env python3
"""V7: shearing dust. Series 7 (beta = 0.125, HL = 4, four particles per cell along y) and
L2 as run (beta = 0.5, HL = 4): Delta from the stored cos values, differences, order,
Richardson value; my own closed form of cos(theta_lin) (SPEC section 4, from draft.tex:262);
my own stream-crossing check from the particle snapshots (ordering in y of each initial
column of dust particles, periodic, unwrapped about the initial position).

    python3 v4_shear.py OUTDIR NAME=DIR ...
"""
import glob
import json
import os
import sys

import numpy as np
from scipy.integrate import quad

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vlib  # noqa: E402
import figstyle as fs  # noqa: E402


def cos_lin(b, HL, gauss=False):
    f = lambda x: np.cos(x)/(4*np.pi + HL*x)**3
    if gauss:   # second quadrature: 400-point Gauss-Legendre
        xg, wg = np.polynomial.legendre.leggauss(400)
        I = np.pi*np.sum(wg*f(np.pi*(xg + 1)))
    else:
        I = quad(f, 0, 2*np.pi, limit=200, epsabs=0, epsrel=1e-13)[0]
    return b*((HL + 6)/(HL + 2)**3 + (32*np.pi**2/HL)*I)


def crossing(dirn, ntrack, t_A):
    files = sorted(glob.glob(os.path.join(dirn, "*.part.*.bin")))
    s0 = vlib.read_snapshot(files[0])
    L = None
    ath = glob.glob(os.path.join(dirn, "*.athinput"))
    case = json.load(open(os.path.join(dirn, "case.json")))
    args = dict(a.split("=", 1) for a in case["athena_args"] if "=" in a and "/" in a.split("=", 1)[0])
    y0min, y0max = float(args["mesh/x2min"]), float(args["mesh/x2max"])
    L = y0max - y0min
    ny = int(args["mesh/nx2"])
    dust = s0["tag"] >= ntrack
    tags = s0["tag"][dust]
    x0 = s0["x"][dust]
    order_tag = np.argsort(tags)
    tags, x0 = tags[order_tag], x0[order_tag]
    # columns by initial (x, z)
    key = np.round(x0[:, 0], 6)*1e3 + np.round(x0[:, 2], 6)
    ukeys, col = np.unique(key, return_inverse=True)
    ppc_y = int(round(len(tags)/(len(ukeys)*ny)))
    dy0 = L/(ny*ppc_y)
    rows = []
    for fn in files:
        s = vlib.read_snapshot(fn)
        m = s["tag"] >= ntrack
        o = np.argsort(s["tag"][m])
        assert np.array_equal(s["tag"][m][o], tags)
        y = s["x"][m][o][:, 1]
        disp = np.mod(y - x0[:, 1] + L/2, L) - L/2
        yu = x0[:, 1] + disp
        mind = np.inf
        for c in range(len(ukeys)):
            sel = np.nonzero(col == c)[0]
            sel = sel[np.argsort(x0[sel, 1])]
            yy = yu[sel]
            d = np.diff(yy)
            dw = yy[0] + L - yy[-1]
            mind = min(mind, d.min(), dw)
        rows.append({"t": s["t"], "min_spacing_over_lattice": float(mind/dy0), "max_abs_disp_over_L": float(np.abs(disp).max()/L)})
    t = np.array([r["t"] for r in rows])
    ms = np.array([r["min_spacing_over_lattice"] for r in rows])
    cross = t[ms <= 0]
    before = t <= t_A
    return {"L": L, "ny": ny, "ppc_y": ppc_y, "n_columns": int(len(ukeys)), "lattice_dy": dy0,
            "first_crossing_snapshot_t": float(cross[0]) if len(cross) else None,
            "last_snapshot_t": float(t[-1]),
            "min_spacing_up_to_tA": float(ms[before].min()), "rows": rows}


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    res = {}
    for arg in sys.argv[2:]:
        name, d = arg.split("=", 1)
        r = json.load(open(os.path.join(d, "rays.json")))
        case = json.load(open(os.path.join(d, "case.json")))
        ntrack = int([a for a in case["athena_args"] if a.startswith("particles/traj_ntrack=")][0].split("=")[1])
        e = {"dir": d, "ny": r["ny"], "ppc_y": r["ppc_y"], "beta": r["beta"], "HL": r["HL"], "b": r["b"],
             "Delta_file": r["Delta"], "Delta_from_cos": r["cos"]/r["cos_lin"] - 1, "cos": r["cos"],
             "cos_lin_file": r["cos_lin"], "b_mine": r["beta"]*r["HL"]**2,
             "cos_lin_mine": cos_lin(r["beta"]*r["HL"]**2, r["HL"]),
             "cos_lin_mine_gauss": cos_lin(r["beta"]*r["HL"]**2, r["HL"], gauss=True),
             "t_A": r["t_A"], "t_B": r["t_B"]}
        e["cos_lin_rel_diff"] = e["cos_lin_mine"]/e["cos_lin_file"] - 1
        nsnap = len(glob.glob(os.path.join(d, "*.part.*.bin")))
        e["n_snapshots"] = nsnap
        e["crossing"] = crossing(d, ntrack, max(r["t_A"], r["t_B"])) if nsnap > 1 else None
        res[name] = e
        c = e["crossing"] or {}
        print(name, f"Delta {e['Delta_file']:.6f} ({e['Delta_from_cos']:.6f}) cos_lin {e['cos_lin_mine']:.15e} file {e['cos_lin_file']:.15e}",
              f"gauss {e['cos_lin_mine_gauss']:.15e} t_A {e['t_A']:.3f} snapshots {nsnap}",
              f"min spacing to t_A {c.get('min_spacing_up_to_tA')} first crossing {c.get('first_crossing_snapshot_t')}")
    # series: differences, order, Richardson
    for pre in ("N7", "L2"):
        ks = sorted([k for k in res if k.startswith(pre)], key=lambda k: res[k]["ny"])
        if len(ks) == 3:
            D = np.array([res[k]["Delta_file"] for k in ks])
            d1, d2 = D[1] - D[0], D[2] - D[1]
            q = d2/d1
            ser = {"names": ks, "Delta": D.tolist(), "d1": d1, "d2": d2, "ratio": q}
            if q > 0 and q < 1:
                p = np.log2(1/q)
                DR = D[2] + d2*q/(1 - q)
                ser.update({"order": p, "Richardson": DR, "finest_minus_R": D[2] - DR})
            ser["dist_to_cosmograph"] = (np.abs(D + 0.8183)).tolist()
            res["series_" + pre] = ser
            print(pre, ser)
    json.dump(res, open(os.path.join(out, "v4_shear.json"), "w"), indent=1)

    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(8, 3.2))
    fig.subplots_adjust(left=0.1, right=0.98, bottom=0.15, top=0.9, wspace=0.28)
    cols = fs.series_colors(3)
    for pre, ax, ttl in (("N7", axs[0], r"series 7: $\beta=0.125$, $HL=4$"),):
        ks = sorted([k for k in res if k.startswith(pre) and not k.startswith("series")], key=lambda k: res[k]["ny"])
        for c, k in zip(cols, ks):
            rr = res[k]["crossing"]["rows"]
            ax.plot([x["t"] for x in rr], [x["min_spacing_over_lattice"] for x in rr], color=c,
                    label=rf"$N_y={res[k]['ny']}$")
            ax.axvline(res[k]["t_A"], color=c, lw=1.0, ls=":")
        ax.axhline(0.0, **fs.GUIDE)
        ax.set_xlabel(r"$t$")
        ax.set_title(ttl, fontsize=10)
        ax.legend(frameon=False, fontsize=8, loc="lower left")
    axs[0].set_ylabel("smallest spacing / lattice spacing")
    # right: Delta against N_y for both series, L2 with CosmoGRaPH's value
    for pre, c, lab in (("N7", fs.PAL["red"], r"series 7 ($\beta=0.125$)"), ("L2", fs.PAL["yellow"], r"L2 ($\beta=0.5$), 4 per cell")):
        ser = res.get("series_" + pre)
        if not ser:
            continue
        ny = [res[k]["ny"] for k in ser["names"]]
        D = np.array(ser["Delta"])
        ref = -0.8183 if pre == "L2" else ser.get("Richardson", D[-1])
        axs[1].plot(ny, np.abs(D - ref), "o-", color=c, label=lab + (": |Delta + 0.8183|" if pre == "L2" else ": |Delta - Richardson|"))
    axs[1].set_xscale("log", base=2)
    axs[1].set_yscale("log")
    axs[1].set_xlabel(r"$N_y$")
    axs[1].set_title("distance of Delta from the reference", fontsize=10)
    axs[1].legend(frameon=False, fontsize=8, loc="center left")
    fs.save(fig, os.path.join(out, "v4_shear_crossing"))


if __name__ == "__main__":
    main()
