"""T3 of tracks/A-emd-pbh/gauge/JOURNAL.md: constraint growth of the shift-driver run of the
cosmology extension against its zero-shift twin, with the time-step limit of T2.

    python3 -I bh2_onset.py --vn OUT_T2/vonneumann.json --out OUTDIR \
        [--runs /data/haiyangw/nrpic/runs/cosmo]

Reads (read only) <runs>/east_d0.05_n64_bh1/east.{cstat,nrpic}.hst and the same of
east_d0.05_n64_bh2. Columns: cstat [1] time, [8] Theta_max, [9] H_max, [11] Hr_max,
[13] M_max; nrpic [1] time, [16] alpha_min, [30] alpha_max. Non-finite records (the
end of bh2) are dropped. Prints the first record at which Hr_max and Theta_max of bh2
exceed twice those of bh1, the largest lapse at that time, and the lapse at which T2
puts the limit (cfl 0.25). Figure OUTDIR/bh2_onset.{png,pdf}, numbers OUTDIR/bh2_onset.json.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "python"))
from nrpic.figstyle import use_style, SERIES, GUIDE, MASK_LINE, FULL_WIDTH  # noqa: E402


def load(path, cols):
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            v = line.split()
            try:
                rows.append([float(v[c - 1]) for c in cols])
            except (ValueError, IndexError):
                continue
    a = np.array(rows)
    ok = np.all(np.isfinite(a) & (np.abs(a) < 1e300), axis=1)
    return a[ok]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vn", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--runs", default="/data/haiyangw/nrpic/runs/cosmo")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    with open(args.vn) as f:
        vn = json.load(f)
    C = vn["bh2"]["cfl_number"]
    a_crit = vn["bh2"]["a_crit"]
    t_crit = vn["bh2"]["t_crit"]
    d = {}
    for tag in ("bh1", "bh2"):
        run = os.path.join(args.runs, f"east_d0.05_n64_{tag}")
        d[tag] = {"cstat": load(os.path.join(run, "east.cstat.hst"), [1, 8, 9, 11, 13]),
                  "nrpic": load(os.path.join(run, "east.nrpic.hst"), [1, 16, 30])}
    c1, c2 = d["bh1"]["cstat"], d["bh2"]["cstat"]
    n = min(len(c1), len(c2))
    assert np.allclose(c1[:n, 0], c2[:n, 0]), "record times differ"
    t = c1[:n, 0]
    res = {"a_crit_T2": a_crit, "t_crit_T2": t_crit, "cfl": C}
    for name, col in (("Hr_max", 3), ("Theta_max", 1), ("M_max", 4)):
        r = c2[:n, col] / np.maximum(c1[:n, col], 1e-300)
        i2 = np.where(r > 2.0)[0]
        first = float(t[i2[0]]) if len(i2) else None
        # first time after which the ratio stays above 2
        stay = None
        for i in range(n):
            if np.all(r[i:] > 2.0):
                stay = float(t[i])
                break
        res[name] = {"first_ratio_gt2": first, "ratio_stays_gt2_from": stay,
                     "ratio_at_t": {f"{tt:.4f}": float(rr) for tt, rr in
                                    zip(t[::4], r[::4])}}
        print(f"{name:10s}: bh2/bh1 > 2 first at t = {first}, stays above 2 from t = {stay}")
    nr2 = d["bh2"]["nrpic"]
    for key in ("Hr_max", "Theta_max"):
        ts = res[key]["ratio_stays_gt2_from"]
        if ts is not None:
            j = np.searchsorted(nr2[:, 0], ts)
            j = min(j, len(nr2) - 1)
            res[key]["alpha_max_bh2_there"] = float(nr2[j, 2])
            res[key]["a_there"] = (1 + ts / 2) ** 2
            print(f"   at t = {ts:.4f}: alpha_max(bh2) = {nr2[j, 2]:.3f}, "
                  f"a(t) = {(1 + ts / 2) ** 2:.3f}; T2 limit alpha = {a_crit:.3f} "
                  f"(t = {t_crit:.3f})")
    tend = float(c2[np.all(np.isfinite(c2), axis=1)][:, 0].max())
    res["bh2_last_finite_cstat_t"] = tend
    # lapse actually present: alpha_max against (1 + t/2)^2
    j = np.searchsorted(nr2[:, 0], t_crit)
    res["alpha_max_bh2_at_t_crit"] = float(nr2[min(j, len(nr2) - 1), 2])
    print(f"bh2 alpha_max at t_crit = {res['alpha_max_bh2_at_t_crit']:.3f} "
          f"(background a = {(1 + t_crit / 2) ** 2:.3f})")
    # integrated amplification from T2 growth factor: sum of ln Gmax over steps
    g = vn["growth_per_step"]
    a_g = np.array(g["a"])
    G = np.array(g["Gmax"])
    dt = 1.953125e-3  # bh2 athena.log, finest level
    tt = np.arange(0.0, 2.2, dt)
    lnamp = np.cumsum(np.log(np.interp((1 + tt / 2) ** 2, a_g, G)))
    res["T2_predicted_ln_amplification_at"] = {f"{x:.2f}": float(np.interp(x, tt, lnamp))
                                               for x in (1.2, 1.4, 1.6, 1.8, 1.97)}
    print("T2 amplification of the fastest grid mode, ln(A):",
          res["T2_predicted_ln_amplification_at"])
    with open(os.path.join(args.out, "bh2_onset.json"), "w") as f:
        json.dump(res, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    use_style()
    fig, axs = plt.subplots(3, 1, figsize=(FULL_WIDTH / 2 + 0.6, 7.0), sharex=True)
    fig.subplots_adjust(left=0.17, right=0.96, bottom=0.07, top=0.97, hspace=0.06)
    for ax, (name, col, lab) in zip(axs[:2], (("Hr_max", 3, r"largest relative $H$"),
                                              ("Theta_max", 1, r"largest $\Theta$"))):
        ax.plot(c1[:, 0], np.abs(c1[:, col]), color=SERIES[0], label="bh1, zero shift")
        ax.plot(c2[:, 0], np.abs(c2[:, col]), color=SERIES[1],
                label=r"bh2, $0.75\,\alpha^2\tilde\Gamma^i - 2\beta^i$")
        ax.axvline(t_crit, **GUIDE)
        ax.set_yscale("log")
        ax.set_ylabel(lab)
        ax.set_xlim(0, 2.6)
    axs[0].legend(loc="upper left", fontsize=8)
    ax = axs[2]
    for tag, col in (("bh1", SERIES[0]), ("bh2", SERIES[1])):
        nr = d[tag]["nrpic"]
        ax.plot(nr[:, 0], nr[:, 2], color=col)
    tt2 = np.linspace(0, 2.6, 100)
    ax.plot(tt2, (1 + tt2 / 2) ** 2, color="k", ls=":", lw=1.0, label=r"$a=(1+t/2)^2$")
    ax.axhline(a_crit, **MASK_LINE)
    ax.axvline(t_crit, **GUIDE, label=r"T2 limit, $0.25\,\alpha = C_{\rm crit}$")
    ax.set_ylabel(r"largest lapse")
    ax.set_ylim(0.0, 6.0)  # the last records of bh2 carry the broken state
    ax.set_xlabel(r"conformal time $t$")
    ax.legend(loc="upper left", fontsize=8)
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(args.out, f"bh2_onset.{ext}"))
    print("wrote", os.path.join(args.out, "bh2_onset.png"))


if __name__ == "__main__":
    main()
