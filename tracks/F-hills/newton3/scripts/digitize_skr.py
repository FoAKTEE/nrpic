"""P7: read the curves of SKR (arXiv:0911.1136) figures 4 and 7 from the MATLAB EPS files in
kb-data (read as text, nothing in them is executed) and compare with the coplanar scan.

The EPS files draw each curve as one or more 'x0 y0 n MP stroke' polylines (relative
moves listed in reverse order; MP is defined in the files' prolog as
'3 1 roll moveto 1 sub {rlineto} repeat'). Axis calibration from the tick marks of each
figure (read by eye from the files, listed below). The digitised values are written to
the run directory only (third-party data are not committed); the comparison figure and the
deviation numbers are committed.

Run: python3 -I scripts/digitize_skr.py <coplanar_run_id> [<deep_supplement_run_id>]
"""
import json
import os
import re
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(sys.argv[0]))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PKG, "..", "..", "..", "python"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from nrpic import figstyle as fs  # noqa: E402
import runlib  # noqa: E402

SRC = "/data/haiyangw/nrpic/kb-data/raw/arxiv/0911.1136/v1/src/figs"
# calibration (EPS units): fig4 x: log10 D = -3 at 1292, 0 at 4539; y: P = 0 at 3990, 1 at 944
# fig7 x: log10 D = -3 at 1599, 0 at 5619; top panel y: E = 0 at 3776, 2 at 680;
#      bottom panel y: log10 E = 0 at 7265, 1 at 5718
CAL = {
    "fig4": {"x": (1292, -3.0, 4539, 0.0), "panels": [((335, 3990), (3990, 0.0, 944, 1.0), False)]},
    "fig7": {"x": (1599, -3.0, 5619, 0.0),
             "panels": [((680, 3776), (3776, 0.0, 680, 2.0), False),
                        ((4980, 8075), (7265, 0.0, 5718, 1.0), True)]},
}
NUM = re.compile(r"^-?\d+(\.\d+)?$")


def polylines(path):
    """List of (rgb, dash, points (n, 2)) for every MP stroke with more than 5 points."""
    colors = {}
    cur_rgb, cur_dash = (0.0, 0.0, 0.0), "SO"
    stack = []
    out = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("%"):
                continue
            m = re.match(r"^/(c\d+) \{ ([\d.]+) ([\d.]+) ([\d.]+) sr\} bdef", line.strip())
            if m:
                colors[m.group(1)] = tuple(float(m.group(i)) for i in (2, 3, 4))
                continue
            for tok in line.split():
                if NUM.match(tok):
                    stack.append(float(tok))
                    continue
                if tok in colors:
                    cur_rgb = colors[tok]
                elif tok == "sg" and stack:
                    g = stack.pop()
                    cur_rgb = (g, g, g)
                elif tok in ("SO", "DA", "DO", "DD"):
                    cur_dash = tok
                elif tok == "MP" and len(stack) >= 3:
                    n = int(stack.pop())
                    y0 = stack.pop()
                    x0 = stack.pop()
                    k = 2 * (n - 1)
                    rel = np.array(stack[len(stack) - k:]).reshape(-1, 2)[::-1] if k else np.zeros((0, 2))
                    del stack[len(stack) - k:]
                    pts = np.vstack([[x0, y0], [x0, y0] + np.cumsum(rel, axis=0)])
                    if n > 5:
                        out.append((cur_rgb, cur_dash, pts))
                else:
                    stack.clear()
    return out


def to_data(fig, pts):
    xa, ua, xb, ub = CAL[fig]["x"]
    lx = ua + (pts[:, 0] - xa) * (ub - ua) / (xb - xa)
    ymid = np.median(pts[:, 1])
    for (lo, hi), (ya, va, yb, vb), logy in CAL[fig]["panels"]:
        if lo - 50 <= ymid <= hi + 50:
            v = va + (pts[:, 1] - ya) * (vb - va) / (yb - ya)
            return 10 ** lx, (10 ** v if logy else v), (lo, hi)
    return None


def main():
    cop = sys.argv[1]
    sup = sys.argv[2] if len(sys.argv) > 2 else None
    srcs = [os.path.join(SRC, "fig4.eps"), os.path.join(SRC, "fig7.eps"),
            os.path.join(runlib.SCRATCH, cop, "coplanar.npz")]
    if sup:
        srcs.append(os.path.join(runlib.SCRATCH, sup, "coplanar.npz"))
    run = runlib.start_run("P7: digitise SKR figs. 4 and 7 (MATLAB EPS in kb-data) and compare with "
                           "the coplanar scan", extra_inputs=srcs,
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P7")
    dig = {}
    for fig in ("fig4", "fig7"):
        for rgb, dash, pts in polylines(os.path.join(SRC, f"{fig}.eps")):
            r = to_data(fig, pts)
            if r is None:
                continue
            D, v, panel = r
            key = f"{fig}|panel{panel[0]}|rgb{rgb}|{dash}"
            dig.setdefault(key, {"D": [], "v": []})
            dig[key]["D"] += D.tolist()
            dig[key]["v"] += v.tolist()
    with open(os.path.join(run["dir"], "skr_digitised.json"), "w") as fh:
        json.dump(dig, fh)
    print("\n".join(f"{k}: {len(v['D'])} points, D {min(v['D']):.3g}..{max(v['D']):.3g}" for k, v in dig.items()))

    # ---- this work
    Z = np.load(srcs[2])
    keep = Z["D"] >= 1e-3 * (1 - 1e-9)
    D = Z["D"][keep]
    mine = {}
    arrays = {k: np.asarray(Z[k])[keep] for k in Z.files if k.rsplit("_", 1)[-1] in ("pro", "ret")}
    if sup:
        Y = np.load(srcs[3])
        D = np.concatenate([Y["D"], D])
        arrays = {k: np.concatenate([Y[k], v]) for k, v in arrays.items()}
        o = np.argsort(D)
        D = D[o]
        arrays = {k: v[o] for k, v in arrays.items()}
    for tag in ("pro", "ret"):
        ok, dis, E = arrays[f"ok_{tag}"], arrays[f"disrupted_{tag}"], arrays[f"E2_{tag}"]
        mine[tag] = {
            "P": np.array([dis[i][ok[i]].mean() for i in range(D.size)]),
            "Em": np.array([np.abs(E[i][dis[i] & ok[i]]).mean() if (dis[i] & ok[i]).any() else np.nan
                            for i in range(D.size)]),
            "Ex": np.array([np.abs(E[i][dis[i] & ok[i]]).max() if (dis[i] & ok[i]).any() else np.nan
                            for i in range(D.size)])}

    def pick(fig, panel, rgb, dash):
        k = f"{fig}|panel{panel}|rgb{rgb}|{dash}"
        d = dig[k]
        o = np.argsort(d["D"])
        return np.array(d["D"])[o], np.array(d["v"])[o]

    RED, BLUEC, BLACK = (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, 0.0)
    ref = {"P_pro": pick("fig4", 335, RED, "SO"), "P_ret": pick("fig4", 335, BLUEC, "SO"),
           "Em_pro": pick("fig7", 680, RED, "SO"), "Em_ret": pick("fig7", 680, RED, "DA"),
           "Ex_pro": pick("fig7", 4980, RED, "SO"), "Ex_ret": pick("fig7", 4980, RED, "DA")}
    S = {"coplanar_run": cop, "supplement_run": sup, "digitised_from": SRC + "/fig4.eps, fig7.eps"}
    for q in ("P", "Em", "Ex"):
        for tag in ("pro", "ret"):
            Dr, vr = ref[f"{q}_{tag}"]
            sel = (Dr >= D.min()) & (Dr <= D.max())
            vm = np.interp(np.log(Dr[sel]), np.log(D), mine[tag][q])
            dv = vm - vr[sel]
            if q == "P":
                S[f"{q}_{tag}"] = {"max_abs_diff": float(np.nanmax(np.abs(dv))),
                                   "median_abs_diff": float(np.nanmedian(np.abs(dv))),
                                   "D_of_max": float(Dr[sel][np.nanargmax(np.abs(dv))]),
                                   "max_abs_diff_D<0.3": float(np.nanmax(np.abs(dv[Dr[sel] < 0.3])))}
                last = Dr[vr > 0.002].max() if np.any(vr > 0.002) else None
                S[f"{q}_{tag}"]["SKR_curve_last_D_with_P>0.002"] = float(last) if last else None
            else:
                good = np.isfinite(vm) & (vr[sel] > 0.05)
                rel = dv[good] / vr[sel][good]
                S[f"{q}_{tag}"] = {"median_rel_diff": float(np.median(np.abs(rel))),
                                   "p90_rel_diff": float(np.percentile(np.abs(rel), 90))}
    with open(os.path.join(run["dir"], "summary_skr_curves.json"), "w") as fh:
        json.dump(S, fh, indent=2)
    os.makedirs(os.path.join(PKG, "results"), exist_ok=True)
    with open(os.path.join(PKG, "results", "skr_curves.json"), "w") as fh:
        json.dump(S, fh, indent=2)
    print(json.dumps(S, indent=1))

    # ---- figure
    fs.use_style()
    fig, axs = plt.subplots(3, 1, figsize=(fs.COLUMN_WIDTH * 1.25, 7.0), sharex=True)
    fig.subplots_adjust(left=0.16, right=0.97, bottom=0.07, top=0.98, hspace=0.06)
    for ax, q, ylab in ((axs[0], "P", r"$P_{\rm dis}$"), (axs[1], "Em", r"$\langle|E|\rangle$"),
                        (axs[2], "Ex", r"$\max|E|$")):
        for tag, ls in (("pro", "-"), ("ret", "--")):
            Dr, vr = ref[f"{q}_{tag}"]
            ax.plot(Dr, vr, color=fs.PAL["blue"], ls=ls, lw=2.2, alpha=0.6,
                    label=f"SKR fig. {'4' if q == 'P' else '7'}, {tag}grade")
            ax.plot(D, mine[tag][q], color=fs.PAL["red"], ls=ls, lw=1.0, label=f"this work, {tag}grade")
        ax.set_ylabel(ylab)
    axs[0].legend(fontsize=7.5, loc="lower left")
    axs[2].set_yscale("log")
    axs[2].set_xscale("log")
    axs[2].set_xlim(1e-3, 3)
    axs[2].set_xlabel(r"$D = r_p / r_t$", labelpad=-1)
    files = fs.save(fig, os.path.join(run["dir"], "fig_skr_curves"))
    import shutil
    for f in files:
        shutil.copy(f, os.path.join(PKG, "figures"))
    runlib.finish_run(run, results=S)


if __name__ == "__main__":
    main()
