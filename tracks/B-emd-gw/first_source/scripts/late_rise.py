#!/usr/bin/env python3
"""P7 and P7b of JOURNAL.md: is the late rise of the flat TT part in the full-GR cosmology
dumps the second-order spatial-gauge piece?

    python3 late_rise.py <run dir> [<run dir> ...]       (output: $NRPIC_RUN_DIR)

For every restart dump of each run (`<run dir>/rst/*.rst`): a = <chi>^(-1/2),
H = -<trK>/3, rho_bar = 3 H^2/(8 pi); the rms of Lambda h, of the traceless non-TT part, of
the spatial-gauge piece G and of Lambda h - G; rho_kin = <(2 Lambda A)^2>/(64 pi) from Lambda A
and from Lambda A - G_A; rho_grad from Lambda h and from Lambda h - G (chi_bar k^2 |h|^2/(64 pi));
shell spectra of the mean squares. Writes late_rise.json and late_rise.{png,pdf}.
Dumps are processed in parallel (NWORK processes, default 3).
"""
import glob
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fslib"))
import paths  # noqa: E402,F401
from gwdiag import tt, readers  # noqa: E402
from fslib import gauge  # noqa: E402

FOURPI = 4 * np.pi


def ms(F, g):
    P = tt.power_tensor(F, g).copy()
    P[0, 0, 0] = 0.0
    return P


def one(path):
    d = readers.read_rst(path)
    g = d["grid"]
    chi, gt, At, trK, alpha, beta = readers.z4c_tensors(d)
    del d
    a = float(np.mean(chi)) ** -0.5
    H = -float(np.mean(trK)) / 3.0
    chib = float(np.mean(chi))
    h = gauge.traceless(gt - np.eye(3)[:, :, None, None, None])
    At = gauge.traceless(At)
    kh = tt._khat(g)[2]
    kk2 = (g.kvec(real=True) ** 2).sum(axis=0)
    nyq = g.nyquist_mask(real=True)

    def proj(F):
        T = tt.lambda_apply(F, kh)
        T[:, :, 0, 0, 0] = 0.0
        T[:, :, nyq] = 0.0
        return T
    Fh = tt.tensor_rfft(h)
    Th = proj(Fh)
    FA = tt.tensor_rfft(At)
    TA = proj(FA)
    del FA
    G, parts = gauge.gauge_piece(h, g, return_parts=True)
    Gh = parts["G_hat"]
    del G, parts
    Ax = h - gauge.nonTT_traceless(h, g)               # TT + homogeneous traceless part
    Gth = Gh + tt.tensor_rfft(gauge.gauge_piece_A(h, Ax, g))
    del Ax
    GA = gauge.gauge_piece_A(h, At, g)
    GAh = tt.tensor_rfft(GA)
    del GA
    P = {"TT": ms(Th, g), "nonTT": ms(Fh - Th, g), "G": ms(Gh, g), "TT_minus_G": ms(Th - Gh, g),
         "Gtot": ms(Gth, g), "TT_minus_Gtot": ms(Th - Gth, g),
         "A_TT": ms(TA, g), "GA": ms(GAh, g), "A_TT_minus_GA": ms(TA - GAh, g)}
    kc, _, cnt, dk = tt._shell_sum(P["TT"], g)
    spec = {key: tt._shell_sum(v, g)[1].tolist() for key, v in P.items()}
    rho_bar = 3 * H * H / (8 * np.pi)
    c_kin = 4.0 / (16 * FOURPI)                       # (d_tau h)^2 = 4 (Lambda A)^2
    c_grad = chib / (16 * FOURPI)
    row = {"file": os.path.basename(path), "a": a, "H": H, "rho_bar": rho_bar,
           "rms_TT": float(np.sqrt(P["TT"].sum())), "rms_nonTT": float(np.sqrt(P["nonTT"].sum())),
           "rms_G": float(np.sqrt(P["G"].sum())), "rms_TT_minus_G": float(np.sqrt(P["TT_minus_G"].sum())),
           "rms_Gtot": float(np.sqrt(P["Gtot"].sum())), "rms_TT_minus_Gtot": float(np.sqrt(P["TT_minus_Gtot"].sum())),
           "k0_traceless_norm": float(np.sqrt((h.mean(axis=(-3, -2, -1)) ** 2).sum())),
           "rms_A_TT": float(np.sqrt(P["A_TT"].sum())), "rms_GA": float(np.sqrt(P["GA"].sum())),
           "rms_A_TT_minus_GA": float(np.sqrt(P["A_TT_minus_GA"].sum())),
           "rho_kin": c_kin * float(P["A_TT"].sum()), "rho_kin_corrected": c_kin * float(P["A_TT_minus_GA"].sum()),
           "rho_grad": c_grad * float((kk2 * P["TT"]).sum()),
           "rho_grad_corrected": c_grad * float((kk2 * P["TT_minus_G"]).sum()),
           "spectra": spec, "k": kc.tolist(), "counts": cnt.tolist(), "L": g.L[0], "n": g.n[0]}
    print(f"{path}: a = {a:.1f}, rms TT {row['rms_TT']:.3e}, G {row['rms_G']:.3e}, "
          f"TT-G {row['rms_TT_minus_G']:.3e}, Gtot {row['rms_Gtot']:.3e}, TT-Gtot {row['rms_TT_minus_Gtot']:.3e}, "
          f"nonTT {row['rms_nonTT']:.3e}, h0 {row['k0_traceless_norm']:.3e}", flush=True)
    return row


def main():
    out = os.environ.get("NRPIC_RUN_DIR", ".")
    runs = sys.argv[1:]
    res = {"runs": {}}
    nw = int(os.environ.get("NWORK", "3"))
    for rd in runs:
        files = sorted(glob.glob(os.path.join(rd, "rst", "*.rst")))
        with Pool(nw) as pool:
            rows = pool.map(one, files)
        res["runs"][os.path.basename(rd.rstrip("/"))] = rows
    with open(os.path.join(out, "late_rise.json"), "w") as f:
        json.dump(res, f)
    plot(res, out)


def plot(res, out):
    from nrpic import figstyle as fs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(fs.FULL_WIDTH * 1.25, 3.4))
    cols = [fs.PAL["red"], fs.PAL["blue"]]
    for c, (name, rows) in zip(cols, res["runs"].items()):
        a = np.array([r["a"] for r in rows])
        lab = "quadratic" if name.endswith("_t") else "cubic"
        m = a > 1.5
        ax[0].loglog(a[m], [r["rms_TT"] for r in rows if r["a"] > 1.5], "o-", color=c, ms=3,
                     label=r"$\Lambda h$ (%s)" % lab)
        ax[0].loglog(a[m], [r["rms_TT_minus_G"] for r in rows if r["a"] > 1.5], "^--", color=c, ms=4,
                     label=r"$\Lambda h-G$")
        ax[0].loglog(a[m], [r["rms_G"] for r in rows if r["a"] > 1.5], ":", color=c, lw=1.5,
                     label=r"$G$")
        if "rms_Gtot" in rows[-1]:
            ax[0].loglog(a[m], [r["rms_Gtot"] for r in rows if r["a"] > 1.5], "-.", color=c, lw=1.0,
                         label=r"$G_{\rm tot}$")
        nt = np.array([r["rms_nonTT"] for r in rows if r["a"] > 1.5])
        ax[0].loglog(a[m], nt ** 2, color="grey", lw=1, alpha=0.6,
                     label=r"(rms non-TT)$^2$" if c == cols[0] else None)
        rb = np.array([r["rho_bar"] for r in rows if r["a"] > 1.5])
        ax[1].loglog(a[m], np.array([r["rho_kin"] for r in rows if r["a"] > 1.5]) / rb, "o-", color=c, ms=3,
                     label=r"$\rho_{\rm kin}$, $\Lambda\tilde A$ (%s)" % lab)
        ax[1].loglog(a[m], np.array([r["rho_kin_corrected"] for r in rows if r["a"] > 1.5]) / rb, "^--",
                     color=c, ms=4, label=r"$\rho_{\rm kin}$, $\Lambda\tilde A-G_A$")
        ax[1].loglog(a[m], np.array([r["rho_grad"] for r in rows if r["a"] > 1.5]) / rb, "s-", color=c, ms=3,
                     alpha=0.5, label=r"$\rho_{\rm grad}$, $\Lambda h$")
        ax[1].loglog(a[m], np.array([r["rho_grad_corrected"] for r in rows if r["a"] > 1.5]) / rb, "v:",
                     color=c, ms=4, alpha=0.7, label=r"$\rho_{\rm grad}$, $\Lambda h-G$")
        last = rows[-1]
        k = np.array(last["k"]) * last["L"] / (2 * np.pi)
        sel = np.array(last["counts"]) > 0
        for key, ls, lb in (("TT", "-", r"$\Lambda h$"), ("G", ":", r"$G$"), ("TT_minus_G", "--", r"$\Lambda h-G$")):
            ax[2].loglog(k[sel][1:], np.array(last["spectra"][key])[sel][1:], ls=ls, color=c,
                         label=lb + " (%s, a = %.0f)" % (lab, last["a"]))
    ax[0].set_xlabel(r"$a$")
    ax[0].set_ylabel("rms over the box")
    ax[0].legend(fontsize=6.5, loc="upper left", ncol=2)
    ax[1].set_xlabel(r"$a$")
    ax[1].set_ylabel(r"$\rho/\bar\rho$")
    ax[1].legend(fontsize=6.5, loc="upper left")
    ax[2].set_xlabel(r"$|k|L/2\pi$")
    ax[2].set_ylabel("mean square per shell, last dump")
    ax[2].legend(fontsize=6.5, loc="lower left")
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "late_rise"))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--plot":
        r = json.load(open(sys.argv[2]))
        plot(r, os.path.dirname(sys.argv[2]))
    else:
        main()
