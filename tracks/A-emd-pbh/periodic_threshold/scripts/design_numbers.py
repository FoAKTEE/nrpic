"""Design numbers of the single-peak set-up in a periodic box (JOURNAL.md, P0).

    python3 design_numbers.py --out DIR

Units of cosmo/README.md: G = c = 1, H_i = 1 at a_i = 1, matter era: H = a^(-3/2),
a H = a^(-1/2), cosmic time t = (2/3) a^(3/2), conformal time tau = 2 (sqrt(a) - 1).
Peak of arXiv:2609.14218 (MDPBH.tex:839): zeta = 2 ln Psi = mu exp(-k^2 r^2/6) [1 + ...];
k/(a_i H_i) = eps_i fixes the start. Zel'dovich eigenvalues (MDPBH.tex:907-908):
lambda_j = (2 mu/15) (k/aH)^2 (1+3e+p, 1-2p, 1-3e+p); an axis collapses when lambda_j = 1.
Horizon entry (MDPBH.tex:709-719): (k/aH)^2 = 6. Top-hat collapse of the compaction shell:
mean linear contrast in r_m at entry deltabar_ent = (12/(5 e_E)) mu (SCOPE.md section 3),
growing as a; collapse when it reaches 1.686 (3/20 (12 pi)^(2/3)) [BACKGROUND].
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figstyle as fs  # noqa: E402

DC = 0.15*(12.0*np.pi)**(2.0/3.0)     # 1.6865, linear contrast at top-hat collapse
EUL = np.e


def scale_factor_at(kx2, k):
    """a at which (k/aH)^2 = kx2 (a_i = H_i = 1): (k/aH)^2 = k^2 a."""
    return kx2/k**2


def times(a, aH_entry):
    """t/t_H, cosmic and conformal time at scale factor a."""
    return (a/aH_entry)**1.5, (2.0/3.0)*a**1.5, 2.0*(np.sqrt(a) - 1.0)


def za_axes(mu, e, p, k):
    """Scale factors at which the three Zel'dovich axes collapse (inf if never)."""
    f = np.array([1 + 3*e + p, 1 - 2*p, 1 - 3*e + p])
    with np.errstate(divide="ignore"):
        a = np.where(f > 0, 15.0/(2.0*mu*k**2*f), np.inf)
    return a


def tophat_a(mu, k):
    """Scale factor of top-hat collapse of the compaction shell."""
    a_H = 6.0/k**2
    dbar_ent = 12.0/(5.0*EUL)*mu
    return a_H*DC/dbar_ent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    res = {}

    # 1. the paper's start, k/(a_i H_i) = 1/5
    k = 0.2
    a_H = scale_factor_at(6.0, k)
    t_i = 2.0/3.0
    t_H = (2.0/3.0)*a_H**1.5
    res["paper_start"] = {
        "k": k, "a_H_over_a_i": a_H, "t_H_over_t_i": t_H/t_i,
        "expected_750sqrt6": 750*np.sqrt(6.0),
        "box_side_comoving": 20.0/k, "r_m": np.sqrt(6.0)/k,
        "box_in_hubble_radii_at_start": 20.0/k*1.0,
        "box_in_hubble_radii_at_entry": 20.0/k*a_H**-0.5,
        "box_in_hubble_radii_at_250tH": 20.0/k*(a_H*250**(2/3))**-0.5,
        "tau_entry": 2*(np.sqrt(a_H) - 1),
    }
    # 2. mu whose top-hat collapse time is 250 t_H, and 1000 t_H
    res["mu_fd"] = {str(n): float(DC/(12/(5*EUL))/n**(2/3)) for n in (250, 1000)}

    # 3. epochs for the scouting amplitudes and starts
    rows = []
    for eps_i in (0.2, 1.0, np.sqrt(6.0)):
        kk = eps_i
        aH_e = scale_factor_at(6.0, kk)
        for mu in (0.03, 0.05, 0.3, 0.5):
            for e in (0.0, 0.2):
                ax = za_axes(mu, e, 0.0, kk)
                ath = tophat_a(mu, kk)
                row = {"eps_i": eps_i, "mu": mu, "e": e,
                       "a_entry": aH_e,
                       "za_axes_t_over_tH": [float(times(x, aH_e)[0]) for x in ax],
                       "tophat_t_over_tH": float(times(ath, aH_e)[0]),
                       "tau_tophat": float(times(ath, aH_e)[2]),
                       "tau_250tH": float(2*(np.sqrt(aH_e*250**(2/3)) - 1)),
                       "lambda1_at_start": float(2*mu/15*kk**2*(1 + 3*e)),
                       "delta_c_at_start": float(2*mu/5*kk**2),
                       "psiN_centre": -0.6*mu}
                rows.append(row)
    res["epochs"] = rows

    # 4. mass of the compaction region (rho_b a^3 = 3/(8 pi) in these units)
    for eps_i in (0.2, 1.0):
        r_m = np.sqrt(6.0)/eps_i
        res.setdefault("mass_rm", {})[str(eps_i)] = 0.5*r_m**3

    with open(os.path.join(a.out, "design_numbers.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(json.dumps({k_: res[k_] for k_ in ("paper_start", "mu_fd", "mass_rm")},
                     indent=1))
    for r in rows:
        print(f"eps_i={r['eps_i']:.3f} mu={r['mu']:.2f} e={r['e']:.1f}  ZA axes t/tH "
              + " ".join(f"{x:8.2f}" for x in r["za_axes_t_over_tH"])
              + f"  tophat {r['tophat_t_over_tH']:8.2f} tau {r['tau_tophat']:7.2f}"
              + f"  tau(250tH) {r['tau_250tH']:7.2f} lam1(start) {r['lambda1_at_start']:.4f}")

    # figure: left, box side in Hubble radii against t/t_H; right, collapse epochs
    fs.use_style()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(8, 3.2))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.15, top=0.95, wspace=0.28)
    ax1 = fig.add_subplot(1, 2, 1)
    tt = np.logspace(-3.5, 3, 300)
    nb = 20.0/np.sqrt(6.0)*tt**(-1.0/3.0)     # box*aH = 20/k * k/sqrt6 * (t/tH)^(-1/3)
    ax1.loglog(tt, nb, color=fs.PAL["red"], label="box side 2L = 20/k")
    ax1.loglog(tt, tt**(-1.0/3.0), color=fs.PAL["blue"], ls="--",
               label="compaction radius r_m")
    ax1.axhline(1.0, **fs.GUIDE)
    ax1.axvline(1.0, color="0.5", lw=1.0, alpha=0.4)
    ax1.axvline(250.0, color="0.5", lw=1.0, alpha=0.4)
    ax1.axvline((1/150)**1.5, color="0.5", lw=1.0, alpha=0.4)
    ax1.set_xlabel(r"$t/t_H$")
    ax1.set_ylabel(r"comoving size $\times\, aH$")
    ax1.legend(frameon=False, loc="upper right")
    ax2 = fig.add_subplot(1, 2, 2)
    mus = np.logspace(-2, 0, 200)
    for e, col in ((0.0, fs.PAL["blue"]), (0.2, fs.PAL["red"])):
        th = [times(tophat_a(m, 1.0), 6.0)[0] for m in mus]
        ax2.loglog(mus, th, color=col, label=f"top hat, e = {e}" if e == 0 else None)
        za = np.array([[times(x, 6.0)[0] for x in za_axes(m, e, 0.0, 1.0)] for m in mus])
        ax2.loglog(mus, za[:, 0], color=col, ls="--", label=f"first ZA axis, e = {e}")
        if e > 0:
            ax2.loglog(mus, za[:, 2], color=col, ls=":", label=f"third ZA axis, e = {e}")
    ax2.axhline(250.0, **fs.GUIDE)
    ax2.axvline(0.045, color="0.5", lw=1.0, alpha=0.4)
    ax2.axvline(0.452, color="0.5", lw=1.0, alpha=0.4)
    ax2.set_xlabel(r"$\mu$")
    ax2.set_ylabel(r"$t/t_H$")
    ax2.set_ylim(0.3, 3e4)
    ax2.legend(frameon=False, loc="upper right", fontsize=8)
    fs.save(fig, os.path.join(a.out, "fig_design_numbers"))


if __name__ == "__main__":
    main()
