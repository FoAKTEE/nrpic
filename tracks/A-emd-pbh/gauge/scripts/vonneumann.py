"""T2 of tracks/A-emd-pbh/gauge/JOURNAL.md: largest stable Courant number of gauge modes
under the discretization of the production inputs (von Neumann, frozen coefficients,
flat conformal metric).

    python3 -I vonneumann.py --out OUTDIR [--n 49]

Discretization read from the code:
  athenak/src/utils/finite_diff.hpp, NGHOST = 4: first derivative
      (3/4, -3/20, 1/60) antisymmetric, symbol i s1, s1 = 2 [3/4 sin t - 3/20 sin 2t
      + 1/60 sin 3t]; second derivative (-49/18, 3/2, -3/20, 1/90), symbol -s2,
      s2 = 49/18 - 3 cos t + (3/10) cos 2t - (1/45) cos 3t; mixed derivative Dxy =
      product of two first-derivative stencils, symbol -s1_a s1_b.
  Kreiss-Oliger: z4c.cpp:168 diss = opt.diss 2^(-2 ng) (-1)^(ng even), added as
      Diss(a) idx[a] in z4c_calcrhs.cpp:763-773 with the eighth-difference stencil
      (1,-8,28,-56,70,...): symbol -opt.diss sum_a sin^8(t_a/2) / dx.
  Integrator rk4 (problems/*/*.athinput): G(z) = 1 + z + z^2/2 + z^3/6 + z^4/24.
Modes:
  scalar   d_t^2 u = v^2 Lap u  (lapse mode, light):  lambda = +- i v sqrt(sum s2)
  shift    d_t beta^i = b Gamma^i, d_t Gamma^i = Lap beta^i + (1/3) d^i d_j beta^j:
           lambda = +- i sqrt(b mu), mu eigenvalues of M = (sum s2) I + N/3,
           N_aa = s2_a, N_ab = s1_a s1_b; longitudinal speed sqrt(4b/3)
Both get the dissipation on every variable. Output: OUTDIR/vonneumann.json and the
figure OUTDIR/vonneumann.{png,pdf}.
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


def s1(t):
    return 2.0 * (0.75 * np.sin(t) - 0.15 * np.sin(2 * t) + np.sin(3 * t) / 60.0)


def s2(t):
    return 49.0 / 18.0 - 3.0 * np.cos(t) + 0.3 * np.cos(2 * t) - np.cos(3 * t) / 45.0


def rk4_G(z):
    return 1 + z + z ** 2 / 2 + z ** 3 / 6 + z ** 4 / 24


def grid(n):
    t = np.linspace(0.0, np.pi, n)
    T1, T2, T3 = np.meshgrid(t, t, t, indexing="ij")
    return T1.ravel(), T2.ravel(), T3.ravel()


def spectra(n):
    t1, t2, t3 = grid(n)
    S2 = np.stack([s2(t1), s2(t2), s2(t3)], axis=1)
    S1 = np.stack([s1(t1), s1(t2), s1(t3)], axis=1)
    lap = S2.sum(axis=1)
    N = np.einsum("pa,pb->pab", S1, S1)
    for a in range(3):
        N[:, a, a] = S2[:, a]
    M = lap[:, None, None] * np.eye(3)[None] + N / 3.0
    mu = np.linalg.eigvalsh(M)  # (p, 3), ascending
    ko = (np.sin(t1 / 2) ** 8 + np.sin(t2 / 2) ** 8 + np.sin(t3 / 2) ** 8)
    return lap, mu, ko


def max_amp(C, omega, ko, diss):
    """Largest |G| over the modes for Courant number C: z = C (-diss ko +- i omega)."""
    z = C * (-diss * ko + 1j * omega)
    return np.abs(rk4_G(z)).max()


def c_crit(omega, ko, diss, tol=1e-6):
    lo, hi = 1e-4, 5.0
    if max_amp(lo, omega, ko, diss) > 1 + 1e-12:
        return 0.0
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        if max_amp(mid, omega, ko, diss) <= 1 + 1e-12:
            lo = mid
        else:
            hi = mid
    return lo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=49)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    lap, mu, ko = spectra(args.n)
    out = {"n_per_dim": args.n, "max_sqrt_lap": float(np.sqrt(lap.max())),
           "max_sqrt_mu_shift": float(np.sqrt(mu.max())),
           "rk4_imag_axis_limit": float(2 * np.sqrt(2)), "cases": {}}
    print(f"largest sqrt(sum s2) = {np.sqrt(lap.max()):.4f} (dx = 1), largest sqrt(mu) "
          f"of the shift operator = {np.sqrt(mu.max()):.4f}")
    # scalar wave of speed 1, shift subsystem with b = 3/4 (longitudinal speed 1)
    cases = {"scalar_v1": np.sqrt(lap), "shift_b0.75": np.sqrt(0.75 * mu.max(axis=1))}
    for name, om in cases.items():
        for diss in (0.0, 0.5, 1.0):
            cc = c_crit(om, ko, diss)
            out["cases"][f"{name}_diss{diss}"] = cc
            print(f"{name:12s} diss = {diss:3.1f}: largest stable C v = {cc:.4f}")
    # implications for the runs: conformal-time lapse alpha = a, shift_alpha2Gamma = 0.75
    C = 0.25
    cc = out["cases"]["shift_b0.75_diss0.5"]
    a_crit = cc / C
    t_crit = 2.0 * (np.sqrt(a_crit) - 1.0)
    out["bh2"] = {"cfl_number": C, "a_crit": a_crit, "t_crit": t_crit,
                  "note": "speed alpha = a of the alpha^2-scaled driver in conformal time"}
    print(f"shift_alpha2Gamma = 0.75, alpha = a, cfl 0.25: a_crit = {a_crit:.3f}, "
          f"t_crit = {t_crit:.3f} (a = (1 + t/2)^2)")
    # growth factor per step against a, for T3
    a_s = np.linspace(1.0, 6.0, 251)
    om = cases["shift_b0.75"]
    gmax = np.array([max_amp(C * a, om, ko, 0.5) for a in a_s])
    out["growth_per_step"] = {"a": a_s.tolist(), "Gmax": gmax.tolist()}
    with open(os.path.join(args.out, "vonneumann.json"), "w") as f:
        json.dump(out, f, indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    use_style()
    fig, axs = plt.subplots(1, 2, figsize=(FULL_WIDTH, 3.2))
    fig.subplots_adjust(left=0.08, right=0.985, bottom=0.15, top=0.95, wspace=0.28)
    ax = axs[0]
    Cs = np.linspace(0.05, 1.2, 231)
    for (name, om), col in zip(cases.items(), (SERIES[0], SERIES[1])):
        for diss, lst in ((0.0, "--"), (0.5, "-")):
            g = [max_amp(c, om, ko, diss) for c in Cs]
            ax.plot(Cs, np.array(g) - 1.0, color=col, ls=lst,
                    label=f"{name}, diss {diss}")
    ax.axhline(0.0, **MASK_LINE)
    ax.set_yscale("symlog", linthresh=1e-6)
    ax.set_xlabel(r"Courant number times speed, $C\,v$")
    ax.set_ylabel(r"$\max|G| - 1$ per RK4 step")
    ax.legend(fontsize=8, loc="upper left")
    ax = axs[1]
    ax.plot(a_s, gmax - 1.0, color=SERIES[1])
    ax.axvline(a_crit, **GUIDE)
    ax.set_yscale("symlog", linthresh=1e-6)
    ax.set_xlabel(r"background scale factor $a$ (lapse $\alpha = a$)")
    ax.set_ylabel(r"$\max|G| - 1$, shift mode, $C=0.25$")
    for ext in ("png", "pdf"):
        fig.savefig(os.path.join(args.out, f"vonneumann.{ext}"))
    print("wrote", os.path.join(args.out, "vonneumann.png"))


if __name__ == "__main__":
    main()
