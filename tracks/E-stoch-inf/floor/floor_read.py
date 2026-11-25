"""Reader of the floor runs (floor/JOURNAL.md entry 1, predictions F1-F5).

For each run pair (s = 1 and s = 1/2 at one resolution) it
1. passes the last dump of each run through ../repro/figs/figures/dumppass.py with --save-modes.
   The lockstep .modes record of a run with noise_mode_scale = 1/2 already carries the factor 1/2
   (scalar_field_2.md: the scale is applied to the mode file; checked here on the two records), so
   the s = 1/2 run is read with --scale 1 (option --sh-scale). Entry 1 had named --scale 0.5; the
   first reading E-20261125-115056-983a32a used it and its control F3 caught the double factor;
2. forms the statistics of entry 1 over the ten shells n^2 = 2, 3, 4, 5, 6, 8, 9, 10, 11, 12:
   median abs(1 - P_NR/P_lin), sqrt(median sum|c_NR - c_lin|^2 / sum|c_lin|^2), the sign pattern,
   the median over the shells n^2 >= 49, the per-mode relative rms (modes with W > 1/2);
3. the ratios R = value(s = 1)/value(s = 1/2) and the judgement of F1-F4;
4. a split made after the data (labelled so in the outputs): with e(s) = c_NR(s) - c_lin(s) per mode
   and e = s L + s^2 Q (no third order), L = 4 e(1/2) - e(1), Q = 2 [e(1) - 2 e(1/2)], per shell
   the relative norms |L|/|c_lin(1)| and |Q|/|c_lin(1)|;
5. one figure: abs(1 - P_NR/P_lin) per shell for both amplitudes, the s = 1 curve divided by 2
   (the second-order expectation) and by 1 (an amplitude-independent floor).

Usage: floor_read.py OUTDIR --pair LABEL:RUN_S1:RUN_SHALF [--pair ...] [--workers 1]
The outputs: OUTDIR/<label>_s1/, OUTDIR/<label>_sh/ (dumppass npz), OUTDIR/floor_stats.json,
OUTDIR/fig_floor.{pdf,png}.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "..", "repro", "figs", "figures")
sys.path.insert(0, FIGDIR)
import figstyle as fs  # noqa: E402

LOW = (2, 3, 4, 5, 6, 8, 9, 10, 11, 12)


def dump_pass(run, label, out, scale):
    od = os.path.join(out, label)
    files = sorted(f for f in os.listdir(run) if f.startswith("sr.sf.") and f.endswith(".dump"))
    last = files[-1].split(".")[-2]
    npz = os.path.join(od, "d" + last + ".npz")
    if not os.path.exists(npz):
        cmd = [sys.executable, os.path.join(FIGDIR, "dumppass.py"), "--run", run, "--base", "sr",
               "--label", label, "--out", out, "--last", "--scale", repr(scale), "--save-modes",
               "--fft-workers", "2"]
        print(" ".join(cmd), flush=True)
        subprocess.run(cmd, check=True)
    return npz


def stats(d):
    n2 = d["inj_n2"]
    p = d["inj_pnr"] / d["inj_plin"]
    amp = d["inj_pdiff"] / d["inj_plin"]
    lo = np.array([np.where(n2 == k)[0][0] for k in LOW])
    hi = np.where(n2 >= 49)[0]
    dev = 1.0 - p
    return dict(
        time=float(d["time"]),
        median_power=float(np.median(np.abs(dev[lo]))),
        amplitude=float(np.sqrt(np.median(amp[lo]))),
        signs="".join("+" if x > 0 else "-" for x in dev[lo]),
        median_power_hi=float(np.median(np.abs(dev[hi]))),
        n_hi=int(hi.size),
        rel_rms=float(d["inj_rel_rms"]),
        dev_low=[float(x) for x in dev[lo]],
        n2=[int(x) for x in n2], dev_all=[float(x) for x in dev])


def split(d1, dh, scale_h=0.5):
    """After the data: e = s L + s^2 Q per mode; shell norms relative to |c_lin(1)|."""
    c1, ch = d1["inj_c_nr"], dh["inj_c_nr"]
    assert np.array_equal(d1["inj_mode_n2"], dh["inj_mode_n2"])
    # c_lin per mode is not saved; rebuild it from the s = 1 shell sums would lose phases, so use the
    # linearity of c_lin in s: c_lin(1/2) = c_lin(1)/2 and e(1) - 2 e(1/2) = c_NR(1) - 2 c_NR(1/2)
    q = 2.0 * (c1 - 2.0 * ch)          # Q (no third order assumed)
    n2m = d1["inj_mode_n2"]
    shells = d1["inj_n2"]
    plin = d1["inj_plin"]
    pdiff1 = d1["inj_pdiff"]
    out = {}
    for k in LOW:
        sel = n2m == k
        i = int(np.where(shells == k)[0][0])
        qn = np.sqrt(np.sum(np.abs(q[sel]) ** 2) / plin[i])
        tot = np.sqrt(pdiff1[i] / plin[i])
        out[int(k)] = dict(Q_rel=float(qn), e1_rel=float(tot))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--pair", action="append", required=True)
    ap.add_argument("--sh-scale", type=float, default=1.0,
                    help="--scale given to dumppass for the s = 1/2 run (1: the record carries s)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    res = {"note": "split_after_data is a reading made after the data (not in entry 1)"}
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, len(args.pair), figsize=(fs.FULL_WIDTH if len(args.pair) > 1
                                                        else fs.COLUMN_WIDTH * 1.3, 3.0),
                             squeeze=False)
    for j, spec in enumerate(args.pair):
        label, r1, rh = spec.split(":")
        n1 = dump_pass(r1, label + "_s1", args.out, 1.0)
        nh = dump_pass(rh, label + "_sh", args.out, args.sh_scale)
        d1, dh = np.load(n1), np.load(nh)
        sys.path.insert(0, FIGDIR)
        import figlib as fl
        last = os.path.basename(n1)[1:-4]
        m1 = fl.read_modes_file(os.path.join(r1, f"sr.sf.{last}.modes"))
        mh = fl.read_modes_file(os.path.join(rh, f"sr.sf.{last}.modes"))
        rec_ratio = mh["R"] / m1["R"]
        rec = dict(min=float(np.abs(rec_ratio).min()), max=float(np.abs(rec_ratio).max()),
                   time_s1=float(m1["time"]), time_sh=float(mh["time"]), sh_scale=args.sh_scale)
        s1, sh = stats(d1), stats(dh)
        ratios = {k: s1[k] / sh[k] for k in ("median_power", "amplitude", "rel_rms",
                                              "median_power_hi")}
        flips = sum(a != b for a, b in zip(s1["signs"], sh["signs"]))
        res[label] = dict(s1=s1, sh=sh, ratios=ratios, sign_flips=int(flips),
                          split_after_data=split(d1, dh), record_ratio=rec,
                          inputs=dict(s1=n1, sh=nh, run_s1=r1, run_sh=rh))
        ax = axes[0, j]
        x = np.array(LOW)
        ax.semilogy(x, np.abs(s1["dev_low"]), "o-", color=fs.SERIES[0], label=r"$s=1$")
        ax.semilogy(x, np.abs(sh["dev_low"]), "s-", color=fs.SERIES[1], label=r"$s=1/2$")
        ax.semilogy(x, np.abs(s1["dev_low"]) / 2, **fs.GUIDE, label=r"$s=1$ curve $/2$")
        ax.semilogy(x, np.abs(s1["dev_low"]) / 4, color="grey", ls=":", lw=1.5,
                    label=r"$s=1$ curve $/4$")
        ax.set_xlabel(r"shell $n^2$")
        ax.set_ylabel(r"$|1-P_{\rm NR}/P_{\rm lin}|$")
        ax.set_title(f"{label}: R(median) = {ratios['median_power']:.2f}", fontsize=9)
        ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    files = fs.save(fig, os.path.join(args.out, "fig_floor"))
    res["figures"] = files
    with open(os.path.join(args.out, "floor_stats.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    for label in [p.split(":")[0] for p in args.pair]:
        r = res[label]
        print(label, "s1", {k: r["s1"][k] for k in ("median_power", "amplitude", "signs",
                                                      "median_power_hi", "rel_rms")})
        print(label, "sh", {k: r["sh"][k] for k in ("median_power", "amplitude", "signs",
                                                      "median_power_hi", "rel_rms")})
        print(label, "ratios", r["ratios"], "flips", r["sign_flips"])
        print(label, "split", r["split_after_data"])


if __name__ == "__main__":
    main()
