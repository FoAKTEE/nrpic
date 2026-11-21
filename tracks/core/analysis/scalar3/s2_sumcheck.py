#!/usr/bin/env python3
"""Check PSd of tracks/core/JOURNAL-scalar3.md (entry 15), an addition to test S: the
columns of `<scalar_field> con_signed` against the dumps when the two reductions of
ScalarField::ConstraintSignedMeans are repeated as the processor executable does them.

    python3 s2_sumcheck.py --data DIR [--out DIR]

DIR is the run directory of s1_signed.py (runs sig and zsig).  The code forms
vtot = sum vol, <H> = (sum vol H)/vtot, and with H' = H - <H>: <|H'|/[H]> =
(sum vol |H'|/[H])/vtot, rms H' = sqrt((sum vol H'^2)/vtot), each sum a running sum over
the cells with i fastest (Kokkos::Sum on one thread), vol = dx1 dx2 dx3.  numpy's mean
sums pairwise.  Here: (a) the running sum of the equal volumes against N^3 vol; (b)
column [21] against the pairwise mean and against the running sums; (c) the same for
[25] and [27].  Writes OUT/summary.json and OUT/fig_sumcheck.png."""
import argparse
import os

import s3
from s3 import common, np, sf

BASE = "usr"
XMAX = 6.283185307179586      # x1max of the input file, x1min = 0


def serial(x):
    """Running sum in the order given (np.cumsum adds one term after the other)."""
    return float(np.cumsum(x)[-1])


def rel(x, y):
    return float(abs(x/y - 1.0)) if y != 0.0 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    out = s3.run_dir(a.out)
    summ = dict(data=os.path.abspath(a.data))
    rows = []
    for k in ("sig", "zsig"):
        rd = os.path.join(a.data, k)
        c = sf.read_con_history(os.path.join(rd, BASE + ".sf.con.hst"))
        for cy, d in sorted(s3.dumps(rd, BASE).items()):
            i = int(np.searchsorted(c["cycle"], cy))
            if i >= c["cycle"].size or int(c["cycle"][i]) != cy:
                continue
            f = d["fields"]
            nn = f["H"].shape[0]
            dx = XMAX/nn
            vol = dx*dx*dx
            order = lambda x: x.transpose(2, 1, 0).ravel()       # noqa: E731  i fastest
            h, hm = order(f["H"]), order(f["Hmag"])
            vtot = serial(np.full(h.size, vol))
            hbar = serial(vol*h)/vtot
            hp = h - hbar
            r = np.where(hm > 0.0, np.abs(hp)/np.where(hm > 0.0, hm, 1.0), 0.0)
            hp_ratio = serial(vol*r)/vtot
            hp_rms = float(np.sqrt(serial(vol*hp*hp)/vtot))
            # numpy (pairwise) values, as s1_signed.py compared
            hb_np = float(f["H"].mean())
            hp_np = f["H"] - hb_np
            r_np = np.where(f["Hmag"] > 0.0, np.abs(hp_np)/f["Hmag"], 0.0)
            row = dict(run=k, cycle=cy, time=float(d["time"]), cells=int(h.size),
                       vtot_rel=float(vtot/(h.size*vol) - 1.0),
                       H_mean=float(c["H_mean"][i]), H_mean_serial=hbar,
                       H_mean_numpy=hb_np,
                       H_mean_vs_numpy=rel(c["H_mean"][i], hb_np),
                       H_mean_vs_serial=rel(c["H_mean"][i], hbar),
                       H_mean_bits_equal=bool(c["H_mean"][i] == hbar),
                       Hp_rms=float(c["Hp_rms"][i]), Hp_rms_serial=hp_rms,
                       Hp_rms_vs_numpy=rel(c["Hp_rms"][i],
                                           float(np.sqrt(np.mean(hp_np**2)))),
                       Hp_rms_vs_serial=rel(c["Hp_rms"][i], hp_rms),
                       Hp_ratio=float(c["Hp_ratio"][i]), Hp_ratio_serial=hp_ratio,
                       Hp_ratio_vs_numpy=rel(c["Hp_ratio"][i], float(r_np.mean())),
                       Hp_ratio_vs_serial=rel(c["Hp_ratio"][i], hp_ratio))
            for x, y in (("Mx_mean", "Mx"), ("My_mean", "My"), ("Mz_mean", "Mz")):
                row[x + "_vs_serial"] = rel(c[x][i], serial(vol*order(f[y]))/vtot)
            rows.append(row)
    summ["rows"] = rows
    sig = [x for x in rows if x["run"] == "sig"]

    def worst(key, sel):
        v = [x[key] for x in sel if x[key] is not None]
        return max(v) if v else None
    summ["max"] = dict(
        vtot_rel=[min(x["vtot_rel"] for x in rows), max(x["vtot_rel"] for x in rows)],
        H_mean_vs_numpy_sig=worst("H_mean_vs_numpy", sig),
        H_mean_vs_serial_sig=worst("H_mean_vs_serial", sig),
        H_mean_vs_serial_all=worst("H_mean_vs_serial", rows),
        H_mean_bits_equal=[int(sum(x["H_mean_bits_equal"] for x in rows)), len(rows)],
        Hp_rms_vs_numpy_sig=worst("Hp_rms_vs_numpy", sig),
        Hp_rms_vs_serial_sig=worst("Hp_rms_vs_serial", sig),
        Hp_ratio_vs_numpy_sig=worst("Hp_ratio_vs_numpy", sig),
        Hp_ratio_vs_serial_sig=worst("Hp_ratio_vs_serial", sig),
        M_mean_vs_serial_sig=max(worst(x + "_vs_serial", sig)
                                 for x in ("Mx_mean", "My_mean", "Mz_mean")))
    common.dump_json(summ, os.path.join(out, "summary.json"))

    fs = common.style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 2.7))
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.17, top=0.95, wspace=0.28)
    B, R_, G = fs.PAL["blue"], fs.PAL["red"], fs.PAL["green"]
    t = [x["time"] for x in sig]
    floor = 1e-17
    for j, (key, lab) in enumerate((("H_mean", r"$\langle\mathcal{H}\rangle$"),
                                    ("Hp_rms", r"rms $\mathcal{H}'$"),
                                    ("Hp_ratio",
                                     r"$\langle|\mathcal{H}'|/[\mathcal{H}]\rangle$"))):
        cl = (B, R_, G)[j]
        ax[0].plot(t, [max(x[key + "_vs_numpy"], floor) for x in sig], "-o", ms=3,
                   color=cl, label=lab)
        ax[1].plot(t, [max(x[key + "_vs_serial"], floor) for x in sig], "-o", ms=3,
                   color=cl, label=lab)
    ax[0].axhline(abs(sig[0]["vtot_rel"]), **fs.MASK_LINE)
    for j, lab in ((0, "record against the pairwise mean of the dump"),
                   (1, "record against the running sums of the dump")):
        ax[j].set_yscale("log")
        ax[j].set_ylim(3e-18, 3e-9)
        ax[j].set_xlabel("time")
        ax[j].set_ylabel(lab, fontsize=7)
    ax[0].legend(loc="lower right", fontsize=6.5)
    fig.savefig(os.path.join(out, "fig_sumcheck.png"), dpi=200)
    print("PSd done:", os.path.join(out, "summary.json"))


if __name__ == "__main__":
    main()
