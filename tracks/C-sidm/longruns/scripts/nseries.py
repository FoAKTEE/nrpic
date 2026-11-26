#!/usr/bin/env python3
"""Reader of the N-series of collisionless controls on M/8 (predictions NS.1-NS.3,
tracks/C-sidm/JOURNAL.md entry 2026-11-24T13:14Z): the same King model (y0 = 0.334032,
stratified seed 1), deck A8 or A8N, at N = 1e4, 1e5, 1e6 particles.

    python3 nseries.py --out DIR LABEL=RUN [LABEL=RUN ...]

LABEL is N1e4, N1e5 or N1e6 (any label works; the number after N is the particle count used
for the 1/N scaling of the constraint floor); RUN a run id under scratch/C-sidm or a run
directory with cc.nrpic.hst (and cc.z4c.user.hst) at its top.

Histories are read so that a restarted segment replaces rows from its first time on (the
rule of blockA_delta.py). Per run:
- t_c: first crossing of alpha_min = 0.3, linear in time between records (as blockA_delta.py);
- alpha_c(t) - alpha_c(0) (alpha_c = alpha_probe at the centre) as 20 M means centred on
  100, 200, 300, 400, 500 M and over [580, 600] M (NS.1 reads the one at 400 M);
- the same for sum_mW / sum_m (mean Lorentz factor) relative to t = 0;
- the H-norm2 floor, mean over [100, 300] M (cc.z4c.user.hst), and the ratio of floors
  between labels against the ratio of particle numbers.
Verdict numbers only; the judgement goes into the journal.
Writes DIR/nseries.json and DIR/fig_nseries.png.
"""
import argparse
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
CENTRES = (100.0, 200.0, 300.0, 400.0, 500.0)
HALF = 10.0


def read_hist(path):
    """Columns by name from the first header with '[1]='; a later row with a time not after
    the last kept one truncates what came before (restarted segment wins)."""
    names, out = None, []
    with open(path) as f:
        for ln in f:
            if ln.startswith("#"):
                if names is None and "[1]=" in ln:
                    names = re.findall(r"\[\d+\]=(\S+)", ln)
                continue
            v = ln.split()
            if not v:
                continue
            r = [float(x) for x in v]
            while out and out[-1][0] >= r[0] - 1e-12:
                out.pop()
            out.append(r)
    a = np.array(out)
    return {n: a[:, i] for i, n in enumerate(names[:a.shape[1]])}


def crossing(t, y, level=0.3):
    i = np.nonzero(y < level)[0]
    if len(i) == 0:
        return None
    k = i[0]
    if k == 0:
        return float(t[0])
    return float(t[k - 1] + (level - y[k - 1]) * (t[k] - t[k - 1]) / (y[k] - y[k - 1]))


def wmean(t, y, a, b):
    m = (t >= a) & (t <= b) & np.isfinite(y)
    if m.sum() < 3 or t[-1] < b - 0.5:
        return None
    return float(np.mean(y[m]))


def nparticles(lab, h):
    m = re.match(r"N(\d+(?:\.\d+)?)e(\d+)", lab)
    if m:
        return float(m.group(1)) * 10 ** int(m.group(2))
    return float(h["np"][0])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--title", default="Collisionless control of y0 = 0.334032 on M/8 against particle number")
    ap.add_argument("--control", default=None,
                    help="label of the control: adds alpha_c(run) - alpha_c(control) as 20 M means")
    ap.add_argument("--band", type=float, default=None,
                    help="draw +-BAND on the alpha_c panel instead of the NS guides (bracket readings)")
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res, ser = {}, {}
    for s in a.runs:
        lab, r = s.split("=", 1)
        d = r if os.path.isdir(r) else os.path.join(SCR, r)
        h = read_hist(os.path.join(d, "cc.nrpic.hst"))
        t = h["time"]
        dac = h["alpha_probe"] - h["alpha_probe"][0]
        gam = h["sum_mW"] / h["sum_m"]
        dgam = gam - gam[0]
        o = dict(run=r, t_end=float(t[-1]), rows=int(len(t)), np0=int(h["np"][0]),
                 alpha_c0=float(h["alpha_probe"][0]), alpha_min0=float(h["alpha_min"][0]),
                 t_c=crossing(t, h["alpha_min"]),
                 alpha_min_min=float(np.nanmin(h["alpha_min"])),
                 t_alpha_min_min=float(t[int(np.nanargmin(h["alpha_min"]))]),
                 dalpha_c={}, dgamma={})
        for c in CENTRES:
            o["dalpha_c"][f"{c:.0f}"] = wmean(t, dac, c - HALF, c + HALF)
            o["dgamma"][f"{c:.0f}"] = wmean(t, dgam, c - HALF, c + HALF)
        o["dalpha_c"]["580_600"] = wmean(t, dac, 580.0, 600.0)
        o["dgamma"]["580_600"] = wmean(t, dgam, 580.0, 600.0)
        # range of the 20 M block means of alpha_c - alpha_c(0) over [0, min(t_end, t_c)]
        # (B17.6, B20.1: the band [-0.03, +0.03]); blocks [0,20], [20,40], ...
        tb = o["t_c"] if o["t_c"] is not None else float(t[-1])
        blocks = [wmean(t, dac, b, b + 20.0) for b in np.arange(0.0, tb - 20.0 + 1e-9, 20.0)]
        blocks = [x for x in blocks if x is not None]
        o["dalpha_c_block20_min"] = float(min(blocks)) if blocks else None
        o["dalpha_c_block20_max"] = float(max(blocks)) if blocks else None
        o["dalpha_c_block20"] = blocks
        zp = os.path.join(d, "cc.z4c.user.hst")
        zt = zh = None
        if os.path.exists(zp):
            z = read_hist(zp)
            zt, zh = z["time"], z["H-norm2"]
            o["H_norm2_0"] = float(zh[0])
            o["H_norm2_mean_100_300"] = wmean(zt, zh, 100.0, 300.0)
        o["N"] = nparticles(lab, h)
        res[lab] = o
        ser[lab] = (t, dac, h["alpha_min"], dgam, zt, zh)
    # pairwise numbers the predictions read
    labs = sorted(res, key=lambda k: res[k]["N"])
    pairs = {}
    for i in range(len(labs)):
        for j in range(i + 1, len(labs)):
            lo, hi = labs[i], labs[j]
            p = {"N_ratio": res[hi]["N"] / res[lo]["N"]}
            if res[lo].get("H_norm2_mean_100_300") and res[hi].get("H_norm2_mean_100_300"):
                p["H_floor_ratio_lo_over_hi"] = res[lo]["H_norm2_mean_100_300"] / res[hi]["H_norm2_mean_100_300"]
            p["dalpha_c_diff_hi_minus_lo"] = {k: (res[hi]["dalpha_c"][k] - res[lo]["dalpha_c"][k])
                                              if res[hi]["dalpha_c"][k] is not None and res[lo]["dalpha_c"][k] is not None
                                              else None for k in res[hi]["dalpha_c"]}
            pairs[f"{hi}_vs_{lo}"] = p
    if a.control:
        tc_, dc_ = ser[a.control][0], ser[a.control][1]
        for lab in labs:
            if lab == a.control:
                continue
            t, dac = ser[lab][0], ser[lab][1]
            tend = min(float(t[-1]), float(tc_[-1]))
            if res[lab]["t_c"] is not None:
                tend = min(tend, res[lab]["t_c"])
            d = {}
            for b in np.arange(0.0, tend - 20.0 + 1e-9, 20.0):
                m1 = (t >= b) & (t <= b + 20.0)
                m2 = (tc_ >= b) & (tc_ <= b + 20.0)
                if m1.sum() >= 3 and m2.sum() >= 3:
                    d[f"{b:.0f}_{b + 20:.0f}"] = float(np.mean(dac[m1]) - np.mean(dc_[m2]))
            res[lab]["delta_vs_control"] = d
            vals = list(d.values())
            res[lab]["delta_vs_control_absmax"] = float(max(abs(x) for x in vals)) if vals else None
    out = dict(runs=res, pairs=pairs, control=a.control, title=a.title,
               predictions="JOURNAL 2026-11-24T13:14Z: NS.1 N1e6 no collapse by 600 M and dalpha_c(400) > -0.005; "
                           "NS.2 t_c(N1e6) in [455, 615] M; NS.3 N1e4 collapse before 300 M (relaxation) or in [455, 615] (scheme)")
    with open(os.path.join(a.out, "nseries.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    for lab in labs:
        o = res[lab]
        print(lab, {k: o[k] for k in ("t_end", "np0", "alpha_c0", "t_c", "alpha_min_min", "t_alpha_min_min",
                                       "H_norm2_mean_100_300", "dalpha_c_block20_min", "dalpha_c_block20_max",
                                       "delta_vs_control_absmax") if k in o})
        print("   dalpha_c", o["dalpha_c"])
        print("   dgamma  ", o["dgamma"])
    print(json.dumps(pairs, indent=1, default=float))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    cols = dict(zip(labs, fs.series_colors(max(3, len(labs)))))
    fig, axs = plt.subplots(2, 2, figsize=(8.6, 6.0))
    ax = axs.ravel()
    for lab in labs:
        t, dac, am, dg, zt, zh = ser[lab]
        c = cols[lab]
        tc = res[lab]["t_c"]
        lbl = f"{lab}" + (f" (t_c {tc:.1f} M)" if tc else " (no collapse)")
        ax[0].plot(t, dac, color=c, lw=0.9, label=lbl)
        ax[1].plot(t, am, color=c, lw=0.9, label=lab)
        ax[2].plot(t, dg, color=c, lw=0.9, label=lab)
        if zt is not None:
            ax[3].semilogy(zt, zh, color=c, lw=0.9, label=lab)
    ax[1].axhline(0.3, **fs.GUIDE)
    if a.band is None:
        ax[0].axhline(-0.005, **fs.GUIDE)
        ax[0].axvline(400.0, **fs.GUIDE)
        ax[0].set_ylim(-0.12, 0.03)
        for x in (455.0, 615.0):
            ax[1].axvline(x, **fs.GUIDE)
        ax[1].set_title("guides: alpha_min 0.3; NS.2 window 455-615 M", fontsize=7)
        ax[0].set_title("guides: NS.1 bar -0.005 at 400 M", fontsize=7)
    else:
        for y in (-a.band, a.band):
            ax[0].axhline(y, **fs.GUIDE)
        ax[0].set_ylim(-0.12, 0.05)
        ax[1].set_title("guide: alpha_min 0.3 (the lapse collapse marker)", fontsize=7)
        ax[0].set_title(f"guides: band +-{a.band:g} of the stable member's prediction", fontsize=7)
    ax[0].set_ylabel(r"$\alpha_c(t)-\alpha_c(0)$")
    ax[1].set_ylabel(r"$\alpha_{\min}$")
    ax[2].set_ylabel(r"$\langle W\rangle(t)-\langle W\rangle(0)$")
    ax[3].set_ylabel("H-norm2")
    for x in ax:
        x.set_xlabel("t / M")
    ax[0].legend(fontsize=7)
    fig.suptitle(a.title, fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_nseries.png"), dpi=150)


if __name__ == "__main__":
    main()
