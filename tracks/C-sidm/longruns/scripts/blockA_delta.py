#!/usr/bin/env python3
"""Reader of block A (predictions A.1-A.4, tracks/C-sidm/JOURNAL.md 2026-11-21T20:25Z).

For each (model, seed) with a control and kicked runs:
  Delta(t) = alpha_c,kick(t) - alpha_c,ctrl(t)   (alpha_probe of cc.nrpic.hst, on the control's
                                                  times, linear interpolation)
  window means of Delta over [0,100), [100,200), ... M; t_c = first linear crossing of
  alpha_min = 0.3; the control's alpha_c - alpha_c(0) mean over [500,600) M (A.4).
Noise model (named before the runs): sigma_w = max(sd over the seeds of the threshold model
of the window mean of Delta, rms of the control's alpha_c about its 50 M running mean);
2.5e-3 while fewer than two seeds exist. A signal is a window mean beyond 3 sigma_w.

    python3 blockA_delta.py --out DIR RUN [RUN ...]

RUN: a run directory (scratch/C-sidm/<run_id>) or a run id; its deck name A8_<y0>_s<s>_<k>
is read from chain/input.athinput or from the *.athinput in the directory. A restarted chain
appends to one history; rows whose time does not exceed the last kept time are replaced by
the later segment. Writes DIR/blockA.json and DIR/fig_blockA.png.

--ripple-tmax T (added 2026-11-24, after the data, [JUDGEMENT]): the ripple of a control is
taken over t < T only. The noise model was named before the runs on the assumption that no
control collapses; two controls collapsed (t_c 535 and 549 M), and a ripple over the whole
record measures the collapse, not the noise (sigma_w 0.07 in run C-20261124-130506-2ddce1f).
Without the option the reader behaves as before. Also printed: alpha_c - alpha_c(0), 20 M
means centred on 100, 200, 300, 400, 500 M, per run.
"""
import argparse
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(WT, "python"))
SCR = "/data/haiyangw/nrpic/scratch/C-sidm"
WIN = 100.0
SIGMA_DEFAULT = 2.5e-3
THRESHOLD_MODEL = "y0p33403"


def read_hist(path):
    """Columns of an NRPIC history; later segments of a restarted run win."""
    names = None
    rows = []
    with open(path) as f:
        for ln in f:
            if ln.startswith("#"):
                if "[1]=" in ln and names is None:
                    names = [m.group(1) for m in re.finditer(r"\[\d+\]=(\S+)", ln)]
                continue
            v = ln.split()
            if v:
                rows.append([float(x) for x in v])
    out = []
    for r in rows:   # a restart re-writes times it had written before the kill
        while out and out[-1][0] >= r[0] - 1e-12:
            out.pop()
        out.append(r)
    a = np.array(out)
    return {n: a[:, i] for i, n in enumerate(names[:a.shape[1]])}


def deck_name(d):
    for p in [os.path.join(d, "chain", "input.athinput")] + sorted(glob.glob(os.path.join(d, "*.athinput"))):
        if os.path.exists(p):
            m = re.search(r"problem\s*=\s*King cluster (A8_\S+)", open(p).read())
            if m:
                return m.group(1)
    return None


def crossing(t, y, level=0.3):
    i = np.nonzero(y < level)[0]
    if len(i) == 0:
        return None
    k = i[0]
    if k == 0:
        return float(t[0])
    return float(t[k - 1] + (level - y[k - 1]) * (t[k] - t[k - 1]) / (y[k] - y[k - 1]))


def running_mean(t, y, width):
    dt = np.median(np.diff(t))
    n = max(1, int(round(width / dt)))
    if n < 2 or len(y) < n:
        return y.copy()
    ys = np.convolve(y, np.ones(n) / n, mode="same")
    h = n // 2
    ys[:h], ys[len(ys) - h:] = np.nan, np.nan
    return ys


def window_means(t, y, tmax):
    out = []
    for w0 in np.arange(0.0, tmax, WIN):
        m = (t >= w0) & (t < w0 + WIN) & np.isfinite(y)
        out.append(float(np.mean(y[m])) if m.sum() > 10 else None)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR"))
    ap.add_argument("--ripple-tmax", type=float, default=None)
    ap.add_argument("runs", nargs="+")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs = {}
    for r in a.runs:
        d = r if os.path.isdir(r) else os.path.join(SCR, r)
        name = deck_name(d)
        h = os.path.join(d, "cc.nrpic.hst")
        if name is None or not os.path.exists(h):
            print(f"skip {r}: no A8 deck or no history", flush=True)
            continue
        m = re.match(r"A8_(y0p\d+)_s(\d+)_(ctrl|kin|kout)$", name)
        runs[(m.group(1), int(m.group(2)), m.group(3))] = dict(dir=d, hist=read_hist(h))
    res = {"runs": {}, "pairs": {}, "noise": {}}
    for (y, s, k), v in sorted(runs.items()):
        H = v["hist"]
        res["runs"][f"{y}_s{s}_{k}"] = dict(dir=v["dir"], t_end=float(H["time"][-1]),
                                           t_c=crossing(H["time"], H["alpha_min"]),
                                           alpha_c0=float(H["alpha_probe"][0]))
        for tw in (100.0, 200.0, 300.0, 400.0, 500.0):
            m = (H["time"] >= tw - 10.0) & (H["time"] <= tw + 10.0)
            res["runs"][f"{y}_s{s}_{k}"][f"dalpha_c_{int(tw)}"] = (
                float(np.mean(H["alpha_probe"][m] - H["alpha_probe"][0])) if m.sum() > 10 else None)
    ripple = {}
    for (y, s, k), v in runs.items():
        if k != "ctrl":
            continue
        H = v["hist"]
        t, ac = H["time"], H["alpha_probe"]
        rm = np.ones(len(t), bool) if a.ripple_tmax is None else (t < a.ripple_tmax)
        ripple[(y, s)] = float(np.nanstd((ac - running_mean(t, ac, 50.0))[rm])) if rm.sum() > 400 else None
        if ripple[(y, s)] is None:
            del ripple[(y, s)]
        m = (t >= 500.0) & (t < 600.0)
        res["runs"][f"{y}_s{s}_ctrl"]["contraction_500_600"] = float(np.mean(ac[m] - ac[0])) if m.sum() > 10 else None
        res["runs"][f"{y}_s{s}_ctrl"]["ripple_rms_50M"] = ripple.get((y, s))
        for kk in ("kin", "kout"):
            if (y, s, kk) not in runs:
                continue
            K = runs[(y, s, kk)]["hist"]
            tk = K["time"]
            tt = t[t <= tk[-1]]
            dl = np.interp(tt, tk, K["alpha_probe"]) - ac[:len(tt)]
            res["pairs"][f"{y}_s{s}_{kk}"] = dict(windows=window_means(tt, dl, min(tt[-1], 600.0) + 1e-9),
                                                 t_end=float(tt[-1]))
            runs[(y, s, kk)]["delta"] = (tt, dl)
    # noise model
    for kk in ("kin", "kout"):
        ws = [res["pairs"][p]["windows"] for p in res["pairs"] if p.startswith(THRESHOLD_MODEL) and p.endswith(kk)]
        sd = []
        if len(ws) >= 2:
            for j in range(max(len(w) for w in ws)):
                col = [w[j] for w in ws if j < len(w) and w[j] is not None]
                sd.append(float(np.std(col, ddof=1)) if len(col) >= 2 else None)
        res["noise"][f"seed_sd_{kk}"] = sd
    rip = max(ripple.values()) if ripple else None
    sds = [x for kk in ("kin", "kout") for x in res["noise"][f"seed_sd_{kk}"] if x is not None]
    sigma = max([x for x in (rip, max(sds) if sds else None) if x is not None] or [SIGMA_DEFAULT])
    if not sds:
        sigma = max(sigma, SIGMA_DEFAULT)
    res["noise"].update(ripple_max=rip, sigma_w=sigma, ripple_tmax=a.ripple_tmax,
                        rule="max(seed sd, ripple); 2.5e-3 floor until two seeds")
    for p, v in res["pairs"].items():
        v["beyond_3sigma"] = [None if w is None else bool(abs(w) > 3 * sigma) for w in v["windows"]]
    with open(os.path.join(a.out, "blockA.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res["noise"], indent=1))
    for n, v in res["runs"].items():
        print(n, "t_end %.1f" % v["t_end"], "t_c", v["t_c"], {k: v[k] for k in v if k.startswith(("contr", "ripple", "dalpha"))})
    for n, v in res["pairs"].items():
        print(n, ["%+.4f" % w if w is not None else "-" for w in v["windows"]])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    models = sorted({y for (y, s, k) in runs})
    fig, axs = plt.subplots(2, max(1, len(models)), figsize=(3.2 * max(1, len(models)), 5.0), squeeze=False)
    cols = fs.series_colors(3)
    for j, y in enumerate(models):
        for (yy, s, k), v in sorted(runs.items()):
            if yy != y:
                continue
            H = v["hist"]
            c = cols[("ctrl", "kin", "kout").index(k)]
            ls = ["-", "--", ":"][(s - 1) % 3]
            axs[0, j].plot(H["time"], H["alpha_probe"] - H["alpha_probe"][0], color=c, ls=ls, lw=0.8,
                           label=f"s{s} {k}")
            if "delta" in v:
                tt, dl = v["delta"]
                axs[1, j].plot(tt, dl, color=c, ls=ls, lw=0.8, label=f"s{s} {k}")
        axs[1, j].axhspan(-3 * sigma, 3 * sigma, color="0.85", lw=0)
        axs[0, j].set_title(y.replace("y0p", "y0 = 0."))
        axs[1, j].set_xlabel("t / M")
        axs[0, j].legend(fontsize=6)
    axs[0, 0].set_ylabel(r"$\alpha_c(t)-\alpha_c(0)$")
    axs[1, 0].set_ylabel(r"$\Delta = \alpha_{c,\rm kick}-\alpha_{c,\rm ctrl}$ (band: $3\sigma_w$)")
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "fig_blockA.png"), dpi=150)
    print("wrote", os.path.join(a.out, "fig_blockA.png"))


if __name__ == "__main__":
    main()
