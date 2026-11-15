"""P8: read BKRS (arXiv:1804.02911) fig. 2 (dis_with_D.eps, MATLAB R2015b EPS read as text)
and test hypothesis H1 on SKR's retrograde curve.

(i) Curves of BKRS fig. 2: isotropic (black solid), coplanar prograde (blue dashed),
    coplanar retrograde (red dot-dashed) (caption mnras.tex:403). Calibration from the
    file: major x ticks at 148.568 (D = 1e-4), 270.618, 392.668, 514.718, 636.767 (D = 1);
    y: P = 0 at 513, P = 1 at 43 (axes box), checked against the plateau value.
(ii) H1: count my coplanar survivors with final semi-major axis > X a as disrupted and
    compare with SKR fig. 4 (from the P7 run's digitised file) for X in 1.5 .. 6.

Run: python3 scripts/digitize_bkrs.py <coplanar_run> <deep_supplement_run> <general_run> <p7_run>
"""
import json
import os
import re
import shutil
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

EPS = "/data/haiyangw/nrpic/kb-data/raw/arxiv/1804.02911/v1/src/dis_with_D.eps"
NUM = re.compile(r"^-?\d+(\.\d+)?$")


def polylines(path):
    rgb, dash = (0.0, 0.0, 0.0), "[]"
    out, stack, cur = [], [], []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("%") or len(line) > 400:
                continue
            m = re.search(r"\[([^\]]*)\]\s+\S+\s+setdash", line)
            if m:
                dash = "[" + m.group(1).strip() + "]"
            for tok in re.sub(r"\[[^\]]*\]", " ", line).split():
                if NUM.match(tok):
                    stack.append(float(tok))
                elif tok == "RC" and len(stack) >= 3:
                    rgb = tuple(stack[-3:])
                    stack.clear()
                elif tok == "GC" and stack:
                    g = stack.pop()
                    rgb = (g, g, g)
                    stack.clear()
                elif tok == "M" and len(stack) >= 2:
                    cur = [stack[-2:]]
                    stack.clear()
                elif tok == "L" and len(stack) >= 2:
                    cur.append(stack[-2:])
                    stack.clear()
                elif tok == "S":
                    if len(cur) > 20:
                        out.append((rgb, dash, np.array(cur)))
                    cur = []
                    stack.clear()
                else:
                    stack.clear()
    return out


def coplanar_arrays(cop, sup):
    Z = np.load(os.path.join(runlib.SCRATCH, cop, "coplanar.npz"))
    keep = Z["D"] >= 1e-3 * (1 - 1e-9)
    D = Z["D"][keep]
    A = {k: np.asarray(Z[k])[keep] for k in Z.files if k.rsplit("_", 1)[-1] in ("pro", "ret")}
    Y = np.load(os.path.join(runlib.SCRATCH, sup, "coplanar.npz"))
    D = np.concatenate([Y["D"], D])
    A = {k: np.concatenate([Y[k], v]) for k, v in A.items()}
    o = np.argsort(D)
    return D[o], {k: v[o] for k, v in A.items()}


def main():
    cop, sup, gen, p7 = sys.argv[1:5]
    inputs = [EPS, os.path.join(runlib.SCRATCH, cop, "coplanar.npz"),
              os.path.join(runlib.SCRATCH, sup, "coplanar.npz"),
              os.path.join(runlib.SCRATCH, gen, "general.npz"),
              os.path.join(runlib.SCRATCH, p7, "skr_digitised.json")]
    run = runlib.start_run("P8: BKRS fig. 2 curves against this work; hypothesis H1 on SKR's "
                           "retrograde disruption criterion", extra_inputs=inputs,
                           preregistered="tracks/F-hills/newton3/JOURNAL.md#P8")
    curves = {}
    for rgb, dash, pts in polylines(EPS):
        D = 10 ** (-4 + (pts[:, 0] - 148.568) / 122.05)
        P = (513.0 - pts[:, 1]) / 470.0
        key = f"rgb{tuple(round(c, 3) for c in rgb)}|{dash}"
        curves.setdefault(key, [])
        curves[key].append((D, P))
    with open(os.path.join(run["dir"], "bkrs_fig2_digitised.json"), "w") as fh:
        json.dump({k: [[d.tolist(), p.tolist()] for d, p in v] for k, v in curves.items()}, fh)
    print({k: [len(d) for d, p in v] for k, v in curves.items()})

    D, A = coplanar_arrays(cop, sup)
    mine = {}
    for tag in ("pro", "ret"):
        ok, dis = A[f"ok_{tag}"], A[f"disrupted_{tag}"]
        mine[tag] = np.array([dis[i][ok[i]].mean() for i in range(D.size)])
    G = np.load(inputs[3])
    kA = G["D_A"] >= 1e-3 * (1 - 1e-9)
    Dg = G["D_A"][kA]
    Pg = np.array([G["disrupted_A"][kA][i][G["ok_A"][kA][i]].mean() for i in range(Dg.size)])

    def longest(key):
        segs = curves[key]
        d = np.concatenate([s[0] for s in segs])
        p = np.concatenate([s[1] for s in segs])
        o = np.argsort(d)
        return d[o], p[o]

    keys = list(curves)
    k_iso = [k for k in keys if k.startswith("rgb(0.149, 0.149, 0.149)")][0]  # dark grey
    k_pro = [k for k in keys if k.startswith("rgb(0.0, 0.0, 1.0)")][0]
    k_ret = [k for k in keys if k.startswith("rgb(1.0, 0.0, 0.0)")][0]
    S = {"curve_keys": {"iso": k_iso, "pro": k_pro, "ret": k_ret}}
    for lab, k, Dm, Pm in (("iso", k_iso, Dg, Pg), ("pro", k_pro, D, mine["pro"]),
                           ("ret", k_ret, D, mine["ret"])):
        d, p = longest(k)
        sel = (d >= Dm.min()) & (d <= Dm.max())
        dv = np.interp(np.log(d[sel]), np.log(Dm), Pm) - p[sel]
        S[f"BKRS_{lab}"] = {"median_abs_diff": float(np.median(np.abs(dv))),
                            "max_abs_diff_D<0.3": float(np.max(np.abs(dv[d[sel] < 0.3]))),
                            "max_abs_diff": float(np.max(np.abs(dv))),
                            "BKRS_last_D_with_P>0.002": float(d[p > 0.002].max())}

    # (ii) H1 against SKR fig. 4
    dig = json.load(open(inputs[4]))
    skr = {}
    for tag, rgb in (("pro", "(1.0, 0.0, 0.0)"), ("ret", "(0.0, 0.0, 1.0)")):
        k = f"fig4|panel335|rgb{rgb}|SO"
        o = np.argsort(dig[k]["D"])
        skr[tag] = (np.array(dig[k]["D"])[o], np.array(dig[k]["v"])[o])
    Xs = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]
    S["H1"] = {}
    alt = {}
    for X in Xs:
        row = {}
        for tag in ("pro", "ret"):
            ok, dis, sv, af = (A[f"ok_{tag}"], A[f"disrupted_{tag}"], A[f"survived_{tag}"],
                               A[f"af_{tag}"])
            Palt = np.array([(dis[i] | (sv[i] & (af[i] > X)))[ok[i]].mean() for i in range(D.size)])
            alt[(X, tag)] = Palt
            d, p = skr[tag]
            sel = (d >= 1e-3) & (d <= 0.6 if tag == "ret" else d <= 3.0)
            dv = np.interp(np.log(d[sel]), np.log(D), Palt) - p[sel]
            row[tag] = {"max_abs_diff": float(np.max(np.abs(dv))),
                        "median_abs_diff": float(np.median(np.abs(dv))),
                        "max_abs_diff_D<0.3": float(np.max(np.abs(dv[d[sel] < 0.3])))}
            if tag == "ret":
                row[tag]["last_D_disrupting"] = float(D[Palt > 0].max())
        S["H1"][f"X={X:g}"] = row
    with open(os.path.join(run["dir"], "summary_bkrs_h1.json"), "w") as fh:
        json.dump(S, fh, indent=2)
    with open(os.path.join(PKG, "results", "bkrs_h1.json"), "w") as fh:
        json.dump(S, fh, indent=2)
    print(json.dumps(S, indent=1))

    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.4))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.93, wspace=0.25)
    ax = axs[0]
    for lab, k, Dm, Pm, ls in (("isotropic", k_iso, Dg, Pg, "-"), ("prograde", k_pro, D, mine["pro"], "--"),
                               ("retrograde", k_ret, D, mine["ret"], "-.")):
        d, p = longest(k)
        ax.plot(d, p, color=fs.PAL["blue"], ls=ls, lw=2.2, alpha=0.55, label=f"BKRS, {lab}")
        ax.plot(Dm, Pm, color=fs.PAL["red"], ls=ls, lw=1.0, label=f"this work, {lab}")
    ax.set_xscale("log")
    ax.set_xlim(1e-3, 3)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel(r"$D$")
    ax.set_ylabel(r"$P_{\rm dis}$")
    ax.set_title("BKRS fig. 2 (read from the EPS)", fontsize=10)
    ax.legend(fontsize=6.5, loc="lower left", ncol=1)
    ax = axs[1]
    d, p = skr["ret"]
    ax.plot(d, p, color=fs.PAL["blue"], lw=2.2, alpha=0.55, label="SKR fig. 4, retrograde")
    ax.plot(D, mine["ret"], color=fs.PAL["red"], lw=1.0, label="this work (bound = survived)")
    best = min(Xs, key=lambda X: S["H1"][f"X={X:g}"]["ret"]["max_abs_diff"])
    ax.plot(D, alt[(best, "ret")], color="k", ls="--", lw=1.0,
            label=f"this work, survivors with $a_f > {best:g}a$ counted as disrupted")
    ax.set_xscale("log")
    ax.set_xlim(1e-3, 1)
    ax.set_ylim(0, 0.85)
    ax.set_xlabel(r"$D$")
    ax.set_title("H1: SKR's retrograde curve", fontsize=10)
    ax.legend(fontsize=7, loc="lower left")
    files = fs.save(fig, os.path.join(run["dir"], "fig_bkrs_and_h1"))
    for f in files:
        shutil.copy(f, os.path.join(PKG, "figures"))
    S["H1_best_X"] = best
    runlib.finish_run(run, results={"BKRS": {k: S[k] for k in S if k.startswith("BKRS")},
                                    "H1_best_X": best, "H1_best": S["H1"][f"X={best:g}"]})


if __name__ == "__main__":
    main()
