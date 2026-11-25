"""P1, P2 of JOURNAL entry 1: the integrator, its variational derivatives and the end-surface
map against closed forms.

P1 exponential potential V = V0 exp(-lam phi): attractor y_a = lam/(8 pi); off the attractor
   dy/dN = 3 (1 - 4 pi y^2/3)(y_a - y) separates, phi - y_a N = -G(y) + const with
   G(y) = int dy/(3 - 4 pi y^2) = atanh(sqrt(4 pi/3) y)/sqrt(12 pi); hence
   N_e - N_0 = [phi_e - phi_0 + G(y_e) - G(y_0)]/y_a, y_e from
   int_{y0}^{ye} dy/(3 (1 - 4 pi y^2/3)(y_a - y)) = N_e - N_0 (solved with mpmath, 40 digits).
   Derivatives: N_phi = -1/y_a, N_phiphi = N_phiy = 0, N_y = -G'(y0)/y_a, N_yy = -G''(y0)/y_a
   (plus terms of order exp(-3 Delta N) through y_e, kept in the mpmath reference by finite
   differences at 40 digits).
P2 Hamilton-Jacobi potential, H = H0 exp(beta phi^2/2), attractor y = -beta phi/(4 pi):
   N = (4 pi/beta) ln(phi_0/phi_e); along the attractor dN/dphi0 = 4 pi/(beta phi0),
   d2N/dphi0^2 = -4 pi/(beta phi0^2).

Usage: test_closed.py <outdir>
"""
import json
import os
import sys

import mpmath as mp
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zv_lib as Z  # noqa: E402

mp.mp.dps = 40
LD = Z.LD


def exp_reference(lam, phi0, y0, phi_e):
    lam, phi0, y0, phi_e = map(mp.mpf, (lam, phi0, y0, phi_e))
    ya = lam / (8 * mp.pi)
    G = lambda y: mp.atanh(mp.sqrt(4 * mp.pi / 3) * y) / mp.sqrt(12 * mp.pi)  # noqa: E731

    if y0 == ya:
        return (phi_e - phi0) / ya
    # 3 N(y) = -(A/b) ln(1 - b y) + (B/b) ln(1 + b y) - C ln|y_a - y| (partial fractions of
    # 1/((1 - b y)(1 + b y)(y_a - y)), b^2 = 4 pi/3)
    b = mp.sqrt(4 * mp.pi / 3)
    A = 1 / (2 * (ya - 1 / b))
    B = 1 / (2 * (ya + 1 / b))
    C = 1 / (1 - b * b * ya * ya)
    smooth = lambda y: -(A / b) * mp.log(1 - b * y) + (B / b) * mp.log(1 + b * y)  # noqa: E731
    sg = mp.sign(ya - y0)
    dN = (phi_e - phi0) / ya
    ye = ya
    for _ in range(200):
        u = mp.log(abs(ya - y0)) + (smooth(ye) - smooth(y0) - 3 * dN) / C
        ye = ya - sg * mp.e ** u
        dN_new = (phi_e - phi0 + G(ye) - G(y0)) / ya
        if abs(dN_new - dN) < mp.mpf(10) ** -36:
            dN = dN_new
            break
        dN = dN_new
    else:
        raise RuntimeError("no convergence")
    return dN


def main(out):
    os.makedirs(out, exist_ok=True)
    res = {"P1": [], "P2": {}, "P1_conv": [], "P2_conv": []}
    # ---------------- P1
    lam = 0.709
    pot = Z.Exponential(lam)
    ya = lam / (8 * np.pi)
    phi_e = 12 * ya
    h = 1e-3
    for dlt in (-0.5, -0.2, 0.0, 0.3, 0.5):
        y0 = ya * (1 + dlt)
        Nref = exp_reference(lam, 0.0, y0, phi_e)
        Nnum = Z.efolds_to_surface(pot, LD(0), LD(y0), LD(phi_e), h)
        N, Na, Nab, _ = Z.map_derivatives(pot, LD(0), LD(y0), LD(phi_e), h)
        G1 = 1 / (3 - 4 * mp.pi * mp.mpf(y0) ** 2)
        G2 = 8 * mp.pi * mp.mpf(y0) / (3 - 4 * mp.pi * mp.mpf(y0) ** 2) ** 2
        ya_m = mp.mpf(lam) / (8 * mp.pi)
        # 40-digit finite differences of the reference in y0 (keep the y_e terms)
        e = mp.mpf(10) ** -8
        Np = exp_reference(lam, 0.0, mp.mpf(y0) + e, phi_e)
        Nm = exp_reference(lam, 0.0, mp.mpf(y0) - e, phi_e)
        Ny_ref = (Np - Nm) / (2 * e)
        Nyy_ref = (Np + Nm - 2 * Nref) / e ** 2
        row = dict(delta=dlt, y0=float(y0), N_ref=float(Nref),
                   err_N_map=float(mp.mpf(str(Nnum)) - Nref),
                   err_N_var=float(mp.mpf(str(N)) - Nref),
                   Nphi=float(Na[0]), Nphi_ref=float(-1 / ya_m),
                   Nphiphi=float(Nab[0, 0]), Nphiy=float(Nab[0, 1]),
                   Ny=float(Na[1]), Ny_closed=float(-G1 / ya_m), Ny_ref=float(Ny_ref),
                   Nyy=float(Nab[1, 1]), Nyy_closed=float(-G2 / ya_m), Nyy_ref=float(Nyy_ref))
        row["rel_Ny"] = row["Ny"] / row["Ny_ref"] - 1
        row["rel_Nyy"] = row["Nyy"] / row["Nyy_ref"] - 1
        row["rel_Nphi"] = row["Nphi"] / row["Nphi_ref"] - 1
        res["P1"].append(row)
        print("P1", {k: (f"{v:.3e}" if isinstance(v, float) else v) for k, v in row.items()})
    # convergence in the step, off the attractor
    y0 = ya * 1.3
    Nref = exp_reference(lam, 0.0, y0, phi_e)
    for hh in (4e-2, 2e-2, 1e-2, 5e-3, 2.5e-3, 1e-3):
        Nn = Z.efolds_to_surface(pot, LD(0), LD(y0), LD(phi_e), hh)
        res["P1_conv"].append(dict(h=hh, err=float(abs(mp.mpf(str(Nn)) - Nref))))
    # ---------------- P2
    beta = 0.5
    pot2 = Z.HamiltonJacobi(beta)
    phi0, phi_e2 = 3.0, 1.0
    y_att = lambda p: -beta * LD(p) / (4 * Z.PI_LD)  # noqa: E731
    Nref2 = 4 * mp.pi / beta * mp.log(mp.mpf(phi0) / phi_e2)
    N2, Na2, Nab2, _ = Z.map_derivatives(pot2, LD(phi0), y_att(phi0), LD(phi_e2), h)
    s = -beta / (4 * Z.PI_LD)
    d1 = Na2[0] + s * Na2[1]
    d2 = Nab2[0, 0] + 2 * s * Nab2[0, 1] + s * s * Nab2[1, 1]
    d1_ref = 4 * mp.pi / (beta * phi0)
    d2_ref = -4 * mp.pi / (beta * phi0 ** 2)
    res["P2"] = dict(N=float(N2), N_ref=float(Nref2), err_N=float(mp.mpf(str(N2)) - Nref2),
                     d1=float(d1), d1_ref=float(d1_ref), rel_d1=float(mp.mpf(str(d1)) / d1_ref - 1),
                     d2=float(d2), d2_ref=float(d2_ref), rel_d2=float(mp.mpf(str(d2)) / d2_ref - 1))
    print("P2", res["P2"])
    for hh in (4e-2, 2e-2, 1e-2, 5e-3, 2.5e-3, 1e-3):
        Nn = Z.efolds_to_surface(pot2, LD(phi0), y_att(phi0), LD(phi_e2), hh)
        res["P2_conv"].append(dict(h=hh, err=float(abs(mp.mpf(str(Nn)) - Nref2))))
    with open(os.path.join(out, "closed_form.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    # ---------------- figure
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..",
                                    "..", "..", "python"))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from nrpic import figstyle as fs
    fs.use_style()
    fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.8))
    ax = axs[0]
    for key, lab, c in (("P1_conv", "exponential, $y_0=1.3\\,y_a$", fs.PAL["blue"]),
                        ("P2_conv", "Hamilton-Jacobi attractor", fs.PAL["red"])):
        hs = np.array([r["h"] for r in res[key]])
        es = np.array([max(r["err"], 1e-19) for r in res[key]])
        ax.loglog(hs, es, "o-", color=c, label=lab)
    hs = np.array([4e-2, 1e-3])
    ax.loglog(hs, 1e-6 * (hs / 4e-2) ** 4, "k--", lw=0.8, label="$\\propto h^4$")
    ax.set_xlabel("step $h$ in $N$")
    ax.set_ylabel("$|N - N_{\\rm exact}|$")
    ax.legend(fontsize=7)
    ax = axs[1]
    d = np.array([r["delta"] for r in res["P1"]])
    for key, lab, c, m in (("rel_Ny", "$N_y$", fs.PAL["blue"], "o"),
                           ("rel_Nyy", "$N_{yy}$", fs.PAL["red"], "s"),
                           ("rel_Nphi", "$N_\\phi$", fs.PAL["green"], "^")):
        v = np.array([abs(r[key]) for r in res["P1"]])
        ax.semilogy(d, np.maximum(v, 1e-19), m, color=c, label=lab)
    ax.axhline(1e-8, color="k", ls=":", lw=0.8)
    ax.set_xlabel("$y_0/y_a - 1$")
    ax.set_ylabel("relative error ($h=10^{-3}$)")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fs.save(fig, os.path.join(out, "fig_closed_form"))


if __name__ == "__main__":
    main(sys.argv[1])
