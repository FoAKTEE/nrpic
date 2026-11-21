"""Lead's wave-3 recheck L17-L20 of the decisive and drift packages (C-sidm, batch 2b).

Own code, independent of decisive/scripts/analyze_decisive.py and drift/scripts/*.py: reads
the NRPIC history `cc.nrpic.hst` of every cluster run by its header names, takes
t_c = first linear crossing of alpha_min = 0.3, and fits each collisionless control with
y = alpha_probe - alpha_probe(0) = A (1 - cos 2 pi t / P) + c by a grid in P followed by a
linear least-squares solve for (A, c) at each P (no shared starting guess with the helpers).
Predictions: tracks/C-sidm/JOURNAL.md 2026-11-21T07:51Z (L17-L20).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"

RUNS = {
    # name: directory (run id / case)
    "cc1_kninf": "C-20261115-171058-c26cfad/cc1_kninf",
    "cc2_kninf": "C-20261115-171059-4b70228/cc2_kninf",
    "d3_kninf": "C-20261121-035737-295e5c3/d3_kninf",
    "cc2_kninf_M8": "C-20261120-222533-ce50a86/cc2_kninf_M8",
    "cc1_kn10_cell_s1": "C-20261115-171059-4b70228/cc1_kn10",
    "cc1_kn10_cell_s2": "C-20261121-062408-49fa14a/cc1_kn10_cell_s2",
    "cc1_kn10_cell_s3": "C-20261121-062408-49fa14a/cc1_kn10_cell_s3",
    "cc1_kn10_part_s1": "C-20261121-025633-bb8dac4/cc1_kn10_part_s1",
    "cc1_kn10_part_s2": "C-20261121-025633-bb8dac4/cc1_kn10_part_s2",
    "cc2_kn10_cell_s1": "C-20261115-171059-35441e3/cc2_kn10",
    "cc2_kn10_cell_s2": "C-20261121-052716-6b64f97/cc2_kn10_cell_s2",
    "cc2_kn10_part_s1": "C-20261120-221846-797bdbe/cc2_kn10_part_s1",
    "cc2_kn10_part_s2": "C-20261120-221846-797bdbe/cc2_kn10_part_s2",
    "cc1_kn1_cell_s1": "C-20261115-171058-c26cfad/cc1_kn1",
    "cc2_kn1_cell_s1": "C-20261115-171059-35441e3/cc2_kn1",
    "d3_kn1_part_s1": "C-20261121-035737-295e5c3/d3_kn1_part_s1",
    "d3_kn10_part_s1": "C-20261121-052716-6b64f97/d3_kn10_part_s1",
}
HELPER_SUMMARY = os.path.join(SCR, "C-20261121-075202-1a37fb9", "summary.json")


def read_hst(path):
    names = None
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#"):
                if "[1]=" in line:
                    names = [tok.split("=", 1)[1] for tok in line[1:].split() if "=" in tok]
                continue
            rows.append([float(x) for x in line.split()])
    a = np.array(rows)
    return {n: a[:, i] for i, n in enumerate(names)}


def first_crossing(t, y, level):
    below = np.flatnonzero(y < level)
    if below.size == 0:
        return None
    i = below[0]
    if i == 0:
        return float(t[0])
    t0, t1, y0, y1 = t[i - 1], t[i], y[i - 1], y[i]
    return float(t0 + (level - y0) * (t1 - t0) / (y1 - y0))


def cos_fit(t, y, pgrid=np.arange(100.0, 1500.0, 0.25)):
    best = None
    for P in pgrid:
        X = np.column_stack([1.0 - np.cos(2.0 * math.pi * t / P), np.ones_like(t)])
        coef, res, *_ = np.linalg.lstsq(X, y, rcond=None)
        r = y - X @ coef
        s = float(np.sum(r * r))
        if best is None or s < best[0]:
            best = (s, P, coef[0], coef[1])
    s, P, A, c = best
    return dict(P=float(P), A=float(A), c=float(c), rms=math.sqrt(s / len(t)))


def main():
    out = os.environ.get("NRPIC_RUN_DIR") or os.path.join(SCR, "tmp", "review_wave3")
    os.makedirs(out, exist_ok=True)
    helper = json.load(open(HELPER_SUMMARY))["runs"]
    res = {}
    H = {}
    for name, rel in RUNS.items():
        h = read_hst(os.path.join(SCR, rel, "cc.nrpic.hst"))
        H[name] = h
        t, am, ap = h["time"], h["alpha_min"], h["alpha_probe"]
        ok = np.isfinite(am) & (am < 1e300)
        r = dict(t_end=float(t[-1]), np_first=int(h["np"][0]), np_min_before_tc=None,
                 t_c=first_crossing(t[ok], am[ok], 0.3))
        tc = r["t_c"] if r["t_c"] is not None else t[-1] + 1
        pre = t < min(tc, t[-1] + 1)
        r["np_min_before_tc"] = int(h["np"][pre].min())
        r["sum_m_bit_identical_before_tc"] = bool(np.all(h["sum_m"][pre] == h["sum_m"][0]))
        hv = helper.get(name, {})
        r["helper_t_c_interp"] = hv.get("t_c_interp")
        if r["t_c"] is not None and hv.get("t_c_interp") is not None:
            r["t_c_minus_helper"] = r["t_c"] - hv["t_c_interp"]
        if name.endswith("kninf") or name.endswith("_M8"):
            w = (t <= 300.0 + 1e-9) & np.isfinite(ap)
            r["fit_0_300"] = cos_fit(t[w], ap[w] - ap[0])
            r["alpha_probe0"] = float(ap[0])
            r["max_excursion"] = float(np.max(ap[w] - ap[0]))
            r["t_max_excursion"] = float(t[w][np.argmax(ap[w] - ap[0])])
            if "H_norm2" in h:
                late = (t >= 100) & (t <= 300)
                r["H_norm2_late_mean"] = float(np.mean(h["H_norm2"][late]))
        res[name] = r

    # L17: mode effect of CC1 at Kn = 10, decision rule of decisive/JOURNAL.md entry 10
    cell = np.array([res[f"cc1_kn10_cell_s{i}"]["t_c"] for i in (1, 2, 3)])
    part = np.array([res[f"cc1_kn10_part_s{i}"]["t_c"] for i in (1, 2)])
    sig = math.sqrt(cell.var(ddof=1) / 3 + part.var(ddof=1) / 2)
    l17 = dict(cell=cell.tolist(), part=part.tolist(), mean_cell=float(cell.mean()),
               mean_part=float(part.mean()), sd_cell=float(cell.std(ddof=1)),
               sd_part=float(part.std(ddof=1)), diff=float(part.mean() - cell.mean()),
               sigma_rule=sig, ratio=float((part.mean() - cell.mean()) / sig))
    cc2c = np.array([res[f"cc2_kn10_cell_s{i}"]["t_c"] for i in (1, 2)])
    cc2p = np.array([res[f"cc2_kn10_part_s{i}"]["t_c"] for i in (1, 2)])
    l17["cc2"] = dict(cell=cc2c.tolist(), part=cc2p.tolist(),
                      sd_all=float(np.concatenate([cc2c, cc2p]).std(ddof=1)))
    l17["cc1_all_sd"] = float(np.concatenate([cell, part]).std(ddof=1))
    # L19: amplitude ratio of the M/8 control
    a4 = res["cc2_kninf"]["fit_0_300"]
    a8 = res["cc2_kninf_M8"]["fit_0_300"]
    l19 = dict(R=a8["A"] / a4["A"], P_M8=a8["P"], P_M4=a4["P"],
               R_max=res["cc2_kninf_M8"]["max_excursion"] / res["cc2_kninf"]["max_excursion"])
    summary = dict(runs=res, L17=l17, L19=l19)
    with open(os.path.join(out, "rv_clusters.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(dict(L17=l17, L19=l19), indent=1))
    for n, r in res.items():
        print(n, "t_c", r["t_c"], "helper", r["helper_t_c_interp"], "fit", r.get("fit_0_300"))
    figure(H, res, l17, out)


def figure(H, res, l17, out):
    sys.path.insert(0, os.path.join(WT, "python"))
    from nrpic import figstyle as fs
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fs.use_style()
    fig, axs = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.5, 3.6))
    # (a) controls and fits
    ax = axs[0]
    cols = fs.SERIES
    for k, name in enumerate(["cc1_kninf", "cc2_kninf", "cc2_kninf_M8", "d3_kninf"]):
        h = H[name]
        t, ap = h["time"], h["alpha_probe"]
        w = t <= 300
        ax.plot(t[w], ap[w] - ap[0], color=cols[k], lw=1.0, label=name.replace("_", r"\_"))
        f = res[name]["fit_0_300"]
        ax.plot(t[w], f["A"] * (1 - np.cos(2 * np.pi * t[w] / f["P"])) + f["c"], color=cols[k],
                lw=1.5, ls="--")
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\alpha_c - \alpha_c(0)$")
    ax.set_title("collisionless controls, cosine fits (dashed)")
    ax.legend(frameon=False, fontsize=8)
    # (b) CC1 at Kn = 10, alpha_min
    ax = axs[1]
    for k, name in enumerate(["cc1_kn10_cell_s1", "cc1_kn10_cell_s2", "cc1_kn10_cell_s3",
                              "cc1_kn10_part_s1", "cc1_kn10_part_s2"]):
        h = H[name]
        ok = np.isfinite(h["alpha_min"]) & (h["alpha_min"] < 1e300)
        ls = "-" if "cell" in name else ":"
        ax.plot(h["time"][ok], h["alpha_min"][ok], color=cols[k], ls=ls, lw=1.2,
                label=name.replace("cc1_kn10_", "").replace("_", " "))
    ax.axhline(0.3, **fs.GUIDE)
    ax.set_xlim(140, 200)
    ax.set_ylim(0.0, 0.7)
    ax.set_xlabel(r"$t/M$")
    ax.set_ylabel(r"$\alpha_{\min}$")
    ax.set_title(r"CC1, Kn = 10: run-up to $\alpha_{\min}=0.3$")
    ax.legend(frameon=False, fontsize=8)
    # (c) t_c per group
    ax = axs[2]
    groups = [("CC1 cell", [res[f"cc1_kn10_cell_s{i}"]["t_c"] for i in (1, 2, 3)]),
              ("CC1 part", [res[f"cc1_kn10_part_s{i}"]["t_c"] for i in (1, 2)]),
              ("CC2 cell", [res[f"cc2_kn10_cell_s{i}"]["t_c"] for i in (1, 2)]),
              ("CC2 part", [res[f"cc2_kn10_part_s{i}"]["t_c"] for i in (1, 2)])]
    for k, (g, v) in enumerate(groups):
        ax.plot([k] * len(v), v, "o", color=cols[k % len(cols)], ms=6)
        ax.plot([k - 0.2, k + 0.2], [np.mean(v)] * 2, **fs.REF_LINE)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([g for g, _ in groups])
    ax.set_ylabel(r"$t_c/M$ ($\alpha_{\min}=0.3$)")
    ax.set_title("collapse time by seed, Kn = 10")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "rv_clusters"))


if __name__ == "__main__":
    main()
