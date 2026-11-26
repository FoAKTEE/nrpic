"""Design of the shearing-dust amplitude without stream crossing (decision 0046 item 2a).

From the exact initial slice (shear_ref.initial_data, draft.tex:177-182 and 515) at
H L = 4 this computes, per amplitude beta (b = beta (HL)^2):
  - the contrast of the active mass density rho_ADM + S (S = rho0 u_x u^x, flat slice)
    and the amplitude delta_amp of its cos(4 pi y / L) Fourier mode (the only mode: the
    data depend on c^2 and s^2);
  - the scale factor a_x of the first stream crossing in the plane-parallel Newtonian
    (Zel'dovich) estimate of an Einstein-de Sitter background with the contrast carried
    by the particle masses and no initial velocity along y: total contrast
    delta(a) = delta_amp D(a), D(a) = 3/5 a + 2/5 a^(-3/2) (a = 1 at the start), the
    displacement gradient delta_amp (D(a) - 1), crossing where it reaches 1;
  - the code time t_x = 2 (sqrt(a_x) - 1) of that crossing (a = (1 + t/2)^2).
The estimate is calibrated against L2 (beta = 0.5), whose observer metric shows its first
kink at t = 3.1 (shear/JOURNAL.md, 2026-11-24 07:00 entry). It is a design estimate
[JUDGEMENT]; the runs check for crossings directly (scripts/crossing.py).

    python3 nocross_design.py [--out DIR]
writes nocross_design.json and nocross_design.png into DIR ($NRPIC_RUN_DIR by default).
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shear_ref as sr  # noqa: E402


def growth(a):
    return 0.6*a + 0.4*a**-1.5


def crossing_a(damp):
    """Smallest a >= 1 with damp (D(a) - 1) = 1 (D grows monotonically for a >= 1)."""
    if damp <= 0.0:
        return np.inf
    target = 1.0 + 1.0/damp
    lo, hi = 1.0, 2.0
    while growth(hi) < target:
        hi *= 2.0
        if hi > 1e12:
            return np.inf
    for _ in range(200):
        mid = 0.5*(lo + hi)
        if growth(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5*(lo + hi)


def mode_amp(y, f, L):
    """Amplitude of the cos(4 pi y/L) mode of f/mean(f) - 1."""
    d = f/np.mean(f) - 1.0
    return 2.0*np.abs(np.mean(d*np.cos(4.0*np.pi*y/L)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--HL", type=float, default=4.0)
    ap.add_argument("--out", default=os.environ.get("NRPIC_RUN_DIR", "."))
    a = ap.parse_args()
    L = a.HL
    y = -0.5*L + (np.arange(4096) + 0.5)*L/4096
    betas = np.array([0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.25, 0.3, 0.4, 0.5])
    rows = []
    for beta in betas:
        b = beta*L**2
        d = sr.initial_data(y, b, L)
        S = d["rho0"]*d["ux"]**2
        act = d["rho_adm"] + S
        row = {"beta": float(beta), "b": float(b),
               "W_max": float(d["W"].max()),
               "damp_rho_adm": mode_amp(y, d["rho_adm"], L),
               "damp_active": mode_amp(y, act, L),
               "damp_D": mode_amp(y, d["D"], L)}
        for k in ("rho_adm", "active"):
            ax = crossing_a(row["damp_" + k])
            row["a_x_" + k] = float(ax)
            row["t_x_" + k] = float(2.0*(np.sqrt(ax) - 1.0)) if np.isfinite(ax) else None
        rows.append(row)
    out = {"HL": L, "rows": rows,
           "note": "Zel'dovich EdS estimate, contrast in the masses, no initial y velocity; "
                   "calibrate with L2's first kink at t = 3.1 (a = 6.5)"}
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "nocross_design.json"), "w") as f:
        json.dump(out, f, indent=1)
    for r in rows:
        print("beta %.3f  W_max %.3f  damp(rho_adm) %.4f  damp(active) %.4f  "
              "a_x %.3g / %.3g  t_x %s / %s" % (
                  r["beta"], r["W_max"], r["damp_rho_adm"], r["damp_active"],
                  r["a_x_rho_adm"], r["a_x_active"], r["t_x_rho_adm"], r["t_x_active"]))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import figstyle
    figstyle.apply() if hasattr(figstyle, "apply") else None
    fig, ax = plt.subplots(figsize=(3.4, 2.6))
    bb = [r["beta"] for r in rows]
    for k, lab, ls in (("rho_adm", r"$\rho_{\rm ADM}$", "-"), ("active", r"$\rho_{\rm ADM}+S$", "--")):
        tx = [r["t_x_" + k] if r["t_x_" + k] is not None else np.nan for r in rows]
        ax.semilogy(bb, tx, ls, marker="o", ms=3, label="crossing, " + lab)
    ax.axhline(3.1, color="0.5", lw=0.8, ls=":", label="L2 first kink (t = 3.1)")
    ax.axhline(10.0, color="k", lw=0.8, ls="-.", label="run end tlim = 10")
    ax.set_xlabel(r"amplitude $\beta = b/(H_*L)^2$")
    ax.set_ylabel(r"code time $t_\times$ of first crossing")
    ax.set_title(r"Zel'dovich estimate, $H_*L = %g$" % L, fontsize=8)
    ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(a.out, "nocross_design.png"), dpi=200)


if __name__ == "__main__":
    main()
