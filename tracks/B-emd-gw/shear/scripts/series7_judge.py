"""Judge shear series 7 (beta = 0.125, H L = 4, N_y = 64, 128, 256 at 4 per cell along y)
against predictions N7a-c (JOURNAL.md, 2026-11-26 14:25).

    python3 series7_judge.py --run RUNDIR [--cases N7_n64_ppc4,N7_n128_ppc4,N7_n256_ppc4]
                             [--out DIR]
Reads each case's rays.json (analyze_rays.py) and particle snapshots (crossing.py), writes
series7.json and series7.png into DIR ($NRPIC_RUN_DIR by default):
  - Delta per mesh, mesh differences, their ratio, the observed order and the Richardson
    extrapolation from the three meshes (N7b, N7c);
  - relative constraint means Hr, Mr averaged over 1 <= t <= t_A from the cstat series (N7b);
  - the smallest neighbour spacing along y per snapshot and the first crossing time (N7a).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import crossing as cx  # noqa: E402


def window_mean(series, key, t0, t1):
    t = np.asarray(series["t"], dtype=float)
    v = np.asarray(series[key], dtype=float)
    m = (t >= t0) & (t <= t1)
    return float(np.mean(v[m])) if m.any() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--cases", default="N7_n64_ppc4,N7_n128_ppc4,N7_n256_ppc4")
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    import glob
    rows = []
    for case in a.cases.split(","):
        cdir = os.path.join(a.run, case)
        with open(os.path.join(cdir, "rays.json")) as f:
            r = json.load(f)
        with open(os.path.join(cdir, "ic", "meta.json")) as f:
            meta = json.load(f)
        ts, smin = [], []
        for p in sorted(glob.glob(os.path.join(cdir, "*.part.*.bin"))):
            t, d, tag = cx.read_snapshot(p)
            ts.append(t)
            smin.append(cx.spacing(meta, d, tag)[0])
        tA = r["t_A"]
        first = next((t for t, s in zip(ts, smin) if s <= 0.0), None)
        before = [s for t, s in zip(ts, smin) if t <= tA]
        cs = r["cstat_series"]
        rows.append({"case": case, "ny": r["ny"], "Delta": r["Delta"],
                     "Delta_quad": r["Delta_quad"], "t_A": tA, "t_B": r["t_B"],
                     "Hr_mean_1_tA": window_mean(cs, "Hr_mean", 1.0, tA),
                     "Mr_mean_1_tA": window_mean(cs, "Mr_mean", 1.0, tA),
                     "cstat_max_to_arrival": r["cstat_max_to_arrival"],
                     "snap_t": ts, "s_min": smin, "t_first_crossing": first,
                     "s_min_to_tA": (min(before) if before else None),
                     "ray_kx_kz_drift": r["ray_kx_kz_drift"],
                     "tracer_ux_uz_drift": r["tracer_ux_uz_drift"]})
    rows.sort(key=lambda x: x["ny"])
    out = {"run": a.run, "rows": rows}
    if len(rows) == 3:
        d = [x["Delta"] for x in rows]
        d1, d2 = d[1] - d[0], d[2] - d[1]
        ratio = d2/d1 if d1 != 0 else None
        order = (np.log2(abs(d1/d2)) if d2 != 0 and d1 != 0 else None)
        rich = None
        if ratio is not None and abs(ratio) < 1.0 and ratio > 0:
            rich = d[2] + d2*ratio/(1.0 - ratio)
        out.update({"diff_64_128": d1, "diff_128_256": d2, "ratio": ratio,
                    "order": order, "Delta_extrap": rich,
                    "err_finest": (d[2] - rich if rich is not None else None),
                    "Hr_ratio_per_doubling": [rows[i]["Hr_mean_1_tA"]/rows[i + 1]["Hr_mean_1_tA"]
                                              for i in range(2)],
                    "Mr_ratio_per_doubling": [rows[i]["Mr_mean_1_tA"]/rows[i + 1]["Mr_mean_1_tA"]
                                              for i in range(2)]})
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "series7.json"), "w") as f:
        json.dump(out, f, indent=1)
    for x in rows:
        print("%s: Delta %.6f (quad %.6f) t_A %.3f  Hr %.3g Mr %.3g  s_min to t_A %.3f  "
              "first crossing %s" % (x["case"], x["Delta"], x["Delta_quad"], x["t_A"],
                                     x["Hr_mean_1_tA"], x["Mr_mean_1_tA"], x["s_min_to_tA"],
                                     x["t_first_crossing"]))
    for k in ("diff_64_128", "diff_128_256", "ratio", "order", "Delta_extrap", "err_finest",
              "Hr_ratio_per_doubling", "Mr_ratio_per_doubling"):
        if k in out:
            print(k, out[k])
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    try:
        import figstyle
        figstyle.use_style()
    except Exception:
        pass
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.4))
    ny = np.array([x["ny"] for x in rows], dtype=float)
    ax[0].plot(1.0/ny, [x["Delta"] for x in rows], "o-", ms=3, label=r"$\Delta$, 4 per cell")
    if out.get("Delta_extrap") is not None:
        ax[0].plot([0.0], [out["Delta_extrap"]], "s", ms=4, label="Richardson")
    ax[0].set_xlabel(r"$1/N_y$")
    ax[0].set_ylabel(r"$\Delta=\cos\vartheta/\cos\vartheta_{\rm lin}-1$")
    ax[0].set_xlim(left=0.0)
    ax[0].legend(fontsize=6)
    ax[0].set_title(r"(a) $\beta=0.125$, $H_*L=4$", fontsize=8)
    for x in rows:
        r = json.load(open(os.path.join(a.run, x["case"], "rays.json")))["cstat_series"]
        ax[1].semilogy(r["t"], np.maximum(r["Hr_mean"], 1e-12), lw=0.8, label="Hr %d" % x["ny"])
        ax[1].semilogy(r["t"], np.maximum(r["Mr_mean"], 1e-12), lw=0.8, ls="--",
                       label="Mr %d" % x["ny"])
    ax[1].axvline(rows[-1]["t_A"], color="0.5", lw=0.6, ls=":")
    ax[1].set_xlabel("code time t")
    ax[1].set_ylabel("relative constraint mean")
    ax[1].legend(fontsize=5, ncol=2)
    ax[1].set_title("(b) constraints; dotted: t_A", fontsize=8)
    for x in rows:
        ax[2].plot(x["snap_t"], x["s_min"], "o-", ms=2, lw=0.8, label="N_y = %d" % x["ny"])
    ax[2].axhline(0.0, color="k", lw=0.6)
    ax[2].axvline(rows[-1]["t_A"], color="0.5", lw=0.6, ls=":")
    ax[2].set_xlabel("code time t")
    ax[2].set_ylabel(r"min spacing / $\Delta q_y$")
    ax[2].legend(fontsize=6)
    ax[2].set_title("(c) stream crossing at 0", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "series7.png"), dpi=200)


if __name__ == "__main__":
    main()
