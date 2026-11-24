"""Why the note's and the independent check's 256^3 members of Fig. 7 differ (ledger rows 68-71).

The note's reader (dumppass.py, ladder_lib.curvature) and the check's (repro/verify lattice.py) take
R^NR of a dump in two ways that agree at linear order:
  note:  R = c[chi]/(2<chi>) + (H_b/Pi_b) c[phi] + (1/4) nhat_i nhat_j c[gt_ij],  H_b = -<K>/(3<alpha>)
  check: R = c[ln chi]/2     + (H/Pi_b)   c[phi] + (1/4) nhat_i nhat_j c[gt_ij],  H   = -<K>/3
and the check counts a shell's modes over both hemispheres (the note: independent modes).
For the final dump (17, N_f) of the SR rungs 128^3 and 256^3 this script evaluates the four readers
  A note, B note with H = -<K>/3, C note with c[ln chi]/2, D = B and C together (the check's),
against the same linear reference c_lin = L^-3/2 W R_lockstep alpha_n (the code's .modes record
of the dump; W the window at the dump's a, H; alpha_n Track E's Philox), and writes
  per-mode rms of |c/c_lin - 1| (all modes; |n| <= 4; |n| > 4),
  largest shell |P/P_lin - 1| over shells of more than ten independent modes and over shells of
  more than ten modes counted in both hemispheres, with the |n|^2 where it falls,
  the largest 1 - W, <alpha> - 1 and the rms of the per-mode differences B-A and C-A over |c_lin|.
Output: OUT/reader_split.json, OUT/fig_reader_split.{png,pdf}.
Usage: reader_split.py OUT
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figlib as fl  # noqa: E402
import figstyle as fs  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

S = fl.SCRATCH
DUMPS = {128: f"{S}/E-20261123-020704-2b99463/C128S/sr.sf.00017",
         256: f"{S}/E-20261124-130952-4be980b/sr.sf.00017"}
SEED = 20261115            # rng_seed of both decks (C128S sr_paper.athinput:21, CL256S input.athinput:21)
VARS = ["chi", "phi", "K", "alpha", "Pi", "gxx", "gxy", "gxz", "gyy", "gyz", "gzz"]
PAIRS = [("gxx", 0, 0, 1.0), ("gyy", 1, 1, 1.0), ("gzz", 2, 2, 1.0),
         ("gxy", 0, 1, 2.0), ("gxz", 0, 2, 2.0), ("gyz", 1, 2, 2.0)]


def coeff(modes, a, workers=2):
    """modes.coeff with a fixed number of FFT threads (ladder_lib uses 8)."""
    from scipy import fft
    F = fft.rfftn(a, workers=workers)
    return F[modes.iz, modes.iy, modes.ix] * modes.shift / modes.N ** 3


def readers(f, modes):
    chi_m, K_m, a_m, Pi_m = (float(f[v].mean()) for v in ("chi", "K", "alpha", "Pi"))
    c_chi = coeff(modes, f["chi"]) / (2.0 * chi_m)
    c_lnchi = coeff(modes, np.log(f["chi"])) / 2.0
    c_phi = coeff(modes, f["phi"])
    nh = modes.nhat
    aniso = np.zeros(modes.M, dtype=complex)
    for name, i, j, w in PAIRS:
        aniso += w * nh[:, i] * nh[:, j] * coeff(modes, f[name])
    aniso *= 0.25
    hA, hB = -K_m / (3.0 * a_m), -K_m / 3.0
    r = {"A": c_chi + (hA / Pi_m) * c_phi + aniso,
         "B": c_chi + (hB / Pi_m) * c_phi + aniso,
         "C": c_lnchi + (hA / Pi_m) * c_phi + aniso,
         "D": c_lnchi + (hB / Pi_m) * c_phi + aniso}
    return r, dict(mean_alpha_minus_1=a_m - 1.0, mean_chi=chi_m, H_b=hA, Pi_b=Pi_m)


def stats(c, lin, modes):
    rel = np.abs(c / lin - 1.0)
    n2 = modes.n2
    sn = modes.shell_of
    pnr = np.bincount(sn, weights=np.abs(c) ** 2)
    plin = np.bincount(sn, weights=np.abs(lin) ** 2)
    cnt = np.bincount(sn)
    dsh = np.abs(pnr / plin - 1.0)
    out = dict(permode_rms=float(np.sqrt(np.mean(rel ** 2))),
               permode_rms_n_le4=float(np.sqrt(np.mean(rel[n2 <= 16] ** 2))),
               permode_rms_n_gt4=float(np.sqrt(np.mean(rel[n2 > 16] ** 2))))
    for tag, sel in (("indep_gt10", cnt > 10), ("both_gt10", 2 * cnt > 10)):
        i = int(np.argmax(np.where(sel, dsh, -1.0)))
        out[f"shell_max_{tag}"] = float(dsh[i])
        out[f"shell_max_{tag}_n2"] = int(modes.shell_n2[i])
        out[f"n_shells_{tag}"] = int(sel.sum())
    shell_rms = np.sqrt(np.bincount(sn, weights=rel ** 2) / cnt)
    return out, shell_rms


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    res = {}
    curves = {}
    for N, base in DUMPS.items():
        md = fl.read_modes_file(base + ".modes")
        nmax2 = int(md["n2"].max())
        modes = fl.ll.Modes(N, nmax2)
        h, f = fl.ll.read_dump(base + ".dump", VARS)
        alpha = fl.alpha_modes(modes, SEED)
        idx = np.searchsorted(md["n2"], modes.n2)
        assert np.array_equal(md["n2"][idx], modes.n2)
        W = fl.window(modes.k, md["a"], md["H"])
        lin = fl.L_BOX ** -1.5 * W * md["R"][idx] * alpha
        r, bg = readers(f, modes)
        del f
        e = dict(dump=base + ".dump", time=h["time"], cycle=h["cycle"], nmax2=nmax2, M=int(modes.M),
                 max_1_minus_W=float(np.max(1.0 - W)), **bg)
        for v, c in r.items():
            e[v], curves[(N, v)] = stats(c, lin, modes)
        for v in ("B", "C", "D"):
            d = np.abs(r[v] - r["A"]) / np.abs(lin)
            e[f"rms_{v}_minus_A"] = float(np.sqrt(np.mean(d ** 2)))
        res[N] = e
        res.setdefault("shell_n2", {})[N] = modes.shell_n2.tolist()
    with open(os.path.join(out, "reader_split.json"), "w") as fp:
        json.dump(res, fp, indent=1)
    fs.use_style()
    fig, axes = plt.subplots(1, 2, figsize=(fs.FULL_WIDTH, 3.0), sharey=True)
    fig.subplots_adjust(left=0.09, right=0.99, bottom=0.16, top=0.9, wspace=0.0)
    col = {"A": fs.PAL["blue"], "B": fs.PAL["yellow"], "C": fs.PAL["green"], "D": fs.PAL["red"]}
    lab = {"A": "note's reader", "B": "note's, $H=-\\langle K\\rangle/3$",
           "C": "note's, $\\ln\\chi$", "D": "check's reader"}
    for ax, N in zip(axes, (128, 256)):
        k = np.sqrt(np.array(res["shell_n2"][N], float))
        for v in "ABCD":
            ax.semilogy(k, curves[(N, v)], color=col[v], lw=1.2, label=lab[v])
        ax.set_xlabel(r"$|n|$")
        ax.set_title(f"$N = {N}$", fontsize=10)
    axes[0].set_ylabel(r"rms over a shell of $|\mathcal{R}^{\rm NR}_n/\mathcal{R}^{\rm lin}_n - 1|$")
    axes[0].legend(loc="upper left", fontsize=7)
    fs.save(fig, os.path.join(out, "fig_reader_split"))
    plt.close(fig)
    for N in (128, 256):
        e = res[N]
        print(N, {v: (round(e[v]["permode_rms"], 12), e[v]["shell_max_indep_gt10"],
                      e[v]["shell_max_both_gt10"], e[v]["shell_max_both_gt10_n2"]) for v in "ABCD"},
              "alpha-1", e["mean_alpha_minus_1"], "1-W", e["max_1_minus_W"])


if __name__ == "__main__":
    main()
